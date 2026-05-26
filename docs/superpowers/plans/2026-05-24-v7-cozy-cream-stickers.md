# v7 Cozy Cream + Stickers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** クリーム背景+ビビッドアクセント+自作SVGステッカー6種で「やわらかく可愛く見やすい」デザインに刷新する。

**Architecture:** 単一ファイル `build.py` 内の `:root` 変数群と SVG sprite defs を更新し、JS render 側で各イベントチップ左に SVG `<use>` 参照を埋め込む。ヘッダーに装飾SVG(雲・葉)を絶対配置。2コミットに分割し各150〜180行以内を厳守。

**Tech Stack:** Python 3 (build時) / HTML+CSS+JS (生成物) / SVG sprite inline

**前提コマンド:**
- ビルド: `python "C:\Users\tamah\Desktop\shift_calendar\build.py" "C:\Users\tamah\OneDrive\Desktop\【登別店】2026年6月シフト初稿  (version 1).xlsx"`
- 差分計測: `git diff --cached --stat`
- ロールバック: `git checkout build.py index.html manifest.json sw.js`

---

## File Structure

すべて `C:\Users\tamah\Desktop\shift_calendar\build.py` の編集。生成物 `index.html` / `manifest.json` / `sw.js` は自動更新、直接編集禁止。

| ファイル | 役割 | 変更可否 |
|---|---|---|
| `build.py` | HTMLテンプレ + 定数 | ✅ 編集 |
| `index.html` / `manifest.json` / `sw.js` | 生成物 | ❌ 直接禁止 |
| `firebase-config.js` | API設定 | ❌ 触らない |
| `events.json` / `extract_events.py` | 別目的 | ❌ 触らない |

---

## Task 1: カラーパレット移行(Cozy Cream)

**Phase:** C1
**推定差分:** +90/-80行(build.py 単体)
**コミット:** C1

**Files:**
- Modify: `build.py:34-88` (`:root` ブロック)

### Step 1.1: `:root` 変数を一括書き換え

- [ ] **Locate `:root` ブロック**

