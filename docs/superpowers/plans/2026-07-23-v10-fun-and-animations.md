# v10 もっと楽しくなる+アニメ強化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** シフトカレンダーPWAに紙吹雪演出/月間サマリーカード/月別シーズンアクセントの3コアフィーチャーと8種のアニメーションを追加、v10として3コミットで配信する。

**Architecture:** すべて `build.py` の HTML テンプレ/CSS/JS 内編集。データモデル・Firestore は無変更。C1(F1+F2+B)/C2(F3+H+D)/C3(C+E+F+G) の3コミット。各アニメは `prefers-reduced-motion: reduce` で無効化可能。

**Tech Stack:** Python 3(build時) / HTML+CSS+JS(生成物)/CSS `@keyframes`+`requestAnimationFrame`

**前提コマンド:**
- ビルド: `python "C:\Users\tamah\Desktop\shift_calendar\build.py" "C:\Users\tamah\CrossDevice\Pixel 10\storage\Download\LINEWORKS\005036@kcsline\k\oneapp\r\jp1.10018843\10018843\v2-10018843-5398951346.390981933\【登別店】2026年6月シフト初稿  (version 1).xlsx"`
- 差分計測: `git diff --cached --stat`
- ロールバック: `git checkout build.py index.html manifest.json sw.js`
- プレビュー: `mcp__Claude_Preview__preview_start name=shift-cal` → 5432

---

## File Structure

すべて `C:\Users\tamah\Desktop\shift_calendar\build.py` の編集。

| セクション | 役割 | 行数目安 |
|---|---|---|
| CSS (`<style>` 内) | 各アニメの @keyframes / .month-summary / .season-* / .confetti | +150 |
| HTML(月ヘッダー) | サマリーカード HTML / 季節粒子 3枚 | +25 |
| JS(render 関連) | renderSummary / animateCount / seasonThemeFor | +40 |
| JS(refreshDaySheet) | confetti burst 呼び出し | +5 |
| JS(shift) | 月切替スライド transition | +15 |
| JS(cell tap) | ripple 挿入ハンドラ | +15 |

編集不可: `firebase-config.js`, `events.json`, `extract_events.py`, `sw.js`(自動生成)

---

## Task 1: C1 — 紙吹雪 + 月間サマリーカード + カウントアップ

**Phase:** C1(単一コミット)
**推定差分:** +90行

**Files:**
- Modify: `build.py` CSS の `</style>` 直前(サマリーCSS + 紙吹雪CSS)
- Modify: `build.py:1553` 付近(月ヘッダー内、`.filters` の直前にサマリーHTML)
- Modify: `build.py:2418` `render()` の頭で `renderSummary()` 呼び出し
- Modify: `build.py:2560` `refreshDaySheet()` 内、`isBothOff(builtin)` 分岐に `spawnConfetti()`
- Modify: `build.py:3170` `shift()` 直後に新規 helper 追加

### Step 1.1: CSS(サマリーカード + 紙吹雪 + カウント)を追加

- [ ] **Locate CSS の `</style>` 終端**

Run:
```bash
grep -n "^</style>" "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

- [ ] **`</style>` の直前に以下を挿入**

```css
/* v10 F2: 月間サマリーカード */
.month-summary {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
  padding: 8px 12px 12px;
}
.summary-card {
  background: var(--surface);
  border-radius: 12px;
  padding: 10px 8px;
  text-align: center;
  color: white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  position: relative;
  overflow: hidden;
}
.summary-card.k { background: linear-gradient(135deg, var(--kouki) 0%, var(--pond-dark) 110%); }
.summary-card.y { background: linear-gradient(135deg, var(--yui) 0%, var(--yui-meeting) 110%); }
.summary-card.both { background: linear-gradient(135deg, var(--leaf) 0%, var(--leaf-dark) 110%); }
.summary-title {
  font-size: 10px;
  font-weight: 800;
  opacity: 0.92;
  letter-spacing: 0.02em;
}
.summary-value {
  font-family: var(--font-en);
  font-size: 22px;
  font-weight: 900;
  line-height: 1;
  margin: 4px 0 2px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.15);
}
.summary-unit {
  font-size: 9.5px;
  font-weight: 700;
  opacity: 0.88;
}

