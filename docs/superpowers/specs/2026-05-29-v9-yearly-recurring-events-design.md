# シフトカレンダー v9「毎年繰り返しの予定」設計

**日付**: 2026-05-29
**ターゲット**: https://tamahome0208-prog.github.io/shift-calendar/
**スコープ**: 既存「記念日」機能を「毎年の予定」に拡張、カレンダー上にも表示
**コミット計画**: 1コミット、~130行(150行枠内)

---

## 0. なぜやるか

ユーザー要望:「誕生日など毎年繰り返しの予定を追加したい」。現状の予定追加は単発(1日付固定)、年次繰返データの専用入口は無い。

既存 `anniversaries` collection は既に `{name, month, day, type}` という**年フリーの月日固定**データモデルで、これは年次繰返にとって理想形。これを活用して "毎年の予定" 機能を完成させる。

---

## 1. 何を変えるか

### 1-1. 設定シート(UI)

- ラベル変更:「**記念日**(最大3件)」→「**毎年の予定**(誕生日・記念日など)」
- **3件上限撤廃**(常時追加可)
- 種類選択追加:`birth🎂` / `anniv💗` / `other🌸` の3択ピッカー(新規追加時のみ。既存編集機能は無し)
- 名前/月/日 + 種類の4フィールドで追加

### 1-2. カレンダーグリッド表示

`render()` 内、各セル描画ロジック拡張:
- 各セルの (year, month, day) について `allAnniversaries` を線形検索
- マッチがあれば該当セルに**特別チップ**を追加(通常のイベントチップ群の最後尾)
- 表示形式: `[🎂アイコン] [name]` を1〜2行で。タップ動作は今回はなし(YAGNI)

### 1-3. 色分け

