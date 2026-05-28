# v8 予定追加履歴シート Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ユーザー追加の custom events を別シートで時系列表示する「予定リスト」機能を追加する。

**Architecture:** 既存 sheet-overlay パターン踏襲。フィルター行に「履歴」ボタンを追加→`history-overlay` をボトムシート展開。`createdAt` フィールドを custom event に追加し、予定日昇順+今日マーカー区切りで描画。

**Tech Stack:** Python 3 (build時) / HTML+CSS+JS (生成物)

**前提コマンド:**
- ビルド: `python "C:\Users\tamah\Desktop\shift_calendar\build.py" "<xlsx>"`
  - xlsx の場所: `C:\Users\tamah\CrossDevice\Pixel 10\storage\Download\LINEWORKS\005036@kcsline\k\oneapp\r\jp1.10018843\10018843\v2-10018843-5398951346.390981933\【登別店】2026年6月シフト初稿  (version 1).xlsx`
- 差分計測: `git diff --cached --stat`
- ロールバック: `git checkout build.py index.html manifest.json sw.js`

---

## File Structure

すべて `C:\Users\tamah\Desktop\shift_calendar\build.py` 編集。生成物は自動更新、直接編集禁止。

| ファイル | 役割 | 変更可否 |
|---|---|---|
| `build.py` | テンプレ+定数+ロジック | ✅ |
| `index.html`/`manifest.json`/`sw.js` | 自動生成 | ❌ |
| `firebase-config.js`/`events.json`/`extract_events.py` | 別目的/設定 | ❌ |
| Firestore | events スキーマ後方互換拡張(`createdAt` optional) | 既存 |

---

## Task 1: createdAt フィールド追加 + 履歴シートHTML/CSS

**推定差分:** +80〜100行 / -2行

**Files:**
- Modify: `build.py:2548` 付近(`async function saveForm`)
- Modify: `build.py:1478` 付近(フィルター行に履歴ボタン)
- Modify: `build.py:1690` 付近(year-overlay 直後に history-overlay)
- Modify: `build.py` CSS の `</style>` 直前(履歴専用CSS)

### Step 1.1: saveForm に createdAt 保存

- [ ] **Locate `async function saveForm`**

Run:
```bash
grep -n "async function saveForm" "C:\Users\tamah\Desktop\shift_calendar\build.py"
```
Expected: 行 2548 付近

- [ ] **Read `saveForm` 全体を確認**

Run:
```
Read build.py offset=2548 limit=40
```

- [ ] **`saveForm` の event 作成行を `createdAt` 込みに置換**

既存(該当行を Read で確認、おそらく以下のような形):
```javascript
  const event = { date, type: formType, title, desc, start, end, reminderMin: formReminder };
  if (editingId) {
    await Storage.update(editingId, event);
  } else {
    await Storage.add(event);
  }
```

変更後:
```javascript
  let createdAt = Date.now();
  if (editingId) {
    const existing = allCustomEvents.find(e => e.id === editingId);
    if (existing && existing.createdAt) createdAt = existing.createdAt;
  }
  const event = { date, type: formType, title, desc, start, end, reminderMin: formReminder, createdAt };
  if (editingId) {
    await Storage.update(editingId, event);
  } else {
    await Storage.add(event);
  }
```

注意: 編集時は既存 `createdAt` を維持(なければ Date.now() で初期化)。

### Step 1.2: フィルター行に履歴ボタン追加

- [ ] **Locate year-btn**

Run:
```bash
grep -n 'id="year-btn"' "C:\Users\tamah\Desktop\shift_calendar\build.py"
```
Expected: 1478

- [ ] **year-btn 行の直後に履歴ボタン挿入**

既存 line 1478 を含む `<button class="chip" id="year-btn" ...>` 〜 `</button>` ブロックを Read で確認。その閉じタグ `</button>` の直後に1行追加:
```html
    <button class="chip" id="history-btn" type="button" aria-label="予定リスト" style="background:var(--surface);color:var(--text-2);border-color:var(--border);">
      <svg style="width:14px;height:14px;"><use href="#i-clock"/></svg>
      履歴
    </button>
```