/* v10 F1: 紙吹雪バースト */
.confetti-wrap {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 100vh;
  pointer-events: none;
  z-index: 9999;
  overflow: hidden;
}
.confetti-piece {
  position: absolute;
  top: -20px;
  width: 8px;
  height: 14px;
  border-radius: 2px;
  animation: conf-fall 1.5s cubic-bezier(0.55, 0.05, 0.6, 0.4) forwards;
  opacity: 0;
}
@keyframes conf-fall {
  0% { opacity: 0; transform: translateY(-20px) rotate(0deg); }
  15% { opacity: 1; }
  100% { opacity: 0; transform: translateY(110vh) rotate(720deg); }
}
@media (prefers-reduced-motion: reduce) {
  .confetti-piece { animation: none; opacity: 0; }
}
```

### Step 1.2: 月ヘッダーに サマリーHTML を追加

- [ ] **Locate `<div class="filters" role="group"`**

Run:
```bash
grep -n 'class="filters" role="group"' "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

Expected: 1553

- [ ] **`<div class="filters" ...>` の直前に挿入**

既存:
```html
    </button>
  </div>
  <div class="filters" role="group" aria-label="表示フィルター">
```

変更後(`</div>` と `<div class="filters"` の間に挿入):
```html
    </button>
  </div>
  <div class="month-summary" id="month-summary" aria-label="今月のサマリー">
    <div class="summary-card k">
      <div class="summary-title">こうき</div>
      <div class="summary-value" id="sum-k">0</div>
      <div class="summary-unit">出勤日</div>
    </div>
    <div class="summary-card y">
      <div class="summary-title">ゆい</div>
      <div class="summary-value" id="sum-y">0</div>
      <div class="summary-unit">出勤日</div>
    </div>
    <div class="summary-card both">
      <div class="summary-title">被り 💗</div>
      <div class="summary-value" id="sum-both">0</div>
      <div class="summary-unit">日</div>
    </div>
  </div>
  <div class="filters" role="group" aria-label="表示フィルター">
```

### Step 1.3: JS ヘルパー(集計 + カウントアップ + 紙吹雪)を追加

- [ ] **Locate `function shift(delta)`**

Run:
```bash
grep -n "^function shift(delta)" "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

Expected: 3170

- [ ] **`function shift(delta) { ... }` の**上**(shift 定義の直前)に以下を挿入**

```javascript
const OFF_LABELS = new Set(['休', '希望休', '有']);
function renderSummary() {
  const daysInMonth = new Date(viewYear, viewMonth + 1, 0).getDate();
  const kOff = new Set(), yOff = new Set();
  for (const [key, evs] of Object.entries(EVENTS)) {
    if (!key.startsWith(`${viewYear}-${String(viewMonth + 1).padStart(2, '0')}-`)) continue;
    for (const e of evs) {
      if (!OFF_LABELS.has(e.summary)) continue;
      if (e.person === 'こうき') kOff.add(key);
      else if (e.person === 'ゆい') yOff.add(key);
    }
  }
  const kWork = daysInMonth - kOff.size;
  const yWork = daysInMonth - yOff.size;
  let bothCount = 0;
  for (const k of kOff) if (yOff.has(k)) bothCount++;
  animateCount(document.getElementById('sum-k'), kWork);
  animateCount(document.getElementById('sum-y'), yWork);
  animateCount(document.getElementById('sum-both'), bothCount);
}

