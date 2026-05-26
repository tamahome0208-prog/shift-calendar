# シフトカレンダー v6 実装プラン

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 既存課題の修正(祝日多年・SWキー・confirm・ハプティック)とカップル文脈強化(記念日・1年前ふりかえり・年間ヒートマップ)を5コミットで実装する。

**Architecture:** すべての変更は `build.py` の TEMPLATE 文字列・HOLIDAYS_2026 定数・SW定数に対する追加/置換のみ。`python build.py <xlsx>` で `index.html`/`manifest.json`/`sw.js` が再生成される。各タスクは独立コミットで、150〜180行以内、ロールバック可能。新規 Firestore コレクション `anniversaries` のセキュリティルール更新は指示役が Claude in Chrome で手動。

**Tech Stack:** Python 3 (build時) / HTML+CSS+JS (生成物) / Firebase Firestore v10.13 / GitHub Pages

**前提コマンド:**
- ビルド: `python "C:\Users\tamah\Desktop\shift_calendar\build.py" "C:\Users\tamah\OneDrive\Desktop\【登別店】2026年6月シフト初稿  (version 1).xlsx"`
- 差分計測: `git diff --stat HEAD`
- ロールバック: `git checkout build.py index.html manifest.json sw.js`

---

## File Structure

すべての変更は単一ファイル `C:\Users\tamah\Desktop\shift_calendar\build.py` に対する Edit。`index.html`/`manifest.json`/`sw.js` はビルド時に自動生成されるため直接編集禁止。

| ファイル | 役割 | 変更可否 |
|---|---|---|
| `build.py` | HTMLテンプレ + 定数 + main() | ✅ 編集対象 |
| `index.html` | 生成物 | ❌ 直接編集禁止 |
| `manifest.json` | 生成物 | ❌ 同上 |
| `sw.js` | 生成物 | ❌ 同上 |
| `firebase-config.js` | API設定 | ❌ 触らない |
| `events.json` | 別目的データ | ❌ 触らない |
| `extract_events.py` | 別目的スクリプト | ❌ 触らない |

---

## Task 1: 祝日多年対応 + SWキャッシュ動的キー + ハプティック振動

**Phase:** A-1 + A-2 + A-3
**推定差分:** 75行
**コミット:** C1

**Files:**
- Modify: `build.py:1787` (HOLIDAYS.includes → HOLIDAYS_BY_YEAR 参照)
- Modify: `build.py:2369-2383` (SW定数 + キャッシュキー動的化)
- Modify: `build.py:2385-2390` (HOLIDAYS_2026 → HOLIDAYS_BY_YEAR)
- Modify: `build.py:2465` (html.replace 行)
- Modify: `build.py:1427` (const HOLIDAYS = → const HOLIDAYS_BY_YEAR =)
- Insert: JS新規関数 `haptic(pattern)`、3箇所で呼出

### Step 1.1: Python側 HOLIDAYS_2026 を辞書化

- [ ] **Replace `build.py:2385-2390` の HOLIDAYS_2026 リスト**

既存:
```python
HOLIDAYS_2026 = [
    "2026-01-01", "2026-01-12", "2026-02-11", "2026-02-23", "2026-03-20",
    "2026-04-29", "2026-05-03", "2026-05-04", "2026-05-05", "2026-05-06",
    "2026-07-20", "2026-08-11", "2026-09-21", "2026-09-23",
    "2026-10-12", "2026-11-03", "2026-11-23",
]
```

新規:
```python
HOLIDAYS_BY_YEAR = {
    2025: [
        "2025-01-01", "2025-01-13", "2025-02-11", "2025-02-23", "2025-02-24",
        "2025-03-20", "2025-04-29", "2025-05-03", "2025-05-04", "2025-05-05",
        "2025-05-06", "2025-07-21", "2025-08-11", "2025-09-15", "2025-09-23",
        "2025-10-13", "2025-11-03", "2025-11-23", "2025-11-24",
    ],
    2026: [
        "2026-01-01", "2026-01-12", "2026-02-11", "2026-02-23", "2026-03-20",
        "2026-04-29", "2026-05-03", "2026-05-04", "2026-05-05", "2026-05-06",
        "2026-07-20", "2026-08-11", "2026-09-21", "2026-09-23",
        "2026-10-12", "2026-11-03", "2026-11-23",
    ],
    2027: [
        "2027-01-01", "2027-01-11", "2027-02-11", "2027-02-23", "2027-03-21",
        "2027-03-22", "2027-04-29", "2027-05-03", "2027-05-04", "2027-05-05",
        "2027-07-19", "2027-08-11", "2027-09-20", "2027-09-23",
        "2027-10-11", "2027-11-03", "2027-11-23",
    ],
    2028: [
        "2028-01-01", "2028-01-10", "2028-02-11", "2028-02-23", "2028-03-20",
        "2028-04-29", "2028-05-03", "2028-05-04", "2028-05-05",
        "2028-07-17", "2028-08-11", "2028-09-18", "2028-09-22",
        "2028-10-09", "2028-11-03", "2028-11-23",
    ],
}
```

### Step 1.2: html.replace で辞書を渡す

- [ ] **Modify `build.py:2465`**

既存: `html = html.replace("__HOLIDAYS_JSON__", json.dumps(HOLIDAYS_2026))`
変更後: `html = html.replace("__HOLIDAYS_JSON__", json.dumps(HOLIDAYS_BY_YEAR))`

### Step 1.3: JS側 HOLIDAYS の参照を辞書対応に

- [ ] **Modify `build.py:1427`**

既存: `const HOLIDAYS = __HOLIDAYS_JSON__;`
変更後: `const HOLIDAYS_BY_YEAR = __HOLIDAYS_JSON__;`

- [ ] **Modify `build.py:1787`** (render内の祝日判定)