### Step 1.3: history-overlay を year-overlay 直後に追加

- [ ] **Locate year-overlay 終端**

Run:
```bash
grep -n 'id="year-overlay"' "C:\Users\tamah\Desktop\shift_calendar\build.py"
```
Expected: 1690

- [ ] **year-overlay の閉じ `</div>` を Read で位置特定**

`Read build.py offset=1690 limit=30` で year-overlay 全体を読む。閉じ `</div></div>` を特定。

- [ ] **year-overlay の直後に history-overlay を挿入**

```html
<!-- History Sheet -->
<div class="sheet-overlay" id="history-overlay" role="dialog" aria-modal="true" aria-labelledby="history-title" aria-hidden="true">
  <div class="sheet" style="max-height: 92vh;">
    <div class="sheet-handle"></div>
    <div class="sheet-header">
      <div class="sheet-title" id="history-title">予定リスト</div>
      <button class="icon-btn" id="history-close" aria-label="閉じる">
        <svg><use href="#i-x"/></svg>
      </button>
    </div>
    <div class="history-counts" id="history-counts"></div>
    <div class="sheet-body" id="history-body"></div>
  </div>
</div>
```

### Step 1.4: 履歴専用CSSを追加

- [ ] **Locate CSS の `</style>` 終端**

Run:
```bash
grep -n "^</style>" "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

- [ ] **`</style>` の直前に履歴専用CSSを挿入**

```css
.history-section-title {
  font-size: 13px;
  font-weight: 800;
  color: var(--muted);
  letter-spacing: 0.06em;
  margin: 14px 0 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.history-divider {
  text-align: center;
  font-size: 11px;
  font-weight: 800;
  color: var(--cheek-deep);
  letter-spacing: 0.1em;
  padding: 12px 0;
  position: relative;
}
.history-divider::before,
.history-divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: calc(50% - 60px);
  height: 1px;
  background: var(--border);
}
.history-divider::before { left: 0; }
.history-divider::after { right: 0; }
.history-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: var(--surface-soft);
  border: 1px solid var(--border);
  border-radius: 14px;
  margin-bottom: 8px;
  transition: transform 0.15s var(--ease-spring);
  cursor: pointer;
}
.history-card:active { transform: scale(0.98); }
.history-card.past { opacity: 0.78; }
.history-card-body { flex: 1; min-width: 0; }
.history-card-meta {
  font-size: 11px;
  font-weight: 700;
  color: var(--muted);
  margin-top: 3px;
  display: flex;
  gap: 6px;
  align-items: center;
}
.history-card-date {
  font-family: var(--font-en);
  font-weight: 800;
  color: var(--text-2);
  font-size: 12px;
}
.history-card-title {
  font-size: 14px;
  font-weight: 800;
  color: var(--text);
  margin-top: 2px;
}
.history-card-time {
  font-family: var(--font-en);
  font-weight: 700;
  color: var(--muted);
  font-size: 12px;
  margin-left: 4px;
}
.history-empty {
  text-align: center;
  padding: 32px 16px;
  color: var(--muted);
  font-weight: 700;
}
.history-counts {
  font-size: 12px;
  font-weight: 700;
  color: var(--muted);
  padding: 6px 16px 8px;
  border-bottom: 1px solid var(--border);
}
```

### Step 1.5: ビルド+検証

- [ ] **Run ビルド**

```bash
python "C:\Users\tamah\Desktop\shift_calendar\build.py" "C:\Users\tamah\CrossDevice\Pixel 10\storage\Download\LINEWORKS\005036@kcsline\k\oneapp\r\jp1.10018843\10018843\v2-10018843-5398951346.390981933\【登別店】2026年6月シフト初稿  (version 1).xlsx"
```

Expected: 正常終了 + 63件 イベント

- [ ] **Run 差分計測**

```bash
cd "C:\Users\tamah\Desktop\shift_calendar"
git add -A
git diff --cached --stat
```

Expected: build.py +80〜110行(目標100以内)

### Step 1.6: コミット&プッシュ

- [ ] **Commit**

```bash
cd "C:\Users\tamah\Desktop\shift_calendar"
git commit -m "$(cat <<'EOF'
v8-1: 予定履歴シートの土台(createdAt+UI骨組み)