function animateCount(el, target) {
  if (!el) return;
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    el.textContent = target;
    return;
  }
  const start = parseInt(el.textContent, 10) || 0;
  const dur = 600;
  const t0 = performance.now();
  function step(t) {
    const p = Math.min(1, (t - t0) / dur);
    const eased = 1 - Math.pow(1 - p, 3);
    el.textContent = Math.round(start + (target - start) * eased);
    if (p < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

function spawnConfetti() {
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const wrap = document.createElement('div');
  wrap.className = 'confetti-wrap';
  wrap.setAttribute('aria-hidden', 'true');
  const colors = ['#F764A2', '#84CC16', '#FCD34D', '#88CDF6', '#B593D6'];
  for (let i = 0; i < 36; i++) {
    const p = document.createElement('div');
    p.className = 'confetti-piece';
    p.style.left = `${Math.random() * 100}%`;
    p.style.background = colors[i % colors.length];
    p.style.animationDelay = `${Math.random() * 0.3}s`;
    p.style.transform = `rotate(${Math.random() * 360}deg)`;
    wrap.appendChild(p);
  }
  document.body.appendChild(wrap);
  setTimeout(() => wrap.remove(), 1900);
}
```

### Step 1.4: render() 内で renderSummary() を呼ぶ

- [ ] **Locate `function render()`**

Run:
```bash
grep -n "^function render()" "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

Expected: 2418

- [ ] **`render()` の先頭近く(`month-num` 更新の直後)に呼び出しを追加**

既存:
```javascript
function render() {
  document.getElementById('year-label').textContent = `${viewYear}`;
  document.getElementById('month-num').textContent = `${viewMonth+1}`;
```

変更後:
```javascript
function render() {
  document.getElementById('year-label').textContent = `${viewYear}`;
  document.getElementById('month-num').textContent = `${viewMonth+1}`;
  renderSummary();
```

### Step 1.5: refreshDaySheet で紙吹雪を発火

- [ ] **Locate `if (isBothOff(builtin))` の分岐**

Run:
```bash
grep -n "if (isBothOff(builtin))" "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

- [ ] **既存の分岐内、`banner` 生成の直前に `spawnConfetti()` 呼び出しを追加**

既存(該当行付近):
```javascript
  if (isBothOff(builtin)) {
    const banner = document.createElement('div');
    banner.className = 'both-off-banner';
```

変更後:
```javascript
  if (isBothOff(builtin)) {
    spawnConfetti();
    const banner = document.createElement('div');
    banner.className = 'both-off-banner';
```

### Step 1.6: ビルド+検証+コミット

- [ ] **Run ビルド**

```bash
python "C:\Users\tamah\Desktop\shift_calendar\build.py" "C:\Users\tamah\CrossDevice\Pixel 10\storage\Download\LINEWORKS\005036@kcsline\k\oneapp\r\jp1.10018843\10018843\v2-10018843-5398951346.390981933\【登別店】2026年6月シフト初稿  (version 1).xlsx"
```

Expected: `index.html (107件のイベント)` 正常終了

- [ ] **Preview 起動 + サマリー要素検証**

Preview (`mcp__Claude_Preview__preview_start` name=shift-cal)、次に:
```javascript
document.querySelectorAll('.summary-card').length  // 3 を期待
document.getElementById('sum-k').textContent       // 数字(0でない)
document.getElementById('sum-both').textContent    // 数字
```

- [ ] **差分計測**

```bash
cd "C:\Users\tamah\Desktop\shift_calendar"
git add -A
git diff --cached --stat
```

Expected: build.py +90〜120行

- [ ] **Commit + push**

```bash
git commit -m "$(cat <<'EOF'
v10-C1: 紙吹雪+月間サマリーカード+カウントアップ

- 月ヘッダー下に3枚のサマリーカード追加(こうき/ゆい/被り 出勤日数)
- 月切替時にカウントアップアニメ(easeOutCubic 600ms)
- 二人ともお休みの日をタップすると紙吹雪36片が舞い降りる(1.9秒)
- prefers-reduced-motion で全アニメ無効化

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git push
```

---

## Task 2: C2 — シーズンアクセント + キラキラ粒子 + 月ヘッダー横スライド

**Phase:** C2(単一コミット)
**推定差分:** +80行

**Files:**
- Modify: `build.py` CSS(季節テーマ + キラキラ + スライド)
- Modify: `build.py:1532` 付近(`<header>` タグにキラキラ粒子3枚追加)
- Modify: `build.py:2418` `render()` に季節テーマ適用処理追加
- Modify: `build.py:3170` `shift(delta)` にスライド演出追加

### Step 2.1: CSS(季節テーマ+粒子+スライド)を追加

- [ ] **`</style>` の直前に以下を挿入**

```css
/* v10 F3: 月別シーズンアクセント */
header {
  transition: background 0.6s ease;
  position: relative;
  overflow: hidden;
}
.season-particle {
  position: absolute;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255,255,255,0.75) 0%, transparent 65%);
  pointer-events: none;
  animation: sparkle 2.6s ease-in-out infinite;
}
.season-particle.p1 { top: 22%; left: 15%; animation-delay: 0s; }
.season-particle.p2 { top: 58%; left: 78%; animation-delay: 0.9s; width: 14px; height: 14px; }
.season-particle.p3 { top: 40%; left: 92%; animation-delay: 1.7s; width: 22px; height: 22px; }
@keyframes sparkle {
  0%, 100% { opacity: 0; transform: scale(0.5); }
  50% { opacity: 0.85; transform: scale(1); }
}

/* v10 Anim D: 月ヘッダー横スライド */
.top-row.slide-out-left { animation: slideOutLeft 0.28s ease both; }
.top-row.slide-out-right { animation: slideOutRight 0.28s ease both; }
.top-row.slide-in-left { animation: slideInLeft 0.28s ease both; }
.top-row.slide-in-right { animation: slideInRight 0.28s ease both; }
@keyframes slideOutLeft  { to { opacity: 0; transform: translateX(-16px); } }
@keyframes slideOutRight { to { opacity: 0; transform: translateX(16px); } }
@keyframes slideInLeft   { from { opacity: 0; transform: translateX(16px); } }
@keyframes slideInRight  { from { opacity: 0; transform: translateX(-16px); } }

@media (prefers-reduced-motion: reduce) {
  header { transition: none; }
  .season-particle { animation: none; opacity: 0; }
  .top-row.slide-out-left,
  .top-row.slide-out-right,
  .top-row.slide-in-left,
  .top-row.slide-in-right { animation: none; }
}
```

### Step 2.2: header にキラキラ粒子3枚を追加

- [ ] **Locate `<div class="header-deco" aria-hidden="true">`**

Run:
```bash
grep -n 'class="header-deco"' "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

- [ ] **`header-deco` div 内の既存 SVG の後ろにキラキラ3枚を追加**

既存:
```html
  <div class="header-deco" aria-hidden="true">
    <svg class="deco-cloud-1"><use href="#deco-cloud"/></svg>
    <svg class="deco-leaf-1"><use href="#deco-leaf-small"/></svg>
  </div>
```

変更後:
```html
  <div class="header-deco" aria-hidden="true">
    <svg class="deco-cloud-1"><use href="#deco-cloud"/></svg>
    <svg class="deco-leaf-1"><use href="#deco-leaf-small"/></svg>
    <div class="season-particle p1"></div>
    <div class="season-particle p2"></div>
    <div class="season-particle p3"></div>
  </div>
```

### Step 2.3: SEASON_THEMES 定数と適用ロジックを追加

- [ ] **`renderSummary` の**下**、`spawnConfetti` の上(または renderSummary の直前)に SEASON_THEMES 定数を追加**

Run:
```bash
grep -n "^const OFF_LABELS" "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

- [ ] **`const OFF_LABELS = ...` の直前(または直後)に以下を挿入**

```javascript
const SEASON_THEMES = {
  1:  'linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%)',
  2:  'linear-gradient(135deg, #FEE7EF 0%, #FCE7F3 100%)',
  3:  'linear-gradient(135deg, #FEE7EF 0%, #FBCFE8 100%)',
  4:  'linear-gradient(135deg, #FFE4E1 0%, #FBCFE8 100%)',
  5:  'linear-gradient(135deg, #ECFCCB 0%, #D9F99D 100%)',
  6:  'linear-gradient(135deg, #DBEAFE 0%, #C7D2FE 100%)',
  7:  'linear-gradient(135deg, #FEF9C3 0%, #FEF3C7 100%)',
  8:  'linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%)',
  9:  'linear-gradient(135deg, #FEF3C7 0%, #FDBA74 100%)',
  10: 'linear-gradient(135deg, #FFE4E1 0%, #FED7AA 100%)',
  11: 'linear-gradient(135deg, #FEF3C7 0%, #FCD34D 100%)',
  12: 'linear-gradient(135deg, #DBEAFE 0%, #E0F2FE 100%)',
};
function applySeasonTheme() {
  const m = viewMonth + 1;
  const bg = SEASON_THEMES[m];
  if (bg) document.querySelector('header').style.background = bg;
}
```

### Step 2.4: render() で applySeasonTheme() を呼ぶ

- [ ] **`renderSummary();` の直後に `applySeasonTheme();` を追加**

既存(Step 1.4 で追加済み):
```javascript
function render() {
  document.getElementById('year-label').textContent = `${viewYear}`;
  document.getElementById('month-num').textContent = `${viewMonth+1}`;
  renderSummary();
```

変更後:
```javascript
function render() {
  document.getElementById('year-label').textContent = `${viewYear}`;
  document.getElementById('month-num').textContent = `${viewMonth+1}`;
  renderSummary();
  applySeasonTheme();
```

### Step 2.5: shift() にスライド演出を追加

- [ ] **`shift(delta)` を以下に置換**

既存:
```javascript
function shift(delta) {
  viewMonth += delta;
  if (viewMonth < 0) { viewMonth = 11; viewYear--; }
  if (viewMonth > 11) { viewMonth = 0; viewYear++; }
  render();
  saveLastView();
}
```

変更後:
```javascript
function shift(delta) {
  const reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const topRow = document.querySelector('.top-row');
  viewMonth += delta;
  if (viewMonth < 0) { viewMonth = 11; viewYear--; }
  if (viewMonth > 11) { viewMonth = 0; viewYear++; }
  if (!topRow || reduced) {
    render();
    saveLastView();
    return;
  }
  const outCls = delta > 0 ? 'slide-out-left' : 'slide-out-right';
  const inCls  = delta > 0 ? 'slide-in-right' : 'slide-in-left';
  topRow.classList.add(outCls);
  setTimeout(() => {
    render();
    saveLastView();
    topRow.classList.remove(outCls);
    topRow.classList.add(inCls);
    setTimeout(() => topRow.classList.remove(inCls), 300);
  }, 260);
}
```

### Step 2.6: ビルド+検証+コミット

- [ ] **Run ビルド + preview 検証**

```bash
python "C:\Users\tamah\Desktop\shift_calendar\build.py" "C:\Users\tamah\CrossDevice\Pixel 10\storage\Download\LINEWORKS\005036@kcsline\k\oneapp\r\jp1.10018843\10018843\v2-10018843-5398951346.390981933\【登別店】2026年6月シフト初稿  (version 1).xlsx"
```

Preview で以下確認:
```javascript
document.querySelectorAll('.season-particle').length  // 3
getComputedStyle(document.querySelector('header')).background.slice(0, 30)  // gradient含む
```

- [ ] **差分計測**

```bash
git add -A && git diff --cached --stat
```

Expected: build.py +70〜100行(累積 C1+C2 で 160〜220)

- [ ] **Commit + push**

```bash
git commit -m "$(cat <<'EOF'
v10-C2: 月別シーズンアクセント+キラキラ粒子+月ヘッダースライド

- 月ヘッダー背景に月別グラデ(桜4月/紫陽花6月/雪12月 etc.12種)
- キラキラ粒子3個が sparkle アニメで明滅
- 前月/次月切替で top-row が横スライド遷移(280ms)
- prefers-reduced-motion で全て無効化

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git push
```

---

## Task 3: C3 — 残りアニメ4種(cellRise / heartBeat / ripple / annivWiggle)

**Phase:** C3(単一コミット)
**推定差分:** +70行

**Files:**
- Modify: `build.py` CSS(4種の @keyframes + 適用クラス)
- Modify: `build.py:2418` `render()` 内のセル生成に `cell.classList.add('cell-rise')` と delay
- Modify: `build.py` 既存の cell click ハンドラに ripple 生成処理を追加

### Step 3.1: 4種のアニメ CSS を追加

- [ ] **`</style>` の直前に以下を挿入**

```css
/* v10 Anim C: セル順次登場 */
.cell.cell-rise {
  animation: cellRise 0.45s var(--ease-spring) both;
}
@keyframes cellRise {
  from { opacity: 0; transform: translateY(6px) scale(0.96); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

/* v10 Anim E: ヒーローハート鼓動 */
.hero-card .heart-beat {
  animation: heartBeat 2.2s ease-in-out infinite;
  transform-origin: center;
}
@keyframes heartBeat {
  0%, 60%, 100% { transform: scale(1); }
  70% { transform: scale(1.2); }
  80% { transform: scale(0.95); }
  90% { transform: scale(1.1); }
}

/* v10 Anim F: セルタップ波紋 */
.cell { position: relative; }
.cell-ripple {
  position: absolute;
  border-radius: 50%;
  background: rgba(247, 100, 162, 0.35);
  width: 20px;
  height: 20px;
  pointer-events: none;
  transform: translate(-50%, -50%) scale(0);
  animation: ripple 0.55s ease-out forwards;
  z-index: 1;
}
@keyframes ripple {
  from { transform: translate(-50%, -50%) scale(0); opacity: 0.55; }
  to   { transform: translate(-50%, -50%) scale(10); opacity: 0; }
}

/* v10 Anim G: 記念日くねくね */
.anniv-chip {
  animation: annivWiggle 4s ease-in-out infinite;
  transform-origin: center;
}
@keyframes annivWiggle {
  0%, 88%, 100% { transform: rotate(0); }
  90% { transform: rotate(-4deg); }
  94% { transform: rotate(3deg); }
  97% { transform: rotate(-1deg); }
}

@media (prefers-reduced-motion: reduce) {
  .cell.cell-rise,
  .hero-card .heart-beat,
  .cell-ripple,
  .anniv-chip { animation: none; }
}
```

### Step 3.2: render() でセルに cell-rise クラスと delay 適用

- [ ] **Locate セル生成の `cell.style.animationDelay = ...` 行**

Run:
```bash
grep -n "cell.style.animationDelay" "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

Expected: 2435

- [ ] **既存の `cell.style.animationDelay` 行の直後に `cell.classList.add('cell-rise')` を追加**

既存:
```javascript
    const cell = document.createElement('div');
    cell.className = 'cell';
    cell.style.animationDelay = `${Math.min(i * 18, 540)}ms`;
```

変更後:
```javascript
    const cell = document.createElement('div');
    cell.className = 'cell';
    cell.style.animationDelay = `${Math.min(i * 18, 540)}ms`;
    cell.classList.add('cell-rise');
```

### Step 3.3: ヒーローハートに heart-beat クラスを付ける

- [ ] **Locate ヒーローカードの heart SVG**

Run:
```bash
grep -n 'class="hero-heart"\|hero-card.*heart\|hero.*use href="#heart"' "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

- [ ] **見つかった SVG に `heart-beat` クラスを追加(既存 class があれば追記)**

例: `<svg class="hero-heart">` を `<svg class="hero-heart heart-beat">` に。
（もし該当 SVG が見つからなければ、`hero-card` 内の代表アイコン `<svg>` にクラス追加。ハート/ケーキ/星のいずれかで運用状況に応じる。）

### Step 3.4: セルタップ時に ripple 挿入

- [ ] **Locate セルクリックハンドラ**

`render()` 内のセル生成部で、既存の `cell.onclick` または `cell.addEventListener('click', ...)` を探す:

Run:
```bash
grep -n "cell.onclick\|cell.addEventListener" "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

- [ ] **既存 click ハンドラを wrap して ripple 生成を追加**

既存例(実装によりバリエーションあり):
```javascript
    cell.onclick = () => openDaySheet(key, y, m, d);
```

変更後:
```javascript
    cell.onclick = (ev) => {
      const rect = cell.getBoundingClientRect();
      if (!window.matchMedia || !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        const r = document.createElement('span');
        r.className = 'cell-ripple';
        r.style.left = `${ev.clientX - rect.left}px`;
        r.style.top = `${ev.clientY - rect.top}px`;
        cell.appendChild(r);
        setTimeout(() => r.remove(), 600);
      }
      openDaySheet(key, y, m, d);
    };
```

注意: セルの `overflow` は default だが、`.cell-ripple` が飛び出しても問題は無い(pointer-events none)。ただし他コンテンツと重ならないよう z-index: 1 を付けている。

### Step 3.5: ビルド+検証+コミット

- [ ] **Run ビルド + preview 検証**

```bash
python "C:\Users\tamah\Desktop\shift_calendar\build.py" "C:\Users\tamah\CrossDevice\Pixel 10\storage\Download\LINEWORKS\005036@kcsline\k\oneapp\r\jp1.10018843\10018843\v2-10018843-5398951346.390981933\【登別店】2026年6月シフト初稿  (version 1).xlsx"
```

Preview で:
```javascript
document.querySelectorAll('.cell.cell-rise').length  // 42程度
document.querySelectorAll('.anniv-chip').length      // 記念日登録済みならその数
```

- [ ] **差分計測**

```bash
git add -A && git diff --cached --stat
```

Expected: build.py +60〜90行(累積 v10全体で 230〜310)

- [ ] **150行超過ならロールバック指示**

単一コミットが 150行超なら:
```bash
git checkout build.py index.html manifest.json sw.js
```
→ Step 3.1 の CSS を減らす(annivWiggle/rippleの一方だけ残す等)。

- [ ] **Commit + push**

```bash
git commit -m "$(cat <<'EOF'
v10-C3: 残りアニメ4種(セル順次登場・ハート鼓動・波紋・記念日くねくね)

- 月切替時にセル群が波打つように出現(cellRise 45ms×index)
- ヒーローカードのハートが2.2秒間隔でドクン(heartBeat)
- セルタップ位置から円が広がる波紋(0.55秒)
- 記念日/誕生日/その他チップが4秒毎にくねっと揺れる
- prefers-reduced-motion で全アニメ無効

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git push
```

---

## Self-Review

**Spec coverage:**
- ✅ F1 紙吹雪 → Task 1 Step 1.1(CSS)+1.3(spawnConfetti)+1.5(発火)
- ✅ F2 月間サマリー → Task 1 Step 1.1(CSS)+1.2(HTML)+1.3(renderSummary)+1.4(呼び出し)
- ✅ F3 シーズン → Task 2 Step 2.1(CSS)+2.3(定数+applySeasonTheme)+2.4(呼び出し)
- ✅ Anim A 紙吹雪バースト → F1 と統合、Task 1
- ✅ Anim B カウントアップ → Task 1 Step 1.3 の `animateCount()`
- ✅ Anim C セル順次登場強化 → Task 3 Step 3.1(cellRise CSS)+3.2(class 付与)
- ✅ Anim D 月ヘッダースライド → Task 2 Step 2.1(CSS)+2.5(shift 内挙動)
- ✅ Anim E ヒーローハート鼓動 → Task 3 Step 3.1(heartBeat CSS)+3.3(class 付与)
- ✅ Anim F セルタップ波紋 → Task 3 Step 3.1(ripple CSS)+3.4(挿入JS)
- ✅ Anim G 記念日くねくね → Task 3 Step 3.1(annivWiggle CSS、`.anniv-chip` 自動適用)
- ✅ Anim H シーズン粒子 → Task 2 Step 2.1(CSS)+2.2(HTML 3枚追加)
- ✅ reduced-motion 対応 → 各 Task の CSS ブロック内で `@media (prefers-reduced-motion: reduce)` を付与

**Placeholder scan:**
- TBD/TODO なし
- 各ステップに完全コード/コマンド
- 「Similar to」なし

**Type consistency:**
- 関数名: `renderSummary`, `animateCount`, `spawnConfetti`, `applySeasonTheme` で統一
- CSS クラス: `.month-summary`, `.summary-card{k,y,both}`, `.confetti-wrap`, `.confetti-piece`, `.season-particle{p1,p2,p3}`, `.top-row.slide-{out,in}-{left,right}`, `.cell-rise`, `.heart-beat`, `.cell-ripple`, `.anniv-chip` で一貫
- 定数: `OFF_LABELS`(Task 1)、`SEASON_THEMES`(Task 2)で命名整合
- id: `sum-k`, `sum-y`, `sum-both`, `month-summary` で一貫

**未確認事項:**
- Step 3.3 のヒーローハート SVG の実際の class 属性は grep で確認して現状に合わせる必要あり。もし該当ハート SVG が hero-card 内で見つからない場合はスキップ可(アニメ E を YAGNI 化)。

---

## 実装の進め方

1. Task 1(C1) → build + preview → commit + push → GitHub Pages 反映確認(1-2分)
2. Task 2(C2) → build + preview → commit + push
3. Task 3(C3) → build + preview → commit + push

各コミット後に user 実機(iOS/Android)で見て確認できるサイクル。3つ全部完了で v10 完成。