既存:
```javascript
    if (HOLIDAYS.includes(key)) num.classList.add('holiday');
```

変更後:
```javascript
    if ((HOLIDAYS_BY_YEAR[y] || []).includes(key)) num.classList.add('holiday');
```

注意: `y` は render() 内の現在処理中の年変数(セルごとに前月/翌月もカバー)。

### Step 1.4: SW キャッシュ動的キー化

- [ ] **Modify `build.py:2369-2383` の SW = """ ... """**

既存:
```python
SW = """const CACHE = 'shift-cal-v4';
self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(['./','./manifest.json'])));
});
```

変更後:
```python
SW = """const CACHE = 'shift-cal-__BUILD_TS__';
self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(['./','./index.html','./manifest.json','./icon.png'])));
});
```

(残りの addEventListener('activate') と ('fetch') は変更なし)

### Step 1.5: main() で BUILD_TS を埋める

- [ ] **Modify `build.py` main() の `with open(...sw.js...)` 行の直前**

既存:
```python
    with open(os.path.join(OUTPUT_DIR, "sw.js"), "w", encoding="utf-8") as f:
        f.write(SW)
```

変更後:
```python
    build_ts = _dt.datetime.now().strftime("%Y%m%d%H%M%S")
    sw_text = SW.replace("__BUILD_TS__", build_ts)
    with open(os.path.join(OUTPUT_DIR, "sw.js"), "w", encoding="utf-8") as f:
        f.write(sw_text)
```

### Step 1.6: ハプティック関数追加

- [ ] **Locate `build.py` 内の JS escapeHtml 関数定義箇所**

Run: `grep -n "function escapeHtml" build.py`
期待結果: 1500-1550 あたりに hit

- [ ] **Insert `haptic` 関数を escapeHtml の直前に追加**

挿入する内容:
```javascript
function haptic(pattern) {
  try { if (navigator.vibrate) navigator.vibrate(pattern); } catch {}
}
```

### Step 1.7: ハプティック呼び出しを3箇所に追加

- [ ] **A番チップタップ時(セル全体タップで開くシートに統合済みなのでセル onclick の前後)**

`render()` の `cell.onclick = () => openDaySheet(...)` を以下に置換(`build.py:1850` 付近):

既存:
```javascript
    cell.onclick = () => openDaySheet(key, y, m, d);
```

変更後:
```javascript
    cell.onclick = () => { haptic(15); openDaySheet(key, y, m, d); };
```

- [ ] **メモ保存ボタン (saveMemo関数か buildDateMemoCard内の保存処理) に追加**

Find via: `grep -n "saveCustom" build.py` で memo 保存ロジック箇所を特定し、保存後の `closeForm()`/`render()` 呼び出しの前に `haptic(15);` を追加。

- [ ] **削除確認(deleteForm)に追加**

`build.py:2103` の `if (!confirm(...)) return;` の前に1行:
```javascript
  haptic([40, 30, 40]);
```

注: confirm 自体は Task 2 で置換するので、Task 1 では先に振動だけ入れる。

### Step 1.8: ビルド+検証

- [ ] **Run ビルド**

```bash
python "C:\Users\tamah\Desktop\shift_calendar\build.py" "C:\Users\tamah\OneDrive\Desktop\【登別店】2026年6月シフト初稿  (version 1).xlsx"
```

Expected output: `index.html (63件のイベント)` と STDERR の openpyxl 警告のみ

- [ ] **Run sw.js の CACHE 行確認**

```bash
grep "CACHE" "C:\Users\tamah\Desktop\shift_calendar\sw.js"
```

Expected: `const CACHE = 'shift-cal-20260524XXXXXX';`(タイムスタンプ入り)

- [ ] **Run 差分計測**

```bash
cd "C:\Users\tamah\Desktop\shift_calendar" && git add -A && git diff --cached --stat
```

Expected: build.py + index.html + sw.js 計 ~150行(build.pyだけだと75行)

### Step 1.9: コミット

- [ ] **Commit**

```bash
cd "C:\Users\tamah\Desktop\shift_calendar"
git commit -m "$(cat <<'EOF'
auto: 祝日多年対応+SWキャッシュ動的キー+ハプティック振動

- HOLIDAYS_2026 → HOLIDAYS_BY_YEAR (2025/2026/2027/2028内蔵)
- SW CACHE名にビルドタイムスタンプ埋込、precacheに index.html/icon.png追加
- haptic(pattern) ユーティリティ追加、3箇所で振動(セルタップ/メモ保存/削除確認)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git push
```

---

## Task 2: confirm() 置換: カスタム確認シート

**Phase:** A-4
**推定差分:** 80行
**コミット:** C2

**Files:**
- Modify: `build.py` HTML(新規 confirm-overlay 追加)
- Modify: `build.py` CSS(.confirm-sheet スタイル追加)
- Modify: `build.py` JS(`showConfirm()` 関数追加、`deleteForm()` 置換)

### Step 2.1: HTMLに confirm-overlay 追加

- [ ] **Locate `<div class="sheet-overlay" id="settings-overlay">` の直後**

Run: `grep -n 'id="settings-overlay"' build.py` で位置を確認

- [ ] **Insert 新規 sheet-overlay**

`settings-overlay` div の閉じ `</div></div>` 直後に追加:
```html
<!-- Confirm Sheet -->
<div class="sheet-overlay" id="confirm-overlay" role="dialog" aria-modal="true" aria-labelledby="confirm-title">
  <div class="sheet" style="max-height: auto;">
    <div class="sheet-handle"></div>
    <div class="sheet-header">
      <div class="sheet-title" id="confirm-title">確認</div>
    </div>
    <div class="sheet-body">
      <p id="confirm-message" style="font-size:15px;font-weight:600;color:var(--text-2);line-height:1.6;padding:8px 0;"></p>
    </div>
    <div class="sheet-footer">
      <div class="btn-row">
        <button class="btn btn-secondary" id="confirm-cancel">キャンセル</button>
        <button class="btn btn-danger" id="confirm-ok">削除する</button>
      </div>
    </div>
  </div>
</div>
```

