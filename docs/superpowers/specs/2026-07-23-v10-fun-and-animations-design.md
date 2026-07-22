# シフトカレンダー v10「もっと楽しくなる」+アニメ強化 設計

**日付**: 2026-07-23
**ターゲット**: https://tamahome0208-prog.github.io/shift-calendar/
**スコープ**: 3コアフィーチャー + 8アニメーション、3コミット分割
**合計規模見積**: ~240行(150行×3コミット枠内、余裕あり)

---

## 0. なぜやるか

ユーザー要望:「視認性を高める」+「使っていて楽しくなる機能を追加」。既に v9 まで機能は揃った。ここからは "開くのが楽しい" 体験に振り、二人で日々シフトを見る動機を作る。

方向A(温度)/B(視認性)/C(小さな喜び)/D(統計)を"エッセンスだけ"1つずつ抽出して盛り込む。

---

## 1. コアフィーチャー(3)

### F1. 休み被り DAY 紙吹雪演出(方向A)

既存 `both-off-banner`(「二人ともお休み 💗」表示)を発展。両者休みの日をタップして day-overlay を開いた瞬間、画面上部から色紙が舞い降りる。

**動作:**
- `refreshDaySheet` 呼び出し時、`isBothOff(builtin)` が true なら confetti burst 実行
- 30〜40片、1.5秒で消える、pointer-events: none で操作を阻害しない
- CSS keyframe(`@keyframes conf-fall`)で回転+落下
- 色: `--cheek`, `--leaf`, `--yui`, `--kouki`, `--custom` の5色ローテ

### F2. 月間サマリーカード(方向B/D)

月ビュー上部(月ヘッダー直下、グリッドの前)に3枚のカラフルなミニカード:

```
┌────────┐ ┌────────┐ ┌────────┐
│ こうき  │ │ ゆい    │ │ 被り   │
│  14    │ │  12    │ │  6    │
│ 出勤日 │ │ 出勤日 │ │  💗   │
└────────┘ └────────┘ └────────┘
```

**集計ロジック:**
- `viewYear`/`viewMonth` に該当する月の全日を走査
- **休扱いラベル** = `{'休', '希望休', '有'}` の集合
- **こうき出勤日** = 月の日数 − (その月のこうきの EVENTS entries のうち summary が 休扱いラベル に含まれる日数)
  - つまり: 明示的 EVENTS が無い日(default working)+ 会議/出店/A/MTG/出張 の日
- **ゆい出勤日** = 同ロジックでゆい
- **被り日** = 「その日にこうきの休扱いエントリがある」AND「その日にゆいの休扱いエントリがある」日数
- 給料日エントリ(person="給料")は集計対象外

**カラー:**
- こうき: `linear-gradient(135deg, var(--kouki), var(--pond-dark))`
- ゆい:   `linear-gradient(135deg, var(--yui), var(--yui-meeting))`
- 被り:   `linear-gradient(135deg, var(--leaf), var(--leaf-dark))`(緑=ハート付)

### F3. 月別シーズンアクセント(方向C)

月ヘッダー(月表示・切替矢印を含むバー)の背景色を月に応じて変化。

**月別テーマ:**
| 月 | テーマ | ヘッダー背景 | 記号 |
|---|---|---|---|
| 1 | お正月 | `linear-gradient(135deg, #FEF3C7, #FDE68A)` | 🎍 |
| 2-3 | 梅 | `linear-gradient(135deg, #FEE7EF, #FCE7F3)` | 🌸 |
| 4 | 桜 | `linear-gradient(135deg, #FFE4E1, #FBCFE8)` | 🌸 |
| 5 | 新緑 | `linear-gradient(135deg, #ECFCCB, #D9F99D)` | 🌱 |
| 6 | 紫陽花 | `linear-gradient(135deg, #DBEAFE, #C7D2FE)` | ☔ |
| 7 | 向日葵 | `linear-gradient(135deg, #FEF9C3, #FEF3C7)` | 🌻 |
| 8 | 夏空 | `linear-gradient(135deg, #DBEAFE, #BFDBFE)` | 🌊 |
| 9 | 秋 | `linear-gradient(135deg, #FEF3C7, #FDBA74)` | 🍁 |
| 10 | 紅葉 | `linear-gradient(135deg, #FFE4E1, #FED7AA)` | 🍁 |
| 11 | 落葉 | `linear-gradient(135deg, #FEF3C7, #FCD34D)` | 🍂 |
| 12 | 雪 | `linear-gradient(135deg, #DBEAFE, #E0F2FE)` | ❄️ |