Run:
```bash
grep -n "^:root {" "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

Expected: `34::root {`

- [ ] **既存の `:root` ブロック全体を新パレットで置換**

旧(`build.py:34-88` 付近、`:root {` から `}` まで)を Read で確認後、以下の新ブロックに置換:

```python
:root {
  /* Keroppi-vivid Cozy Cream パレット */
  --leaf: #84CC16;
  --leaf-dark: #65A30D;
  --leaf-deep: #3F6212;
  --pond: #5AA6DC;
  --pond-dark: #2E7CB9;
  --pond-light: #B8DCF0;
  --cheek: #FFAFC5;
  --cheek-deep: #F764A2;
  --belly: #FDF6D8;
  --lily-pink: #FFD9E6;
  --mint-mist: #ECF8E3;
  --water-mist: #E8F4FB;
  --peach: #FFB892;
  --peach-deep: #FF8E5C;
  --sunshine: #FBBF24;

  /* 機能色 - Cozy Cream Canvas */
  --bg: #FFF8F0;
  --bg-2: #FFEFDF;
  --surface: #ffffff;
  --surface-soft: #FFFAEF;
  --surface-2: #FFEAD8;
  --text: #1F1A0F;
  --text-2: #3F341F;
  --muted: #8A7860;
  --muted-2: #A89878;
  --border: #F8E4CC;
  --border-strong: #E8C8A0;
  --hairline: rgba(120, 70, 20, 0.08);

  --kouki: #5AA6DC;
  --kouki-meeting: #2E7CB9;
  --kouki-outing: #92C9E8;
  --kouki-soft: #E8F4FB;
  --yui: #F764A2;
  --yui-meeting: #DC4A88;
  --yui-outing: #FFBED4;
  --yui-soft: #FFE9F1;
  --pay: #65A30D;
  --pay-soft: #ECF8E3;
  --custom: #C58AE0;
  --custom-soft: #F4E8FB;

  --shadow-xs: 0 1px 1px rgba(120, 70, 20, 0.05);
  --shadow-sm: 0 2px 6px rgba(120, 70, 20, 0.06), 0 1px 2px rgba(120, 70, 20, 0.04);
  --shadow-md: 0 4px 12px rgba(120, 70, 20, 0.08), 0 2px 4px rgba(120, 70, 20, 0.05);
  --shadow-lg: 0 24px 48px rgba(120, 70, 20, 0.15), 0 8px 16px rgba(120, 70, 20, 0.06);
  --shadow-pink: 0 4px 16px rgba(247, 100, 162, 0.3);
  --shadow-leaf: 0 4px 16px rgba(132, 204, 22, 0.28);
  --shadow-inset: inset 0 1px 0 rgba(255, 255, 255, 0.5);

  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
  --ease-out: cubic-bezier(0.32, 0.72, 0, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);

  --safe-top: env(safe-area-inset-top, 0px);
  --safe-bottom: env(safe-area-inset-bottom, 0px);
  --font-jp: "Zen Maru Gothic", -apple-system, BlinkMacSystemFont, "Hiragino Maru Gothic ProN", "Yu Gothic UI", sans-serif;
  --font-en: "Plus Jakarta Sans", -apple-system, "Zen Maru Gothic", sans-serif;
}
```

注意: `Edit` ツール使用前に必ず `Read` で既存内容を取得し `old_string` 完全一致を確認。

### Step 1.2: header 背景色も RGB 値で参照している箇所を更新

- [ ] **Find existing rgba(253, 255, 252,...) in header**

Run:
```bash
grep -n "rgba(253, 255, 252" "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

該当行があれば `rgba(255, 248, 240, 0.78)` に変更(クリーム背景の半透明版)。

### Step 1.3: theme-color メタタグ更新

- [ ] **Modify `<meta name="theme-color">`**

既存:
```html
<meta name="theme-color" content="#fdfffc">
```

新規:
```html
<meta name="theme-color" content="#FFF8F0">
```

Run:
```bash
grep -n 'name="theme-color"' "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

manifest.json テンプレ内も同様に該当行を修正(`background_color` / `theme_color` が `#fdfffc` なら `#FFF8F0` に変更)。

Run:
```bash
grep -n '"background_color"\|"theme_color"' "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

### Step 1.4: body 背景グラデの色相を暖色寄りに更新

- [ ] **Locate `body {` の background-image**

Run:
```bash
grep -n "radial-gradient(circle at 100% 0%" "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

既存:
```css
  background-image:
    radial-gradient(circle at 100% 0%, rgba(124, 194, 67, 0.04) 0%, transparent 36%),
    radial-gradient(circle at 0% 100%, rgba(255, 122, 165, 0.03) 0%, transparent 40%);
```

新規:
```css
  background-image:
    radial-gradient(circle at 100% 0%, rgba(255, 184, 146, 0.08) 0%, transparent 36%),
    radial-gradient(circle at 0% 100%, rgba(247, 100, 162, 0.04) 0%, transparent 40%);
```

### Step 1.5: ビルドして検証

- [ ] **Run build**

```bash
python "C:\Users\tamah\Desktop\shift_calendar\build.py" "C:\Users\tamah\OneDrive\Desktop\【登別店】2026年6月シフト初稿  (version 1).xlsx"
```

Expected: `index.html (63件のイベント)` の正常終了

- [ ] **Run 差分計測**

```bash
cd "C:\Users\tamah\Desktop\shift_calendar"
git add -A
git diff --cached --stat
```

Expected: build.py +90/-80程度、合計150行以内

- [ ] **180行超過なら中止しロールバック**

```bash
git checkout build.py index.html manifest.json sw.js
```

その場合は :root 変数の追加分を抑えて再実装(ペーパー値は新色のみ、shadow は据置 など分割)。

### Step 1.6: コミット & プッシュ

- [ ] **Commit**

```bash
cd "C:\Users\tamah\Desktop\shift_calendar"
git commit -m "$(cat <<'EOF'
v7-C1: Cozy Cream カラーパレット移行

- bg #FBFBF7 → #FFF8F0(クリーム)、bg-2 ピーチクリームへ
- アクセント彩度キープ: leaf #7CC243→#84CC16, cheek-deep #FF7AA5→#F764A2
- 追加: peach #FFB892, peach-deep #FF8E5C, sunshine #FBBF24
- 影と hairline を暖色寄り rgba に
- theme-color と manifest 背景色をクリームに同期

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git push
```

---

## Task 2: SVGステッカー6種+チップ組込+ヘッダー装飾

**Phase:** C2
**推定差分:** +160/-50行(build.py 単体)
**コミット:** C2

**Files:**
- Modify: `build.py:1228-` (SVG sprite defs ブロック)
- Modify: `build.py:1342` 付近(header HTML)
- Modify: 各 CSS の `.event` 周辺
- Modify: JS の `eventTypeClass` 近辺に `stickerId(summary, person)` を追加
- Modify: render() 内の `ev.innerHTML = ...` 2箇所

### Step 2.1: SVG sprite に 6+2 シンボル追加

- [ ] **Locate `<svg class="sprite"` の `<defs>`**

Run:
```bash
grep -n 'class="sprite"' "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

- [ ] **`<defs>` の閉じ `</defs>` 直前に以下シンボルを追加**

```html
    <!-- v7 イベントステッカー6種 -->
    <symbol id="st-leaf" viewBox="0 0 24 24">
      <path d="M5 18 C 6 10, 12 4, 19 5 C 18 12, 12 18, 5 18 Z" fill="#84CC16" stroke="#65A30D" stroke-width="0.8" stroke-linejoin="round"/>
      <path d="M 5 18 Q 11 13 18 6" stroke="#3F6212" stroke-width="0.8" fill="none" stroke-linecap="round"/>
    </symbol>
    <symbol id="st-bubble" viewBox="0 0 24 24">
      <path d="M4 6 Q 4 3 7 3 H 17 Q 20 3 20 6 V 13 Q 20 16 17 16 H 11 L 7 20 V 16 H 7 Q 4 16 4 13 Z" fill="#5AA6DC" stroke="#2E7CB9" stroke-width="0.8" stroke-linejoin="round"/>
      <circle cx="9" cy="10" r="1" fill="white"/>
      <circle cx="12" cy="10" r="1" fill="white"/>
      <circle cx="15" cy="10" r="1" fill="white"/>
    </symbol>
    <symbol id="st-bag" viewBox="0 0 24 24">
      <path d="M 8 6 V 5 a 4 4 0 0 1 8 0 V 6" stroke="#FF8E5C" stroke-width="1.4" fill="none" stroke-linecap="round"/>
      <path d="M 5 7 H 19 L 18 20 H 6 Z" fill="#FFB892" stroke="#FF8E5C" stroke-width="0.8" stroke-linejoin="round"/>
    </symbol>
    <symbol id="st-star" viewBox="0 0 24 24">
      <path d="M12 3 L 14 10 L 21 12 L 14 14 L 12 21 L 10 14 L 3 12 L 10 10 Z" fill="#FBBF24" stroke="#D97706" stroke-width="0.6" stroke-linejoin="round"/>
    </symbol>
    <symbol id="st-coin" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="9" fill="#FBBF24" stroke="#3F6212" stroke-width="0.8"/>
      <circle cx="12" cy="12" r="6.5" fill="none" stroke="#3F6212" stroke-width="0.5" opacity="0.4"/>
      <text x="12" y="16" text-anchor="middle" font-size="11" font-weight="900" fill="#3F6212">¥</text>
    </symbol>
    <symbol id="st-pin" viewBox="0 0 24 24">
      <path d="M12 3 L 12 12 L 7 14 L 12 14 L 12 22 L 13 14 L 17 14 L 12 12 Z" fill="#C58AE0" stroke="#9333EA" stroke-width="0.7" stroke-linejoin="round"/>
      <circle cx="12" cy="8" r="2.4" fill="#A372C6"/>
    </symbol>
    <!-- v7 ヘッダー装飾 -->
    <symbol id="deco-cloud" viewBox="0 0 96 36">
      <path d="M 14 24 Q 6 24 6 18 Q 6 12 14 12 Q 16 4 26 6 Q 32 0 42 6 Q 52 4 56 12 Q 72 10 76 18 Q 80 26 70 28 H 16 Q 10 28 14 24 Z" fill="currentColor"/>
    </symbol>
    <symbol id="deco-leaf-small" viewBox="0 0 24 24">
      <path d="M3 21 Q 4 11 12 4 Q 20 6 21 14 Q 18 22 6 21 Z" fill="currentColor"/>
      <path d="M 5 19 Q 11 14 19 8" stroke="rgba(0,0,0,0.25)" stroke-width="0.6" fill="none" stroke-linecap="round"/>
    </symbol>
```

### Step 2.2: ヘッダーに装飾追加

- [ ] **Locate `<header>` の HTML 直後**

Run:
```bash
grep -n "<header>" "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

(おそらく `build.py:1340` 付近の header オープニングタグ直後)

- [ ] **`<header>` の開きタグ直後に header-deco を挿入**

```html
  <div class="header-deco" aria-hidden="true">
    <svg class="deco-cloud-1"><use href="#deco-cloud"/></svg>
    <svg class="deco-leaf-1"><use href="#deco-leaf-small"/></svg>
  </div>
```

### Step 2.3: ヘッダー装飾の CSS 追加

- [ ] **Locate CSS の `header { ... }` ブロックの直後**

Run:
```bash
grep -n "^header {" "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

- [ ] **`header { ... }` の閉じ `}` の直後に追加**

```css
.header-deco {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}
.header-deco svg { position: absolute; }
.deco-cloud-1 {
  top: calc(var(--safe-top) + 14px);
  right: -8px;
  width: 90px;
  height: 36px;
  opacity: 0.32;
  color: var(--peach);
}
.deco-leaf-1 {
  bottom: 10px;
  left: 58%;
  width: 22px;
  height: 22px;
  opacity: 0.28;
  color: var(--leaf);
  transform: rotate(-15deg);
}
header > * { position: relative; z-index: 1; }
header { position: sticky; }
```

注意: 既存の `header { position: sticky; ... }` と重複しないよう、既存の `position: sticky` 行があるか確認。あれば追加不要。

### Step 2.4: イベントチップに sticker 用 CSS

- [ ] **Locate `.event {` の CSS ブロック**

Run:
```bash
grep -n "^\.event {" "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

- [ ] **`.event { ... }` ブロック内の display 行を grid に変更**

既存:
```css
.event {
  padding: 3px 2px 4px;
  border-radius: 7px;
  color: white;
  line-height: 1.05;
  min-width: 0;
  max-width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  ...
}
```

新規(`display: flex; flex-direction: column; align-items: center;` を `display: grid; grid-template-columns: 12px 1fr; align-items: center; gap: 3px;` に置換、その他の関連プロパティ調整):
```css
.event {
  padding: 4px 4px 4px 3px;
  border-radius: 7px;
  color: white;
  line-height: 1.05;
  min-width: 0;
  max-width: 100%;
  display: grid;
  grid-template-columns: 12px 1fr;
  align-items: center;
  gap: 3px;
  letter-spacing: -0.03em;
  overflow: hidden;
  text-align: left;
  transition: transform 0.18s var(--ease-spring);
  position: relative;
}
.event-sticker {
  width: 12px;
  height: 12px;
  flex-shrink: 0;
  opacity: 0.95;
  filter: drop-shadow(0 1px 0 rgba(255,255,255,0.4));
}
.event-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
  align-items: flex-start;
}
```

注意: 既存 `.event` の他プロパティ(`background`、`color` 等)は維持する。`Read` で完全一致を確認してから `Edit` する。

### Step 2.5: JS に stickerId 関数追加

- [ ] **Locate `function eventTypeClass(`**

Run:
```bash
grep -n "function eventTypeClass" "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

- [ ] **`function eventTypeClass(...)` の閉じ `}` の直後に挿入**

```javascript
function stickerId(summary, person) {
  if (A_SHIFT_LABELS.includes(summary)) return 'st-star';
  if (MEETING_LABELS.includes(summary)) return 'st-bubble';
  if (OUTING_LABELS.includes(summary)) return 'st-bag';
  if (REST_LABELS.includes(summary)) return 'st-leaf';
  if (person === '給料') return 'st-coin';
  if (person === '予定') return 'st-pin';
  return null;
}
```

### Step 2.6: render() の event innerHTML を sticker 込みに更新

- [ ] **Locate render() 内の `ev.innerHTML = `**

Run:
```bash
grep -n "ev.innerHTML = " "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

該当 2 行あり(`build.py:2176` と `2178`)。

- [ ] **Modify `build.py:2176-2179` の if/else ブロック全体を置換**

既存:
```javascript
      if (e.person === '給料') {
        ev.innerHTML = `<span class="event-label">${escapeHtml(e.summary)}</span>`;
      } else {
        ev.innerHTML = `<span class="event-name">${e.person}</span><span class="event-label">${escapeHtml(e.summary)}</span>`;
      }
```

新規:
```javascript
      const sId = stickerId(e.summary, e.person);
      const stickerSvg = sId ? `<svg class="event-sticker"><use href="#${sId}"/></svg>` : '<span></span>';
      if (e.person === '給料') {
        ev.innerHTML = `${stickerSvg}<span class="event-text"><span class="event-label">${escapeHtml(e.summary)}</span></span>`;
      } else {
        ev.innerHTML = `${stickerSvg}<span class="event-text"><span class="event-name">${e.person}</span><span class="event-label">${escapeHtml(e.summary)}</span></span>`;
      }
```

### Step 2.7: フィルターchipのactive時に小ステッカー(任意・YAGNI判定 → スキップ)

- [ ] **このステップは YAGNI でスキップ**

理由: chip の active 表示は既存の color toggle で十分。ステッカー追加は視覚ノイズ増加リスク。仕様書側でも「ボタンは現状維持」明記済み。

### Step 2.8: ビルドして検証

- [ ] **Run build**

```bash
python "C:\Users\tamah\Desktop\shift_calendar\build.py" "C:\Users\tamah\OneDrive\Desktop\【登別店】2026年6月シフト初稿  (version 1).xlsx"
```

Expected: `index.html (63件のイベント)` 正常終了

- [ ] **Run 差分計測**

```bash
cd "C:\Users\tamah\Desktop\shift_calendar"
git add -A
git diff --cached --stat
```

Expected: build.py +160/-50程度、合計200行以内

- [ ] **180行超過時は YAGNI でステッカー数を絞る**

ステッカー6種類のうち、優先順位:
1. `st-leaf`(休 - 最頻出)
2. `st-coin`(給料日)
3. `st-star`(A番)
4. `st-bubble`(会議)
5. `st-bag`(出店)
6. `st-pin`(custom予定 - 低頻度)

180行を超えそうなら6→4種に削減(pin/bubbleをスキップ)。

### Step 2.9: preview_eval で動作確認

- [ ] **preview を起動 or 既存サーバーへリロード**

(指示役が preview 起動・確認、サブエージェントはコミット後の検証はビルド成功+差分行数チェックのみで可)

期待:
```javascript
document.querySelectorAll('.event-sticker').length // > 30
document.querySelectorAll('.deco-cloud-1').length // === 1
document.querySelectorAll('.deco-leaf-1').length // === 1
```

### Step 2.10: コミット & プッシュ

- [ ] **Commit**

```bash
cd "C:\Users\tamah\Desktop\shift_calendar"
git commit -m "$(cat <<'EOF'
v7-C2: SVGステッカー6種+ヘッダー装飾

- 自作SVG: st-leaf(休), st-bubble(会議), st-bag(出店),
  st-star(A番), st-coin(給料日), st-pin(予定)
- 各イベントチップに 12x12 グリッドで左にステッカー配置
- ヘッダー右上に薄い雲、左下に小さな葉(opacity 0.3、装飾のみ)
- stickerId(summary, person) ヘルパー追加
- ev.innerHTML 構造を grid テンプレート対応に

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git push
```

---

## Self-Review

**Spec coverage:**
- ✅ Cozy Cream パレット移行 → Task 1
- ✅ 影と hairline 暖色化 → Task 1
- ✅ theme-color/manifest 更新 → Task 1
- ✅ body 背景グラデ色相 → Task 1
- ✅ SVGステッカー6種 → Task 2(st-leaf/st-bubble/st-bag/st-star/st-coin/st-pin)
- ✅ ヘッダー装飾(雲・葉)→ Task 2
- ✅ チップ grid レイアウト → Task 2
- ✅ stickerId 関数 → Task 2
- ✅ render() innerHTML 更新 → Task 2

**Placeholder scan:**
- TBD/TODO/"implement later" なし ✓
- 各ステップに完全なコード or コマンドあり ✓
- 「Similar to Task N」なし ✓

**Type consistency:**
- `stickerId(summary, person)` のシグネチャ Task 2 内で統一 ✓
- CSS クラス `.event-sticker` / `.event-text` 命名一貫 ✓
- SVG symbol id (`st-leaf` 等)プレフィックス統一 ✓
- 変数名(`--peach` / `--peach-deep` / `--sunshine`)Task 1 で定義、その後参照 ✓

---

## 実装の進め方

各タスクを完了するたびに:

1. ビルド成功確認(STDERR が openpyxl 警告だけ)
2. preview で視覚確認(指示役側で preview_eval 実行可)
3. `git diff --cached --stat` で行数閾値内確認(C1=150, C2=180)
4. ロールバック条件(180行超・build失敗・preview壊れ)に該当なし
5. コミット&プッシュ
6. 次タスクへ

すべて完了したら、変更要約をユーザーに報告。