### Step 2.2: showConfirm JS関数追加

- [ ] **Locate `function deleteForm()` の直前**

Run: `grep -n "function deleteForm" build.py` で位置確認(~2100行付近)

- [ ] **Insert showConfirm 関数**

`deleteForm()` 定義の直前に追加:
```javascript
let _confirmResolver = null;
function showConfirm(title, message, okLabel) {
  return new Promise((resolve) => {
    document.getElementById('confirm-title').textContent = title;
    document.getElementById('confirm-message').textContent = message;
    document.getElementById('confirm-ok').textContent = okLabel || '削除する';
    _confirmResolver = resolve;
    document.getElementById('confirm-overlay').classList.add('open');
    lockBodyScroll('confirm-overlay');
  });
}
function _resolveConfirm(ok) {
  document.getElementById('confirm-overlay').classList.remove('open');
  releaseBodyScroll('confirm-overlay');
  if (_confirmResolver) { _confirmResolver(ok); _confirmResolver = null; }
}
```

### Step 2.3: deleteForm を await ベースに

- [ ] **Modify `deleteForm()` 関数(`build.py:2100付近`)**

既存:
```javascript
function deleteForm() {
  if (!editingId) return;
  haptic([40, 30, 40]);
  if (!confirm('この予定を削除します。よろしいですか?')) return;
  // ...残りの処理
}
```

変更後:
```javascript
async function deleteForm() {
  if (!editingId) return;
  haptic([40, 30, 40]);
  const ok = await showConfirm('予定を削除', 'この予定を削除します。よろしいですか?', '削除する');
  if (!ok) return;
  // ...残りの処理(変更なし)
}
```

注意: 関数を async に変更。呼び出し元(f-delete onclick)は既に await 互換なら OK、そうでなければ `.then()` で対応。

### Step 2.4: init() で confirm ボタンのリスナー登録

- [ ] **Modify `init()` 関数末尾(`scheduleReminders()` 呼出前)**

挿入:
```javascript
  document.getElementById('confirm-ok').onclick = () => _resolveConfirm(true);
  document.getElementById('confirm-cancel').onclick = () => _resolveConfirm(false);
  document.getElementById('confirm-overlay').onclick = e => {
    if (e.target.id === 'confirm-overlay') _resolveConfirm(false);
  };
```

### Step 2.5: Escape ハンドラを confirm にも対応

- [ ] **Find `keydown` リスナー(Escape処理)`**

Run: `grep -n "Escape" build.py` で位置確認

- [ ] **既存の Escape チェーンに confirm を加える**

優先順: confirm > form > settings > day(confirmは一番手前)

既存例:
```javascript
document.addEventListener('keydown', e => {
  if (e.key !== 'Escape') return;
  if (document.getElementById('form-overlay').classList.contains('open')) closeForm();
  else if (document.getElementById('settings-overlay').classList.contains('open')) closeSettings();
  else if (document.getElementById('day-overlay').classList.contains('open')) closeDaySheet();
});
```

変更後(冒頭にconfirmチェック追加):
```javascript
document.addEventListener('keydown', e => {
  if (e.key !== 'Escape') return;
  if (document.getElementById('confirm-overlay').classList.contains('open')) _resolveConfirm(false);
  else if (document.getElementById('form-overlay').classList.contains('open')) closeForm();
  else if (document.getElementById('settings-overlay').classList.contains('open')) closeSettings();
  else if (document.getElementById('day-overlay').classList.contains('open')) closeDaySheet();
});
```

### Step 2.6: ビルド+検証+コミット

- [ ] **Run ビルド**

```bash
python "C:\Users\tamah\Desktop\shift_calendar\build.py" "C:\Users\tamah\OneDrive\Desktop\【登別店】2026年6月シフト初稿  (version 1).xlsx"
```

Expected: 正常終了

- [ ] **Run 差分計測**

```bash
cd "C:\Users\tamah\Desktop\shift_calendar" && git add -A && git diff --cached --stat
```

Expected: build.py が +60〜90行(目標80)以内

- [ ] **Commit**

```bash
git commit -m "$(cat <<'EOF'
auto: confirm()置換 - ケロッピー風カスタム確認シート