現行の月ヘッダーは白背景固定。これを月ごとに置換する。

**実装:**
- JS 定数 `SEASON_THEMES = {1: {...}, 2: {...}, ...}`
- `render()` 内で `viewMonth+1` からテーマ取得、月ヘッダー要素の style.background 更新
- 月切替のトランジションは C2 で追加

---

## 2. アニメーション(8)

### A. 紙吹雪バースト
→ F1 と統合。実装は F1 参照。

### B. カウントアップ
サマリーカードの数字が0から目標値へ加速→減速で駆け上がる。

- `requestAnimationFrame` ベース、~600ms
- easing: `easeOutCubic`
- `render()` 内でカード数字要素に対して `animateCount(el, 0, target, 600)` 呼び出し
- 月切替のたびに再演出

### C. チップ順次登場強化
既存の `dayEvents.forEach((e, idx) => { row.style.animationDelay = idx * 50ms })` を月切替時のセル自体にも拡張。

- 月切替時、41セル(日曜〜土曜 × 6週)がインデックス順に "沸き上がる"
- 各セル `animation: cellRise 0.4s var(--ease-spring) both` + delay `idx * 12ms`
- `@keyframes cellRise { from { opacity: 0; transform: translateY(6px) scale(0.96); } }`

### D. 月ヘッダー横スライド
月切替時、ヘッダー全体が横にスライドしながらフェード切替。

- `prev` ボタン: 右→左(month name が left へ swipe out、新 name が right からslide in)
- `next` ボタン: 左→右
- 300ms、`cubic-bezier(0.4, 0, 0.2, 1)`
- ヘッダー背景色(F3)は最初と最後で変化するので、gradient 遷移も含む

### E. ヒーローハート鼓動
記念日カウントダウンのハートを定期的にドクン。

- `#heart` symbol を使う要素に `.heart-beat` class 付与
- `@keyframes heartBeat { 0%,60%,100% { transform: scale(1); } 70% { transform: scale(1.2); } 80% { transform: scale(0.95); } 90% { transform: scale(1.1); } }`
- 2秒間隔で無限リピート
- 現行のfloatとは別レイヤーで、鼓動のみ追加

### F. セルタップ波紋
セルタップ時、タップ位置から円が広がる Material 風。

- `.day-cell` に `overflow: hidden; position: relative;` (既に position は relative)
- タップ位置座標から `<span class="ripple">` を動的挿入、animation 完了後 remove
- `@keyframes ripple { from { transform: scale(0); opacity: 0.5; } to { transform: scale(10); opacity: 0; } }` 500ms

### G. 記念日くねくね
`.anniv-chip` が定期的にゆらり揺れる(目立ちすぎない程度)。

- `@keyframes annivWiggle { 0%,90%,100% { transform: rotate(0); } 92% { transform: rotate(-4deg); } 95% { transform: rotate(3deg); } 98% { transform: rotate(-1deg); } }`
- animation-duration: 4s、無限、`transform-origin: center`
- `prefers-reduced-motion: reduce` で無効化

### H. シーズン粒子
月ヘッダー背景に微かなキラキラ点滅。

- ヘッダーに absolute の `.season-particle` div を 3個配置
- 各 `background: radial-gradient(circle, rgba(255,255,255,0.8) 0%, transparent 70%)`
- `@keyframes sparkle { 0%,100% { opacity: 0; transform: scale(0.6); } 50% { opacity: 0.9; transform: scale(1); } }` 2〜3秒
- 位置は月ごとに固定(top: 20%/60%/40%, left: 25%/70%/85%)

---

## 3. データモデル

**変更なし。** 全て既存の `EVENTS`, `allCustomEvents`, `allAnniversaries` から算出。Firestore スキーマ変更なし。

---

## 4. コミット分割