- saveForm に createdAt: Date.now() を追加(編集時は既存維持)
- フィルター行に「履歴」ボタン追加(年ボタンの隣)
- history-overlay の HTML 骨組み(空状態)
- 履歴専用CSS(.history-card, .history-divider, .history-empty 等)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git push
```

---

## Task 2: 履歴描画ロジック + Escape組込

**推定差分:** +90〜110行 / -1行

**Files:**
- Modify: `build.py:1939` 付近(`escapeHtml` の隣に `relativeTime` 追加)
- Modify: `build.py:2548` 付近(`saveForm` 関数の後に履歴ロジック挿入位置)
- Modify: `build.py:2902` 付近(Escape ハンドラに history を最上位として追加)
- Modify: `build.py` init() リスナー登録部に history-btn 用追加

### Step 2.1: relativeTime と getHistoryItems ヘルパー追加

- [ ] **Locate `function escapeHtml`**

Run:
```bash
grep -n "function escapeHtml" "C:\Users\tamah\Desktop\shift_calendar\build.py"
```
Expected: 1939

- [ ] **`escapeHtml` 関数の直後に2関数追加**

```javascript
function relativeTime(ms) {
  if (!ms) return '以前に追加';
  const diff = (Date.now() - ms) / 1000;
  if (diff < 0) return 'たった今追加';
  if (diff < 60) return 'たった今追加';
  if (diff < 3600) return `${Math.floor(diff/60)}分前に追加`;
  if (diff < 86400) return `${Math.floor(diff/3600)}時間前に追加`;
  if (diff < 604800) return `${Math.floor(diff/86400)}日前に追加`;
  if (diff < 2592000) return `${Math.floor(diff/604800)}週間前に追加`;
  return `${Math.floor(diff/2592000)}ヶ月前に追加`;
}
function getHistoryItems() {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const items = (allCustomEvents || [])
    .filter(e => e.type !== 'memo')
    .map(e => ({ ...e, _dateObj: new Date(e.date + 'T00:00:00') }))
    .sort((a, b) => a._dateObj - b._dateObj);
  const past = items.filter(e => e._dateObj < today);
  const future = items.filter(e => e._dateObj >= today);
  return { past, future, today };
}
```

### Step 2.2: openHistoryView / closeHistoryView / renderHistoryView 追加

- [ ] **Locate `function closeYearView`**

Run:
```bash
grep -n "function closeYearView" "C:\Users\tamah\Desktop\shift_calendar\build.py"
```
Expected: 2158

- [ ] **`closeYearView()` の閉じ `}` の直後に履歴ロジック関数群を追加**

```javascript
function openHistoryView() {
  renderHistoryView();
  document.getElementById('history-overlay').classList.add('open');
  document.getElementById('history-overlay').setAttribute('aria-hidden', 'false');
  if (typeof lockBodyScroll === 'function') lockBodyScroll('history-overlay');
}
function closeHistoryView() {
  document.getElementById('history-overlay').classList.remove('open');
  document.getElementById('history-overlay').setAttribute('aria-hidden', 'true');
  if (typeof releaseBodyScroll === 'function') releaseBodyScroll('history-overlay');
}
function renderHistoryView() {
  const { past, future, today } = getHistoryItems();
  const body = document.getElementById('history-body');
  const counts = document.getElementById('history-counts');
  counts.textContent = `過去 ${past.length}件 / 未来 ${future.length}件`;
  body.innerHTML = '';
  const personClass = (e) => PERSON_KEY[PERSON_FROM_KEY[e.type] || '予定'] || 'custom';
  const personLabel = (e) => PERSON_FROM_KEY[e.type] || '予定';
  if (past.length === 0 && future.length === 0) {
    const empty = document.createElement('div');
    empty.className = 'history-empty';
    empty.textContent = 'まだ追加された予定はありません';
    body.appendChild(empty);
    return;
  }
  const makeCard = (e, isPast) => {
    const wd = ['日','月','火','水','木','金','土'][e._dateObj.getDay()];
    const dStr = `${e._dateObj.getMonth()+1}/${e._dateObj.getDate()}(${wd})`;
    const cls = personClass(e);
    const time = (e.start && e.end) ? `<span class="history-card-time">${e.start}〜${e.end}</span>` : '';
    const card = document.createElement('div');
    card.className = 'history-card' + (isPast ? ' past' : '');
    card.innerHTML = `
      <div class="history-card-body">
        <div class="history-card-meta">
          <span class="person-tag ${cls}">${personLabel(e)}</span>
          <span class="history-card-date">${dStr}</span>
        </div>
        <div class="history-card-title">${escapeHtml(e.title || '(タイトルなし)')}${time}</div>
        <div class="history-card-meta">${relativeTime(e.createdAt)}${e.desc ? ' · ' + escapeHtml(e.desc.slice(0, 40)) : ''}</div>
      </div>
      <button class="row-icon" data-edit="${e.id}" aria-label="編集">
        <svg><use href="#i-edit"/></svg>
      </button>
    `;
    card.onclick = () => {
      closeHistoryView();
      const [y, m, d] = e.date.split('-').map(Number);
      viewYear = y; viewMonth = m - 1;
      render();
      setTimeout(() => openDaySheet(e.date, y, m - 1, d), 100);
    };
    card.querySelector('[data-edit]').onclick = (ev) => {
      ev.stopPropagation();
      closeHistoryView();
      setTimeout(() => openForm(e.id), 80);
    };
    return card;
  };
  if (past.length) {
    const title = document.createElement('div');
    title.className = 'history-section-title';
    title.textContent = '過去';
    body.appendChild(title);
    past.forEach(e => body.appendChild(makeCard(e, true)));
  }
  const todayBar = document.createElement('div');
  todayBar.className = 'history-divider';
  todayBar.textContent = `今日 ${today.getMonth()+1}/${today.getDate()}`;
  body.appendChild(todayBar);
  if (future.length) {
    const title = document.createElement('div');
    title.className = 'history-section-title';
    title.textContent = 'これから';
    body.appendChild(title);
    future.forEach(e => body.appendChild(makeCard(e, false)));
  }
}
```

### Step 2.3: init() に history リスナー登録

- [ ] **Locate init() の `year-btn` リスナー登録箇所**

Run:
```bash
grep -n "year-btn'\\)\\.onclick" "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