- showConfirm(title, message, okLabel) Promise返却型
- 既存sheet-overlay構造再利用、deleteFormで利用
- Escape keyでもキャンセル可能
- ブラウザ標準UIを排し世界観統一

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git push
```

---

## Task 3: 記念日カウントダウン

**Phase:** B-1
**推定差分:** 120行
**コミット:** C3

**Files:**
- Modify: `build.py` Storage クラスに anniversaries 対応追加
- Modify: `build.py` CSS(.anniv-list, .anniv-row, .anniv-add スタイル)
- Modify: `build.py` settings sheet に「記念日」セクション追加
- Modify: `build.py` renderHero() に記念日表示ロジック追加

### Step 3.1: localStorage キー定数追加

- [ ] **Locate `const LS_WEATHER` 行**

Run: `grep -n "const LS_WEATHER" build.py`

- [ ] **追加で LS_ANNIV 定数を入れる**

`const LS_WEATHER = ...;` の直後に追加:
```javascript
const LS_ANNIV = 'shift-cal-anniversaries-v1';
let allAnniversaries = [];
```

### Step 3.2: Storage クラス拡張

- [ ] **Locate `Storage = {` の `events()` メソッド付近**

Run: `grep -n "^const Storage = {" build.py`

- [ ] **Storage 内に anniversaries 用メソッドを追加**

`Storage` オブジェクトに新規メソッド追加(既存の `add`/`update`/`remove` の隣):
```javascript
  anniversaries() { return allAnniversaries; },
  async addAnniv(a) {
    if (firestoreDb) {
      await this._addDoc(collection(firestoreDb, 'anniversaries'), a);
    } else {
      const item = { id: uid(), ...a };
      allAnniversaries.push(item);
      try { localStorage.setItem(LS_ANNIV, JSON.stringify(allAnniversaries)); } catch {}
      renderSettingsAnniv();
      render();
    }
  },
  async removeAnniv(id) {
    if (firestoreDb) {
      await this._deleteDoc(this._doc(firestoreDb, 'anniversaries', id));
    } else {
      allAnniversaries = allAnniversaries.filter(a => a.id !== id);
      try { localStorage.setItem(LS_ANNIV, JSON.stringify(allAnniversaries)); } catch {}
      renderSettingsAnniv();
      render();
    }
  },
```

注意: Firestoreモードでは onSnapshot listener 追加が必要(次ステップ)。

### Step 3.3: initFirebase に anniv リスナー追加

- [ ] **Locate `initFirebase` メソッド内の `unsubscribe = onSnapshot(`**

Run: `grep -n "onSnapshot(this._coll" build.py`

- [ ] **events の onSnapshot 直後に anniv onSnapshot 追加**

既存:
```javascript
    unsubscribe = onSnapshot(this._coll, snap => {
      allCustomEvents = snap.docs.map(d => ({ id: d.id, ...d.data() }));
      ...
    });
```

変更後(直後に追加):
```javascript
    this._collAnniv = collection(firestoreDb, 'anniversaries');
    unsubscribeAnniv = onSnapshot(this._collAnniv, snap => {
      allAnniversaries = snap.docs.map(d => ({ id: d.id, ...d.data() }));
      try { localStorage.setItem(LS_ANNIV, JSON.stringify(allAnniversaries)); } catch {}
      renderSettingsAnniv();
      render();
    });
```

`let unsubscribe = null;` の隣に `let unsubscribeAnniv = null;` も追加。

### Step 3.4: initLocal で anniv 読込

- [ ] **Locate `initLocal()` メソッド**

- [ ] **Anniv のローカル読込を追加**

既存 `initLocal()`:
```javascript
  initLocal() {
    setSync('offline');
    try { allCustomEvents = JSON.parse(localStorage.getItem(LS_CUSTOM) || '[]'); }
    catch { allCustomEvents = []; }
    render();
  },
```

変更後:
```javascript
  initLocal() {
    setSync('offline');
    try { allCustomEvents = JSON.parse(localStorage.getItem(LS_CUSTOM) || '[]'); }
    catch { allCustomEvents = []; }
    try { allAnniversaries = JSON.parse(localStorage.getItem(LS_ANNIV) || '[]'); }
    catch { allAnniversaries = []; }
    render();
  },
```

### Step 3.5: 設定シートに記念日セクションのHTML追加

- [ ] **Locate Settings sheet の HTML(`id="settings-overlay"`)**

Run: `grep -n 'id="settings-overlay"' build.py`

- [ ] **既存のFirebase config field と Notification field の間に anniv セクション挿入**

挿入する内容(`<div class="field"> ... 通知 ...` の前):
```html
      <div class="field">
        <label style="display:flex;align-items:center;gap:6px;">記念日(最大3件)</label>
        <div id="anniv-list" class="anniv-list"></div>
        <div id="anniv-add-area">
          <button class="btn btn-secondary" id="anniv-add-toggle" style="font-size:13px;padding:10px;">+ 追加</button>
        </div>
        <div id="anniv-add-form" style="display:none; margin-top:8px;">
          <input type="text" id="anniv-name" placeholder="例: 付き合った日" style="width:100%;padding:10px;border-radius:10px;border:1.5px solid var(--border);font-size:14px;margin-bottom:6px;">
          <div style="display:flex;gap:6px;">
            <input type="number" id="anniv-month" min="1" max="12" placeholder="月" style="flex:1;padding:10px;border-radius:10px;border:1.5px solid var(--border);font-size:14px;">
            <input type="number" id="anniv-day" min="1" max="31" placeholder="日" style="flex:1;padding:10px;border-radius:10px;border:1.5px solid var(--border);font-size:14px;">
            <button class="btn btn-primary" id="anniv-save" style="flex:1;font-size:13px;padding:10px;">保存</button>
          </div>
        </div>
      </div>
```

### Step 3.6: CSS 追加

- [ ] **Locate CSS の最後の `</style>` 直前**

- [ ] **Anniv 専用 CSS 追加**

```css
.anniv-list { display: flex; flex-direction: column; gap: 6px; margin-bottom: 8px; }
.anniv-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: var(--surface-soft);
  border: 1px solid var(--border);
  border-radius: 12px;
  font-size: 13px;
  font-weight: 700;
}
.anniv-row .anniv-name { flex: 1; color: var(--text); }
.anniv-row .anniv-date { font-family: var(--font-en); color: var(--cheek-deep); font-weight: 800; }
.anniv-row .anniv-del {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--muted);
  font-size: 14px;
  cursor: pointer;
}
.anniv-row .anniv-del:active { transform: scale(0.92); }
```

### Step 3.7: renderSettingsAnniv 関数追加

- [ ] **Locate `function openSettings`**

- [ ] **renderSettingsAnniv 関数を openSettings の直前に追加**

```javascript
function renderSettingsAnniv() {
  const list = document.getElementById('anniv-list');
  if (!list) return;
  list.innerHTML = '';
  const annivs = allAnniversaries;
  annivs.forEach(a => {
    const row = document.createElement('div');
    row.className = 'anniv-row';
    row.innerHTML = `
      <span class="anniv-name">${escapeHtml(a.name)}</span>
      <span class="anniv-date">${a.month}/${a.day}</span>
      <button class="anniv-del" data-id="${a.id}" aria-label="削除">×</button>
    `;
    list.appendChild(row);
  });
  list.querySelectorAll('[data-id]').forEach(b => {
    b.onclick = () => Storage.removeAnniv(b.dataset.id);
  });
  // 3件達したら追加ボタン非表示
  const addBtn = document.getElementById('anniv-add-toggle');
  if (addBtn) addBtn.style.display = annivs.length >= 3 ? 'none' : 'inline-flex';
}
```

### Step 3.8: 追加フォーム制御を init() に追加

- [ ] **init() 末尾近く(他の onclick 設定群の隣)に追加**

```javascript
  const annivToggle = document.getElementById('anniv-add-toggle');
  if (annivToggle) annivToggle.onclick = () => {
    document.getElementById('anniv-add-form').style.display = 'block';
    annivToggle.style.display = 'none';
  };
  const annivSave = document.getElementById('anniv-save');
  if (annivSave) annivSave.onclick = async () => {
    const name = document.getElementById('anniv-name').value.trim();
    const month = parseInt(document.getElementById('anniv-month').value, 10);
    const day = parseInt(document.getElementById('anniv-day').value, 10);
    if (!name || !month || !day || month < 1 || month > 12 || day < 1 || day > 31) return;
    await Storage.addAnniv({ name, month, day });
    document.getElementById('anniv-name').value = '';
    document.getElementById('anniv-month').value = '';
    document.getElementById('anniv-day').value = '';
    document.getElementById('anniv-add-form').style.display = 'none';
  };