| type | チップ背景 | アイコン |
|---|---|---|
| `birth` | linear-gradient(135deg, var(--cheek) 0%, var(--cheek-deep) 100%) | st-cake(新規) |
| `anniv` | linear-gradient(135deg, var(--yui) 0%, var(--yui-meeting) 100%) | heart(既存) |
| `other` | linear-gradient(135deg, var(--custom) 0%, #A372C6 100%) | st-star(既存) |

未指定/不明 → `other` 扱い。

### 1-4. ヒーローカード

既存「あとX日で○○」表示は**変更なし**。30日以内の最近接を表示。

---

## 2. データモデル

### 2-1. anniversaries collection(既存、変更なし)

```js
{ id: string, name: string, month: 1-12, day: 1-31, type: 'birth'|'anniv'|'other' }
```

`type` が無い既存データは `'other'` として描画。

### 2-2. Firestore セキュリティルール

変更不要(既に `anniversaries` collection 許可済み)。

---

## 3. SVGアイコン追加

新規 `st-cake`(誕生日用ケーキ):
```html
<symbol id="st-cake" viewBox="0 0 24 24">
  <rect x="4" y="12" width="16" height="9" rx="1.5" fill="#FFD9E6" stroke="#F764A2" stroke-width="0.8"/>
  <path d="M 4 15 Q 8 17 12 15 Q 16 17 20 15" stroke="#F764A2" stroke-width="1" fill="none"/>
  <rect x="11" y="6" width="2" height="6" fill="#FBBF24" rx="0.5"/>
  <path d="M12 4 L 12.5 6 L 11.5 6 Z" fill="#FF8E5C"/>
</symbol>
```

(SVG sprite defs に追加、~12行)

---

## 4. CSS 追加

```css
.anniv-chip {
  padding: 3px 4px;
  border-radius: 7px;
  color: white;
  font-size: 9.5px;
  font-weight: 800;
  display: flex;
  align-items: center;
  gap: 3px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  letter-spacing: -0.03em;
  position: relative;
  pointer-events: none;
}
.anniv-chip svg {
  width: 12px; height: 12px;
  flex-shrink: 0;
}
.anniv-chip.t-birth { background: linear-gradient(135deg, var(--cheek) 0%, var(--cheek-deep) 100%); }
.anniv-chip.t-anniv { background: linear-gradient(135deg, var(--yui) 0%, var(--yui-meeting) 100%); }
.anniv-chip.t-other { background: linear-gradient(135deg, var(--custom) 0%, #A372C6 100%); }
```

---

## 5. ロジック変更

### 5-1. 設定シート HTML

`anniv-add-form` の名前入力直後に種類ピッカー追加:
```html
<div style="display:flex;gap:6px;margin-bottom:6px;">
  <select id="anniv-type" style="flex:1;padding:10px;border-radius:10px;border:1.5px solid var(--border);font-size:14px;">
    <option value="birth">🎂 誕生日</option>
    <option value="anniv" selected>💗 記念日</option>
    <option value="other">🌸 その他</option>
  </select>
</div>
```

### 5-2. anniv-save クリックハンドラ修正

既存:
```js
await Storage.addAnniv({ name, month, day });
```

新規:
```js
const type = document.getElementById('anniv-type').value;
await Storage.addAnniv({ name, month, day, type });
```

### 5-3. ラベルとボタン制御撤廃

既存:
```html
<label>記念日(最大3件)</label>
```

変更後:
```html
<label>毎年の予定(誕生日・記念日など)</label>
```

`renderSettingsAnniv` 内の `annivs.length >= 3 ? 'none' : 'inline-flex'` を削除(常時表示)。

### 5-4. render() 内グリッド描画拡張

`dayEvents` 描画ループの直後、`if (dayEvents.length > 3)` の前後に挿入:
```js
const anniversariesForDay = (allAnniversaries || []).filter(a => a.month === m + 1 && a.day === d);
anniversariesForDay.forEach(a => {
  const type = a.type || 'other';
  const chip = document.createElement('div');
  chip.className = `anniv-chip t-${type}`;
  const iconId = type === 'birth' ? 'st-cake' : (type === 'anniv' ? 'heart' : 'st-star');
  chip.innerHTML = `<svg><use href="#${iconId}"/></svg><span>${escapeHtml(a.name)}</span>`;
  cell.appendChild(chip);
});
```

注意: 各セル描画ループ内で `m, d` は **viewMonth + 1** ではなく、そのセル自身の月日(0-origin の `m`)を使用するため `m + 1` でマッチ。

### 5-5. 既存リストへの type 表示

`renderSettingsAnniv` の row HTML を以下に変更(既存名と日付に種類絵文字を添える):
```js
const typeEmoji = { birth: '🎂', anniv: '💗', other: '🌸' }[a.type || 'other'];
row.innerHTML = `
  <span class="anniv-name">${typeEmoji} ${escapeHtml(a.name)}</span>
  <span class="anniv-date">${a.month}/${a.day}</span>
  <button class="anniv-del" data-id="${a.id}" aria-label="削除">×</button>
`;
```

ここは絵文字使用(設定画面のみ、ささやかな視認補助)。カレンダー本体は自作SVGで統一。

---

## 6. 規模見積もり

| 項目 | 推定行 |
|---|---|
| SVG sprite (st-cake) | +12 |
| CSS (.anniv-chip*) | +24 |
| 設定シート HTML(種類ピッカー) | +7 |
| ラベル文言変更 | +1/-1 |
| renderSettingsAnniv 修正 | +5/-3 |
| anniv-save 修正 | +2/-0 |
| 上限制限削除 | -2/+0 |
| render() グリッド拡張 | +10 |
| 合計 | **+62行 前後** |

仕様書のスコープ目安は 130行だったが、実装はもっとスリム。1コミットで余裕で収まる。

---

## 7. 範囲外(YAGNI)

- 月次・週次繰返(別タスク)
- 既存 custom events に recurrence フラグ追加
- フィルターチップに「毎年」追加
- カレンダーチップタップでの編集ダイアログ(現状は設定シートで管理)
- 通知連動(誕生日リマインダー)
- 過去年齢計算(誕生日でも「○歳の誕生日」とは表示しない)
- 既存記念日の type 変更 UI(削除→再追加で対応)

---

## 8. 実装ファイル

| ファイル | 役割 | 変更可否 |
|---|---|---|
| `build.py` | テンプレ + ロジック | ✅ |
| 生成物 | 自動生成 | ❌ |

Firestore スキーマ・ルール変更なし。

---

## 9. コミット計画

| # | 内容 | 推定行数 |
|---|---|---|
| C1 | 毎年の予定機能(SVG+CSS+設定UI+render拡張+ラベル変更) | ~70行 |

1コミットで完結。

---

## 10. テスト計画

| 観点 | 検証 |
|---|---|
| 既存データ | 既に登録済みの記念日が `other` として正しく表示される |
| 新規追加 | 設定 → 種類選択 → 保存 → 該当月日のセルに表示 |
| 4件目以降 | 3件以上でも追加可能(上限撤廃) |
| 色分け | birth=ピンクケーキ、anniv=ハート、other=星 |
| 月跨ぎ | 他月セル(前月末/翌月頭表示)でも該当日にマッチすれば表示 |
| ヒーローカウントダウン | 既存挙動維持 |

---

## 11. ロールバック条件

- ビルドエラー / preview 起動失敗
- HTML サイズ 20% 以上変動
- 既存機能(設定/anniv追加/ヒーローカウントダウン)の regression
- 1コミット150行超 → `git checkout` でロールバック → 機能分割