- [ ] **year-btn 周辺のリスナー群の直後に history-btn 用追加**

挿入する内容:
```javascript
  const histBtn = document.getElementById('history-btn');
  if (histBtn) histBtn.onclick = openHistoryView;
  const histClose = document.getElementById('history-close');
  if (histClose) histClose.onclick = closeHistoryView;
  document.getElementById('history-overlay').onclick = e => {
    if (e.target.id === 'history-overlay') closeHistoryView();
  };
```

### Step 2.4: Escape ハンドラに history を最上位として追加

- [ ] **Locate Escape ハンドラ**

Run:
```bash
grep -n "addEventListener\\('keydown'" "C:\Users\tamah\Desktop\shift_calendar\build.py"
```
Expected: 2902

- [ ] **Modify Escape ハンドラ**

既存:
```javascript
  document.addEventListener('keydown', (ev) => {
    if (ev.key !== 'Escape') return;
    if (document.getElementById('year-overlay').classList.contains('open')) { closeYearView(); return; }
    else if (document.getElementById('confirm-overlay').classList.contains('open')) { _resolveConfirm(false); return; }
    const top = topMostOpenSheet();
    if (top === 'form-overlay') closeForm();
    else if (top === 'settings-overlay') closeSettings();
    else if (top === 'day-overlay') closeDaySheet();
  });
```

変更後(history を最上位に追加):
```javascript
  document.addEventListener('keydown', (ev) => {
    if (ev.key !== 'Escape') return;
    if (document.getElementById('history-overlay').classList.contains('open')) { closeHistoryView(); return; }
    if (document.getElementById('year-overlay').classList.contains('open')) { closeYearView(); return; }
    else if (document.getElementById('confirm-overlay').classList.contains('open')) { _resolveConfirm(false); return; }
    const top = topMostOpenSheet();
    if (top === 'form-overlay') closeForm();
    else if (top === 'settings-overlay') closeSettings();
    else if (top === 'day-overlay') closeDaySheet();
  });
```

