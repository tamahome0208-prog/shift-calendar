# シフトカレンダー v6: 修正+俯瞰&思い出機能 設計

**日付**: 2026-05-24
**ターゲット**: https://tamahome0208-prog.github.io/shift-calendar/
**スコープ**: 既存課題の修正 + カップル文脈強化機能の追加
**コミット計画**: 5コミット、各150行以内、合計 ~525行

---

## 0. 前提と非スコープ

### 既存アーキテクチャ(変更なし)

- 単一HTML/CSS/JS(`build.py` がHTMLテンプレを生成)
- Firebase Firestore + Anonymous Auth(`events` コレクション)
- GitHub Pages 自動デプロイ
- ケロッピーテーマ・Calm Canvas デザイン(v5)

### 非スコープ(YAGNI で削除)

- View Transitions API: ブラウザ対応&Safari制限が不安定
- Pull-to-refresh: PWAでの標準サポート薄
- 長押しメニュー: 既存タップ操作で代替可能、UI複雑化
- A番黄色の色再調整: 主観的、現状機能している
- ダブルタップハート送信: 機能としてふわっとしすぎ

---

## 1. 修正系 (Phase A)

### A-1. 祝日多年対応

**現状の問題**: `HOLIDAYS_2026` のみで2025/2027以降の他月セル(月跨ぎ表示)で祝日色が出ない。

**設計**:
- Python側 `HOLIDAYS_2026` を `HOLIDAYS_BY_YEAR` 辞書へ
- 2025・2026・2027・2028の主要祝日を内蔵
- JS側 `HOLIDAYS` 配列を `HOLIDAYS_BY_YEAR` オブジェクトへ
- 判定: `(HOLIDAYS_BY_YEAR[y] || []).includes(key)` で参照

**ファイル**: `build.py`(末尾の HOLIDAYS_2026 と render 内 HOLIDAYS.includes)
**推定差分**: +30行
**確認**: 2025年12月→2026年1月跨ぎ表示で 1/1 が赤になる

### A-2. Service Worker キャッシュキー動的化

**現状の問題**: `CACHE = 'shift-cal-v4'` 固定。build.py 更新してもキャッシュ無効化されないリスク。`addAll` に `index.html`/`icon.png` を含まずオフライン不完全。

**設計**:
- `build.py` で `__BUILD_TIMESTAMP__` プレースホルダを生成時に置換
- SW: `const CACHE = 'shift-cal-{ts}';`
- precache: `['./','./index.html','./manifest.json','./icon.png']`
- 既存の activate hook で古いキャッシュ削除は維持

**ファイル**: `build.py`(SW定義 + テンプレ置換ロジック)
**推定差分**: +15行
**確認**: ビルド前後で `sw.js` の `CACHE` が異なる

### A-3. ハプティック振動

**設計**:
- `navigator.vibrate(ms)` を試行(失敗時無視)
- 適用:
  - A番チップタップ: `[20]`(単発短)
  - メモ保存成功: `[15]`
  - 削除確認(キャンセル可能側): `[40,30,40]`
  - 記念日達成日: `[20,40,20,40,20]`(後述、B-1)
- ユーティリティ関数 `haptic(pattern)` を1箇所に集約

**ファイル**: `build.py`(JS関数追加 + 4箇所の呼び出し)
**推定差分**: +30行
**確認**: Android Chrome で振動感じる(iOS は無視されるが副作用なし)

### A-4. confirm() 置換: カスタム確認シート

**現状の問題**: 削除確認だけブラウザ標準 `confirm()`。ケロッピー世界観から浮く。

**設計**:
- 新規 `showConfirm(title, message, onConfirm, danger=false)` 関数
- 既存 `.sheet-overlay`/`.sheet` 構造を再利用、シンプルな確認用 sheet
- 4つの要素: タイトル(太字)・メッセージ(本文)・キャンセル・確定(danger時赤)
- アニメ・glassmorphism は既存のシートと同じ
- 既存の `deleteForm()` 内 `confirm()` 1箇所を置換

**ファイル**: `build.py`(CSS + HTML + JS)
**推定差分**: +80行
**確認**: 「削除」ボタン押下時にケロッピー風シートが出る

---

## 2. カップル文脈強化 (Phase B)

### B-1. 記念日カウントダウン

**目的**: カップルアプリの定着要素として記念日(付き合った日・誕生日・結婚記念日等)を最大3件登録できるようにし、近いものをヒーローカードに表示。

**設計**:
- Firestore コレクション `anniversaries` を新設
  - スキーマ: `{id, name: string, month: 1-12, day: 1-31, type: "anniv"|"birth"|"other"}`
- セキュリティルールに `anniversaries` collection を追加(authで読み書き可)
- 設定シートに「記念日」セクション追加
  - 最大3件まで(UIで強制)
  - 名前・月・日のフォーム
  - 削除可能(各行に×)
- `renderHero()` 拡張:
  - 全記念日について次回到来日を計算
  - 最も近いもの(30日以内)を status 行に: 「あと X 日で○○」
  - 当日なら強調(hot class)
- 記念日当日にはハプティック `[20,40,20,40,20]` 発火(1セッション1回)

**ファイル**: `build.py`(Storage拡張 + CSS + HTML + JS)
**推定差分**: +120行
**確認**: 記念日入力→翌週見ると「あとXX日で○○」がヒーローに出る

### B-2. 1年前の今日(思い出ふりかえり)