```

### Step 3.9: openSettings で記念日リスト描画

- [ ] **`function openSettings()` の最後に1行追加**

既存末尾: `document.getElementById('settings-overlay').classList.add('open');`
直前に追加: `renderSettingsAnniv();`

### Step 3.10: renderHero に記念日表示追加

- [ ] **Locate `function renderHero()` の statusMsg 設定箇所**

Run: `grep -n "let statusMsg" build.py`

- [ ] **statusMsg 決定ロジックに記念日チェック追加**

既存の `else if (nextDate && nextDate.days > 0 && nextDate.days <= 7)` の前に追加:
```javascript
  // 30日以内の記念日があれば優先表示
  if (statusMsg === '今日もおつかれさま' && !hot) {
    const todayMD = (today.getMonth()+1) * 100 + today.getDate();
    let nextAnniv = null;
    for (const a of allAnniversaries) {
      const annivThisYear = new Date(today.getFullYear(), a.month - 1, a.day);
      let target = annivThisYear;
      if (target < today) target = new Date(today.getFullYear() + 1, a.month - 1, a.day);
      const daysAway = Math.floor((target - today) / 86400000);
      if (daysAway >= 0 && daysAway <= 30 && (!nextAnniv || daysAway < nextAnniv.days)) {
        nextAnniv = { name: a.name, days: daysAway };
      }
    }
    if (nextAnniv) {
      if (nextAnniv.days === 0) {
        statusMsg = `今日は ${nextAnniv.name}`;
        hot = true;
        haptic([20, 40, 20, 40, 20]);
      } else {
        statusMsg = `あと ${nextAnniv.days} 日で ${nextAnniv.name}`;
      }
    }
  }
```

### Step 3.11: ビルド+検証+コミット

- [ ] **Run ビルド**

```bash
python "C:\Users\tamah\Desktop\shift_calendar\build.py" "C:\Users\tamah\OneDrive\Desktop\【登別店】2026年6月シフト初稿  (version 1).xlsx"
```

- [ ] **Run 差分計測**

```bash
cd "C:\Users\tamah\Desktop\shift_calendar" && git add -A && git diff --cached --stat
```

Expected: build.py +110〜140行

- [ ] **Commit**

```bash
git commit -m "$(cat <<'EOF'
feat: 記念日カウントダウン機能追加

- 最大3件の記念日(付き合った日・誕生日等)を登録可能
- Firestore anniversaries collection で2人同期
- 30日以内の到来日をヒーローカードに表示「あとXX日で○○」
- 当日はhot強調+haptic振動
- 設定シートに追加/削除UI、3件達したら追加ボタン隠れる

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git push
```

注意: コミット後、指示役が Firestore セキュリティルールに `anniversaries` 許可を追加する必要あり(別工程・Claude in Chrome)。

---

## Task 4: 1年前の今日(ふりかえり)

**Phase:** B-2
**推定差分:** 70行
**コミット:** C4

**Files:**
- Modify: `build.py` HTML(Recallカード追加)
- Modify: `build.py` CSS
- Modify: `build.py` JS(renderRecall 関数追加、render から呼出)

### Step 4.1: HTML に Recall カード追加

- [ ] **Locate hero-card section**

Run: `grep -n 'id="hero-card"' build.py`

- [ ] **hero-card </section> の直後に Recall カード挿入**

```html
<section class="recall-card" id="recall-card" hidden>
  <button class="recall-header" id="recall-toggle" type="button" aria-expanded="false">
    <span class="recall-label">ふりかえり</span>
    <span class="recall-count" id="recall-count">0</span>
    <svg class="recall-chevron" viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/></svg>
  </button>
  <div class="recall-body" id="recall-body" hidden></div>