### C1: F1 + F2 + Anim B(推定 90行)
- 紙吹雪 CSS(20行)
- 紙吹雪 JS(20行、`spawnConfetti()`)
- サマリーカード HTML/CSS(30行)
- サマリー計算+描画 JS(15行、`renderSummary()`)
- カウントアップ helper(15行、`animateCount()`)

### C2: F3 + Anim H + Anim D(推定 80行)
- SEASON_THEMES 定数(15行)
- 月ヘッダー背景適用 JS(10行)
- Anim D 月スライド CSS+JS(30行)
- Anim H キラキラ粒子 CSS+HTML(15行)
- 統合微調整(10行)

### C3: Anim C + E + F + G(推定 70行)
- cellRise stagger(15行)
- heartBeat(10行)
- ripple 波紋(25行)
- annivWiggle(10行)
- reduced-motion 対応(10行)

**合計: 約 240行**、150行×3コミット枠内で余裕。

---

## 5. 実装ファイル

すべて `build.py` 編集のみ。

| ファイル | 役割 | 変更可否 |
|---|---|---|
| `build.py` | HTMLテンプレ+CSS+JS | ✅ |
| 生成物 (index.html等) | 自動生成 | ❌ |
| firebase-config.js / events.json / extract_events.py | 別目的 | ❌ |
| Firestore | スキーマ変更なし | 既存 |

---

## 6. 範囲外(YAGNI)

- スタンプ/シール貼り付け機能(A方向の別要素)
- 週表示・大文字モード(B方向の別要素)
- ケロッピー歩き・ガチャ(C方向の別要素)
- 給料計算補助・ダイジェスト画像出力(D方向の別要素)
- confetti を canvas 実装(SVG/CSSで十分軽い)
- 月ヘッダーの季節文字追加(絵文字1つだけ)

---

## 7. アクセシビリティ

- 全てのアニメを `@media (prefers-reduced-motion: reduce)` で無効化
- サマリーの数字は aria-label で「こうき14日出勤」等を明示
- 紙吹雪は decorative なので `aria-hidden="true"`
- カウントアップは reduce-motion 環境では即最終値表示

---

## 8. パフォーマンス

- 紙吹雪: 40片、CSS animation で GPU 加速、1.5秒で完全消滅
- カウントアップ: `requestAnimationFrame` 使用、DOM は数字要素のみ更新
- cellRise: transform+opacity のみ、reflow なし
- キラキラ粒子: 3個のみ、CSS animation

FPS 影響最小、モバイル前提でも滑らか。

---

## 9. テスト計画

| 観点 | 検証 |
|---|---|
| F1 紙吹雪 | 二人休みの日をタップ→紙吹雪が舞い、1.5秒で消える |
| F2 サマリー | 月切替でカード数字が更新される |
| F3 シーズン | 1月→12月まで切替、ヘッダー色が変化 |
| B カウント | サマリー数字が0から目標値へアニメーション |
| C 順次登場 | 月切替でセルが波打って現れる |
| D 月スライド | 月ヘッダーが横にスライド遷移 |
| E ハート鼓動 | ヒーローハートが2秒間隔でドクン |
| F 波紋 | セルタップで円が広がる |
| G くねくね | 記念日チップが4秒毎に揺れる |
| H キラキラ | シーズンヘッダーに粒子が明滅 |
| reduce-motion | 全アニメ無効化される |
| 既存機能 | 記念日カウントダウン・履歴シート・毎年予定表示は無影響 |

---

## 10. ロールバック条件

- ビルドエラー / preview 起動失敗
- HTMLサイズ 30% 以上変動
- 既存機能(day-overlay, settings, history-overlay, カウントダウン)の regression
- 単一コミット 200行超 → `git checkout` で該当コミットをロールバック、分割
- FPS が体感で下がる → 該当アニメを opt-out で戻せるように分離

---

## 11. コミット順序

1. C1(F1+F2+B) → build + preview 動作確認 → push
2. C2(F3+H+D) → build + preview 動作確認 → push
3. C3(C+E+F+G) → build + preview 動作確認 → push

各コミット後に user が iOS/Android の実機で確認できる仕組み(GitHub Pages反映後1-2分)。