**目的**: 過去のメモ・両方休み日を思い出す体験。retention 向上。

**設計**:
- 新規 `Recall` カードをヒーローカード直下に折り畳み式で配置
- 表示条件: 「今日と同じ月日の去年」または「先月同日」に該当イベント/メモがある場合のみ
- 該当無ければカード自体非表示(無音)
- 折り畳み: タイトル「ふりかえり」+ 件数バッジ、タップで開閉
- 表示内容: 過去日付・両方休みフラグ・該当メモ本文の先頭40文字

**ファイル**: `build.py`(CSS + HTML + JS、`renderRecall()` 新規)
**推定差分**: +70行
**確認**: 過去にメモがある日付の同じ月日に来ると Recall が出る

### B-3. 年間ヒートマップビュー

**目的**: 1年通しての両方休みパターン、A番分布、空き周期の俯瞰。

**設計**:
- 既存のフィルターチップ右に「年」アイコンボタン追加
- タップで全画面ボトムシート展開
- 中身: 12行(月)×31列(日)のマトリクス
  - 各セル 10×10px 程度の小さい正方形
  - 色分け:
    - 両方休み: ケロッピーピンク `#FF7AA5`
    - 片方休み(休/有/希望休): 薄いピンク `#FFBED4`
    - A番のいずれか: 黄リング(border)
    - 給料日: 緑ドット
    - イベント無: 白
  - セルタップ → シート閉じる + 該当月にジャンプ + その日のシート開く
- 上部に「2026年」+ 前年/翌年ボタン
- 下部に凡例

**ファイル**: `build.py`(CSS + HTML + JS、`renderYearView()` 新規)
**推定差分**: +180行(単独で 150行を僅かに超える、注意)
**確認**: 年ボタンタップで12×31グリッドが表示され、両方休みがピンクで強調される

---

## 3. データ構造

### Firestore コレクション

```
events/                    # 既存
  {id}: { date, type, title, desc, start, end, reminderMin }
  {id}: { date, type:"memo", stamp, memo }

anniversaries/             # 新規 (B-1)
  {id}: { name, month, day, type }
```

### Firestore セキュリティルール(要更新)

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /events/{document=**} {
      allow read, write: if request.auth != null;
    }
    match /anniversaries/{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

→ Firebase コンソールで指示役が手動更新(私が Claude in Chrome で実施)

### localStorage キー(JS側)

- `shift-cal-custom-v2`: 既存(events のローカルキャッシュ)
- `shift-cal-anniversaries-v1`: 新規(anniversaries のローカルキャッシュ)
- `shift-cal-weather-v1`: 既存
- `shift-cal-fb-config`: 既存
- `shift-cal-celebrated-{key}`: セッションキャッシュ(お祝いアニメ)

---

## 4. コミット計画と差分

| # | 内容 | フェーズ | 推定行数 | 安全余裕 |
|---|---|---|---|---|
| C1 | 祝日多年 + SWキー + ハプティック | A-1, A-2, A-3 | 75 | OK |
| C2 | confirm置換カスタムシート | A-4 | 80 | OK |
| C3 | 記念日カウントダウン | B-1 | 120 | OK |
| C4 | 1年前の今日 | B-2 | 70 | OK |
| C5 | 年間ヒートマップビュー | B-3 | 180 | 監視 |

**C5 リスク管理**: 単独180行は 150行ガイドラインを超える。180→150に削るオプション:
- 月別フィルター無し、純粋ヒートマップだけにする
- 凡例を最小化
- 年送りボタンをドット表示で省スペース

最終的に超えるなら、C5 を C5a(CSS+構造、~80行)と C5b(描画ロジック+ジャンプ、~100行)に分割。

---

## 5. 設計原則の遵守

- ✅ **build.py のみ編集**: index.html/manifest.json/sw.js は自動生成
- ✅ **各コミット150行以内**: C5 は監視必要、最悪分割
- ✅ **firebase-config.js/events.json/extract_events.py 触らない**
- ✅ **本番 events コレクションへ書き込みしない**(テストは別コレクション or 即削除)
- ✅ **既存デザイン哲学(Calm Canvas / ケロッピー)維持**
- ✅ **--no-verify/--force フラグ禁止**
- ✅ **エラー時 git checkout でロールバック**

---

## 6. テスト計画

各コミット後、`preview_eval` で以下を確認:

| C# | 確認項目 |
|---|---|
| C1 | 2026年1月セル表示時、1/1が赤(holiday). SW生成ファイルの CACHE 行に timestamp が入る. |
| C2 | カスタム予定を1つ追加→編集画面で削除→ケロッピー風シート表示確認→確定で削除 |
| C3 | 設定で記念日「テスト/12/25」追加→ヒーローカード status に「あとXX日でテスト」表示 |
| C4 | localStorage に過去日付のテストメモ仕込み→今日と同月日にRecall表示 |
| C5 | 年ビューボタン→グリッド表示→両方休み日がピンク→セルタップで月ジャンプ |

---

## 7. ロールバック条件

以下のいずれかで該当コミットを `git checkout` でロールバック:

- ビルドエラー(`python build.py` が失敗)
- HTMLサイズが20%以上変動(意図しないテンプレ破損)
- preview起動で console error
- 既存機能のregression(ヒーローカード非表示、Firebase接続失敗など)
- コミット差分が180行超

ロールバックしても他コミットは保持(独立したコミット設計のため)。