</section>
```

### Step 4.2: CSS 追加

- [ ] **CSS の </style> 直前に追加**

```css
.recall-card {
  margin: 6px 14px 6px;
  background: var(--surface);
  border: 1px solid var(--hairline);
  border-radius: 18px;
  overflow: hidden;
  box-shadow: var(--shadow-xs);
}
.recall-header {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 12px 16px;
  background: transparent;
  border: none;
  cursor: pointer;
  font-family: inherit;
  text-align: left;
}
.recall-header:active { background: var(--surface-soft); }
.recall-label {
  flex: 1;
  font-size: 13px;
  font-weight: 800;
  color: var(--text-2);
  letter-spacing: 0.04em;
}
.recall-count {
  font-family: var(--font-en);
  font-size: 11px;
  font-weight: 800;
  padding: 2px 8px;
  background: var(--cheek);
  color: white;
  border-radius: 999px;
  letter-spacing: 0;
}
.recall-chevron {
  width: 16px;
  height: 16px;
  color: var(--muted);
  transition: transform 0.2s var(--ease-out);
}
.recall-header[aria-expanded="true"] .recall-chevron { transform: rotate(180deg); }
.recall-body {
  padding: 0 16px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.recall-item {
  padding: 10px 12px;
  background: var(--surface-soft);
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-2);
  line-height: 1.5;
}
.recall-item-when {
  font-family: var(--font-en);
  font-size: 11px;
  font-weight: 800;
  color: var(--muted);
  letter-spacing: 0.06em;
  margin-bottom: 4px;
  display: block;
}
```

### Step 4.3: renderRecall 関数追加

- [ ] **Locate `function renderHero()`**

- [ ] **renderHero の直後に renderRecall 関数追加**

```javascript
function renderRecall() {
  const today = new Date();
  const card = document.getElementById('recall-card');
  const body = document.getElementById('recall-body');
  const countEl = document.getElementById('recall-count');
  if (!card) return;
  const targets = [
    { years: 1, label: '1年前の今日' },
    { months: 1, label: '先月の今日' },
  ];
  const items = [];
  for (const t of targets) {
    const d = new Date(today);
    if (t.years) d.setFullYear(d.getFullYear() - t.years);
    if (t.months) d.setMonth(d.getMonth() - t.months);
    const key = dateKey(d.getFullYear(), d.getMonth(), d.getDate());
    const builtin = EVENTS[key] || [];
    const customForKey = allCustomEvents.filter(e => e.date === key);
    const memoRec = customForKey.find(e => e.type === 'memo');
    const bothOff = isBothOff(builtin);
    if (bothOff || (memoRec && (memoRec.memo || memoRec.stamp)) || customForKey.length > 0) {
      let txt = bothOff ? '二人ともお休みでした' : '';
      if (memoRec && memoRec.memo) txt += (txt ? ' / ' : '') + memoRec.memo.slice(0, 40);
      if (!txt && customForKey.length > 0) txt = customForKey[0].title || '予定あり';
      items.push({ when: t.label, key, txt });
    }
  }
  if (items.length === 0) {
    card.hidden = true;
    return;
  }
  card.hidden = false;
  countEl.textContent = items.length;
  body.innerHTML = '';
  items.forEach(it => {
    const el = document.createElement('div');
    el.className = 'recall-item';
    el.innerHTML = `<span class="recall-item-when">${it.when}</span>${escapeHtml(it.txt)}`;
    body.appendChild(el);
  });
}
```

### Step 4.4: トグル動作を init() に追加

- [ ] **init() 末尾に追加**

```javascript
  const recallToggle = document.getElementById('recall-toggle');
  if (recallToggle) recallToggle.onclick = () => {
    const expanded = recallToggle.getAttribute('aria-expanded') === 'true';
    recallToggle.setAttribute('aria-expanded', String(!expanded));
    document.getElementById('recall-body').hidden = expanded;
  };
```

### Step 4.5: render() からの呼出追加

- [ ] **Locate `renderHero();` の呼出箇所**

Run: `grep -n "renderHero();" build.py`

- [ ] **renderHero() の直後に追加**

既存:
```javascript
  renderHero();
}
```

変更後:
```javascript
  renderHero();
  renderRecall();
}
```

### Step 4.6: ビルド+検証+コミット

- [ ] **Run ビルド+差分計測**

```bash
python "C:\Users\tamah\Desktop\shift_calendar\build.py" "C:\Users\tamah\OneDrive\Desktop\【登別店】2026年6月シフト初稿  (version 1).xlsx"
cd "C:\Users\tamah\Desktop\shift_calendar"
git add -A
git diff --cached --stat
```

Expected: build.py +60〜85行

- [ ] **Commit**

```bash
git commit -m "$(cat <<'EOF'
feat: ふりかえりカード - 1年前/先月の今日

- カレンダー上部に折り畳み式 Recallカード追加
- 1年前の今日 / 先月の今日に該当データ(両方休み/メモ/予定)があれば表示
- 該当0件なら非表示(無音)
- 件数バッジ + シェブロン展開/折り畳み

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git push
```

---

## Task 5: 年間ヒートマップビュー

**Phase:** B-3
**推定差分:** 180行(警戒、超過時は分割)
**コミット:** C5(必要なら C5a/C5b に分割)

**Files:**
- Modify: `build.py` Header に「年」ボタン追加(SVGアイコン)
- Modify: `build.py` 新規 sheet-overlay (year-overlay) 追加
- Modify: `build.py` CSS(.year-grid, .year-cell, .year-month-row スタイル)
- Modify: `build.py` JS(renderYearView 関数、jumpToDate ヘルパー)

### Step 5.1: グリッドアイコンSVG追加

- [ ] **Locate SVG sprite defs(`<symbol id="i-settings"` 付近)**

Run: `grep -n 'symbol id="i-settings"' build.py`

- [ ] **i-grid symbol を追加(`<symbol id="i-settings">` の直前)**

```html
    <symbol id="i-grid" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="2" fill="none"/><rect x="14" y="3" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="2" fill="none"/><rect x="3" y="14" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="2" fill="none"/><rect x="14" y="14" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="2" fill="none"/></symbol>