### Step 2.5: ビルド+検証

- [ ] **Run ビルド**

```bash
python "C:\Users\tamah\Desktop\shift_calendar\build.py" "C:\Users\tamah\CrossDevice\Pixel 10\storage\Download\LINEWORKS\005036@kcsline\k\oneapp\r\jp1.10018843\10018843\v2-10018843-5398951346.390981933\【登別店】2026年6月シフト初稿  (version 1).xlsx"
```

Expected: 正常終了 + 63件

- [ ] **Run 差分計測**

```bash
cd "C:\Users\tamah\Desktop\shift_calendar"
git add -A
git diff --cached --stat
```

Expected: build.py +90〜120行(目標110以内)

- [ ] **180行超過なら一部ロールバック**

renderHistoryView の中で `makeCard` 関数のテンプレを最小化、または `history-divider` セクションを削減して再実装。

### Step 2.6: 動作検証(preview_eval ベース)

これは指示役側で確認するので、subagent は実行不要。完了通知のみ。

期待する eval(指示役が後で実施):
```javascript
// historyボタンが存在
!!document.getElementById('history-btn')
// 履歴シートが存在
!!document.getElementById('history-overlay')
// 関数が定義済み
typeof openHistoryView === 'function'
```

### Step 2.7: コミット&プッシュ

- [ ] **Commit**

```bash
cd "C:\Users\tamah\Desktop\shift_calendar"
git commit -m "$(cat <<'EOF'
v8-2: 履歴シートの描画ロジック+Escape組込

- relativeTime(ms) と getHistoryItems() ヘルパー追加
- openHistoryView/closeHistoryView/renderHistoryView 関数群
- 過去/今日マーカー/未来のセクション分割、カードタップで day-overlay、編集アイコンで form-overlay
- メモ(type:'memo')は履歴から除外
- Escape ハンドラに history-overlay を最上位として追加
- init() に history-btn/close リスナー登録

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git push
```

---

## Self-Review

**Spec coverage:**
- ✅ createdAt フィールド追加 → Task 1 (Step 1.1)
- ✅ 履歴ボタン → Task 1 (Step 1.2)
- ✅ history-overlay HTML → Task 1 (Step 1.3)
- ✅ 履歴専用CSS → Task 1 (Step 1.4)
- ✅ relativeTime ヘルパー → Task 2 (Step 2.1)
- ✅ getHistoryItems ロジック → Task 2 (Step 2.1)
- ✅ open/close/render History 関数 → Task 2 (Step 2.2)
- ✅ メモ除外(`type !== 'memo'`) → Task 2 Step 2.1
- ✅ カードタップ→day-overlay → Task 2 Step 2.2
- ✅ 編集アイコン→form-overlay → Task 2 Step 2.2
- ✅ Escape ハンドラ拡張 → Task 2 Step 2.4

**Placeholder scan:**
- TBD/TODO なし
- 各ステップに完全なコード/コマンド
- 「Similar to」なし

**Type consistency:**
- `createdAt` 統一(Task 1 で導入、Task 2 で `relativeTime` 引数として使用)
- 関数名 `openHistoryView/closeHistoryView/renderHistoryView` 統一
- CSS クラス `.history-card/.history-card-meta/.history-card-date/...` 統一
- `getHistoryItems` の return shape `{past, future, today}` Task 2 内で一貫使用
- `PERSON_KEY/PERSON_FROM_KEY` は既存定数を参照(変更不要)
- `viewYear/viewMonth/openDaySheet/openForm` 既存関数の活用整合

---

## 実装の進め方

各タスク完了ごとに:
1. ビルド成功確認(63件)
2. `git diff --cached --stat` で行数閾値内(C1:~100, C2:~110)
3. ロールバック条件(180行超・build失敗・preview壊れ)に該当なし
4. コミット&プッシュ
5. 次タスクへ

両方完了後、指示役側で preview 起動 → history ボタンタップ → 履歴表示確認。