```

### Step 5.2: フィルターチップ群に「年」ボタン追加

- [ ] **Locate `<div class="chip active" data-key="custom">` の </div>**

- [ ] **フィルター直後・filters div を閉じる前に1ボタン挿入**

既存:
```html
    <div class="chip active" data-key="custom"><span class="dot"></span>予定</div>
  </div>
```

変更後:
```html
    <div class="chip active" data-key="custom"><span class="dot"></span>予定</div>
    <button class="chip" id="year-btn" type="button" aria-label="年間ビュー" style="background:var(--surface);color:var(--text-2);border-color:var(--border);">
      <svg style="width:14px;height:14px;"><use href="#i-grid"/></svg>
      年
    </button>
  </div>
```

### Step 5.3: 年間ビュー sheet-overlay の HTML 追加

- [ ] **Locate `<div class="sheet-overlay" id="confirm-overlay">` の </div></div>**

- [ ] **confirm-overlay の直後に year-overlay 追加**

```html
<!-- Year View Sheet -->
<div class="sheet-overlay" id="year-overlay" role="dialog" aria-modal="true" aria-labelledby="year-title">
  <div class="sheet" style="max-height: 92vh;">
    <div class="sheet-handle"></div>
    <div class="sheet-header">
      <div style="display:flex;align-items:center;gap:8px;">
        <button class="icon-btn" id="year-prev" aria-label="前年" style="width:32px;height:32px;"><svg style="width:16px;height:16px;"><use href="#i-left"/></svg></button>
        <div class="sheet-title" id="year-title">2026年</div>
        <button class="icon-btn" id="year-next" aria-label="翌年" style="width:32px;height:32px;"><svg style="width:16px;height:16px;"><use href="#i-right"/></svg></button>
      </div>
      <button class="icon-btn" id="year-close" aria-label="閉じる"><svg><use href="#i-x"/></svg></button>
    </div>
    <div class="sheet-body">
      <div class="year-grid" id="year-grid"></div>
      <div class="year-legend">
        <span class="year-leg"><span class="year-swatch full"></span>両方休み</span>
        <span class="year-leg"><span class="year-swatch half"></span>片方休み</span>
        <span class="year-leg"><span class="year-swatch a"></span>A番</span>
        <span class="year-leg"><span class="year-swatch pay"></span>給料日</span>
      </div>
    </div>
  </div>
</div>
```

### Step 5.4: CSS 追加

- [ ] **CSS の </style> 直前に追加**

```css
.year-grid {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.year-month-row {
  display: flex;
  align-items: center;
  gap: 6px;
}
.year-month-label {
  font-family: var(--font-en);
  font-size: 10px;
  font-weight: 800;
  color: var(--muted);
  letter-spacing: 0.06em;
  width: 26px;
  flex-shrink: 0;
}
.year-cells {
  display: grid;
  grid-template-columns: repeat(31, 1fr);
  gap: 2px;
  flex: 1;
}
.year-cell {
  aspect-ratio: 1;
  background: var(--surface);
  border: 0.5px solid var(--border);
  border-radius: 2px;
  position: relative;
  cursor: pointer;
}
.year-cell.empty { visibility: hidden; }
.year-cell.full { background: var(--cheek-deep); border-color: var(--cheek-deep); }
.year-cell.half { background: var(--cheek); border-color: var(--cheek); }
.year-cell.a::after {
  content: '';
  position: absolute;
  inset: -1px;
  border: 1.5px solid #F59E0B;
  border-radius: 3px;
}
.year-cell.pay::before {
  content: '';
  position: absolute;
  bottom: 1px;
  right: 1px;
  width: 3px;
  height: 3px;
  background: var(--leaf);
  border-radius: 50%;
}
.year-legend {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 16px;
  font-size: 11px;
  font-weight: 700;
  color: var(--muted);
}
.year-leg { display: inline-flex; align-items: center; gap: 5px; }
.year-swatch { width: 12px; height: 12px; border-radius: 3px; display: inline-block; }
.year-swatch.full { background: var(--cheek-deep); }
.year-swatch.half { background: var(--cheek); }
.year-swatch.a { background: white; border: 1.5px solid #F59E0B; }
.year-swatch.pay { background: var(--leaf); border-radius: 50%; }
```

### Step 5.5: renderYearView 関数追加

- [ ] **Locate `function renderRecall()` の閉じカッコ`}`**

- [ ] **直後に renderYearView 関数を挿入**

```javascript
let yearViewYear = null;
function openYearView() {
  yearViewYear = viewYear;
  renderYearView();
  document.getElementById('year-overlay').classList.add('open');
  lockBodyScroll('year-overlay');
}
function closeYearView() {
  document.getElementById('year-overlay').classList.remove('open');
  releaseBodyScroll('year-overlay');
}
function renderYearView() {
  if (yearViewYear == null) yearViewYear = viewYear;
  document.getElementById('year-title').textContent = `${yearViewYear}年`;
  const grid = document.getElementById('year-grid');
  grid.innerHTML = '';
  const monthShort = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'];
  for (let m = 0; m < 12; m++) {
    const row = document.createElement('div');
    row.className = 'year-month-row';
    const lbl = document.createElement('div');
    lbl.className = 'year-month-label';
    lbl.textContent = monthShort[m];
    row.appendChild(lbl);
    const cells = document.createElement('div');
    cells.className = 'year-cells';
    const dim = new Date(yearViewYear, m + 1, 0).getDate();
    for (let d = 1; d <= 31; d++) {
      const cell = document.createElement('button');
      cell.type = 'button';
      cell.className = 'year-cell';
      if (d > dim) {
        cell.classList.add('empty');
        cells.appendChild(cell);
        continue;
      }
      const key = dateKey(yearViewYear, m, d);
      const builtin = EVENTS[key] || [];
      const hasA = builtin.some(e => A_SHIFT_LABELS.includes(e.summary));
      const hasPay = builtin.some(e => e.person === '給料');
      if (isBothOff(builtin)) cell.classList.add('full');
      else {
        const kHas = builtin.some(e => e.person === 'こうき' && REST_LABELS.includes(e.summary));
        const yHas = builtin.some(e => e.person === 'ゆい' && REST_LABELS.includes(e.summary));
        if (kHas || yHas) cell.classList.add('half');
      }
      if (hasA) cell.classList.add('a');
      if (hasPay) cell.classList.add('pay');
      cell.setAttribute('aria-label', `${m+1}月${d}日`);
      cell.onclick = () => {
        haptic(10);
        closeYearView();
        viewYear = yearViewYear;
        viewMonth = m;
        render();
        setTimeout(() => openDaySheet(key, viewYear, viewMonth, d), 120);
      };
      cells.appendChild(cell);
    }
    row.appendChild(cells);
    grid.appendChild(row);
  }
}
```

### Step 5.6: init() でリスナー登録

- [ ] **init() 末尾の他リスナー群の隣に追加**

```javascript
  document.getElementById('year-btn').onclick = openYearView;
  document.getElementById('year-close').onclick = closeYearView;
  document.getElementById('year-overlay').onclick = e => {
    if (e.target.id === 'year-overlay') closeYearView();
  };
  document.getElementById('year-prev').onclick = () => { yearViewYear--; renderYearView(); };
  document.getElementById('year-next').onclick = () => { yearViewYear++; renderYearView(); };
```

### Step 5.7: Escape ハンドラに year-overlay を加える

- [ ] **既存の Escape チェーンに year-overlay を最上位に追加**

```javascript
document.addEventListener('keydown', e => {
  if (e.key !== 'Escape') return;
  if (document.getElementById('year-overlay').classList.contains('open')) closeYearView();
  else if (document.getElementById('confirm-overlay').classList.contains('open')) _resolveConfirm(false);
  else if (document.getElementById('form-overlay').classList.contains('open')) closeForm();
  else if (document.getElementById('settings-overlay').classList.contains('open')) closeSettings();
  else if (document.getElementById('day-overlay').classList.contains('open')) closeDaySheet();
});
```

### Step 5.8: ビルド+検証

- [ ] **Run ビルド**

```bash
python "C:\Users\tamah\Desktop\shift_calendar\build.py" "C:\Users\tamah\OneDrive\Desktop\【登別店】2026年6月シフト初稿  (version 1).xlsx"
```

- [ ] **Run 差分計測**

```bash
cd "C:\Users\tamah\Desktop\shift_calendar"
git add -A
git diff --cached --stat
```

Expected: build.py +170〜200行(警戒帯。200を超えたら次ステップでロールバックして分割実装)

### Step 5.9: 200行超過時のロールバック判定

- [ ] **差分行数チェック**

```bash
git diff --cached --numstat build.py | awk '{print $1}'
```

- [ ] **200行超なら git checkout でロールバックして C5a/C5b に分割**

ロールバック:
```bash
git checkout -- build.py
python "C:\Users\tamah\Desktop\shift_calendar\build.py" "C:\Users\tamah\OneDrive\Desktop\【登別店】2026年6月シフト初稿  (version 1).xlsx"
```

分割: C5a は SVG+CSS+HTML(構造のみ)、C5b は renderYearView ロジック+init リスナー

### Step 5.10: コミット

- [ ] **Commit(200行以内の場合)**

```bash
git commit -m "$(cat <<'EOF'
feat: 年間ヒートマップビュー追加

- フィルター行に年ボタン、タップで12ヶ月×31日のグリッド表示
- 各セル色分け: 両方休み=濃ピンク, 片方休み=薄ピンク
- A番=黄リング, 給料日=緑ドット
- セルタップで該当日にジャンプ
- 前年/翌年送り対応、凡例付き

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git push
```

---

## Self-Review Summary

**Spec coverage:**
- ✅ A-1 祝日多年 → Task 1
- ✅ A-2 SWキー → Task 1
- ✅ A-3 ハプティック → Task 1
- ✅ A-4 confirm置換 → Task 2
- ✅ B-1 記念日 → Task 3
- ✅ B-2 1年前の今日 → Task 4
- ✅ B-3 年間ヒートマップ → Task 5
- ⚠️ Firestore セキュリティルール更新は **指示役の手動工程**(Claude in Chrome 経由)— Task 3 終了後に実施

**Placeholder scan:** TODO/TBD/「実装後」等の placeholder なし。各ステップに実コード/コマンド/期待値あり。

**Type consistency:**
- `HOLIDAYS_BY_YEAR` 一貫使用 ✓
- `Storage.addAnniv/removeAnniv` メソッド名 Task 3 内で統一 ✓
- `showConfirm(title, message, okLabel)` Promise返却 Task 2/Task 3 整合 ✓
- `renderYearView` / `openYearView` / `closeYearView` Task 5 整合 ✓
- `_resolveConfirm(ok)` Task 2 のキャンセル動作で利用 ✓

**Scope check:** 各タスク独立コミット、ロールバック可能。C5のみ要監視(180-200行)、分割手順を Step 5.9 で明示済み。

---

## 実装の進め方

各タスクを完了したら、次のタスクに移る前に:

1. ビルド成功確認(STDERR が openpyxl 警告だけ)
2. preview で動作確認(`mcp__Claude_Preview__preview_eval` で主要要素の存在をチェック)
3. `git diff --cached --stat` で行数確認
4. ロールバック条件(180行超・build失敗・preview失敗)に該当なし
5. コミット&プッシュ
6. Firestore ルール更新(Task 3 後のみ、指示役が Claude in Chrome 経由で実施)

すべて完了したら、変更要約をユーザーに報告。
