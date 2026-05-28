# v9 毎年繰り返しの予定 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 既存「記念日」機能を「毎年の予定(誕生日・記念日など)」に拡張し、カレンダーグリッドに種類別チップを表示する。

**Architecture:** 既存 `anniversaries` collection(`{name, month, day, type}`)が年フリーの月日固定データモデルとして既に整っているのを活用。3件上限の撤廃、設定UIに種類ピッカー追加、SVGスプライトに `st-cake` 追加、`render()` でセル描画時に該当 anniversaries を線形検索して特別チップを追加。

**Tech Stack:** Python 3 (build時) / HTML+CSS+JS (生成物)

**前提コマンド:**
- ビルド: `python "C:\Users\tamah\Desktop\shift_calendar\build.py" "C:\Users\tamah\CrossDevice\Pixel 10\storage\Download\LINEWORKS\005036@kcsline\k\oneapp\r\jp1.10018843\10018843\v2-10018843-5398951346.390981933\【登別店】2026年6月シフト初稿  (version 1).xlsx"`
- 差分計測: `git diff --cached --stat`
- ロールバック: `git checkout build.py index.html manifest.json sw.js`

---

## File Structure

すべて `C:\Users\tamah\Desktop\shift_calendar\build.py` の編集。

| ファイル | 役割 | 変更可否 |
|---|---|---|
| `build.py` | テンプレ+定数+ロジック | ✅ |
| `index.html`/`manifest.json`/`sw.js` | 自動生成 | ❌ |
| `firebase-config.js`/`events.json`/`extract_events.py` | 別目的 | ❌ |
| Firestore | スキーマ変更なし、ルール変更なし | 既存 |

---

## Task 1: 毎年繰り返しの予定 機能拡張

**Phase:** C1(単一コミット)
**推定差分:** +70行 / -5行

**Files:**
- Modify: `build.py:1478` 直後(SVG sprite に `st-cake` 追加)
- Modify: `build.py:1696`(ラベル文言変更)
- Modify: `build.py:1701-1708`(設定フォームに種類セレクト追加)
- Modify: `build.py` CSS の `</style>` 直前(`.anniv-chip*` 追加)
- Modify: `build.py:2799-2819`(`renderSettingsAnniv`: 種類絵文字表示 + 上限撤廃)
- Modify: `build.py:3032-3042`(`anniv-save` ハンドラ: type 取得)
- Modify: `build.py:2472`付近(`render()` 内、セル描画ロジックに anniversaries チップ追加)

### Step 1.1: SVG sprite に st-cake 追加

- [ ] **Locate `<symbol id="st-star"` の位置確認**

Run:
```bash
grep -n 'symbol id="st-star"' "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

Expected: 1478

- [ ] **st-star の `</symbol>` 直後に st-cake symbol を挿入**

`Read build.py offset=1478 limit=4` で st-star の閉じタグ位置を確認後、その直後に追加:

```html
    <symbol id="st-cake" viewBox="0 0 24 24">
      <rect x="4" y="12" width="16" height="9" rx="1.5" fill="#FFD9E6" stroke="#F764A2" stroke-width="0.8"/>
      <path d="M 4 15 Q 8 17 12 15 Q 16 17 20 15" stroke="#F764A2" stroke-width="1" fill="none"/>
      <rect x="11" y="6" width="2" height="6" fill="#FBBF24" rx="0.5"/>
      <path d="M12 4 L 12.5 6 L 11.5 6 Z" fill="#FF8E5C"/>
    </symbol>
```

### Step 1.2: 設定シートのラベル文言変更

- [ ] **Modify `build.py:1696`**

既存:
```html
        <label style="display:flex;align-items:center;gap:6px;">記念日(最大3件)</label>
```

変更後:
```html
        <label style="display:flex;align-items:center;gap:6px;">毎年の予定(誕生日・記念日など)</label>
```

### Step 1.3: 設定フォームに種類セレクト追加

- [ ] **Locate `<input type="text" id="anniv-name"`**

Run:
```bash
grep -n 'id="anniv-name"' "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

Expected: 1702

- [ ] **anniv-name 入力の直後に種類セレクトを挿入**

既存(`build.py:1701-1707`):
```html
        <div id="anniv-add-form" style="display:none; margin-top:8px;">
          <input type="text" id="anniv-name" placeholder="例: 付き合った日" style="width:100%;padding:10px;border-radius:10px;border:1.5px solid var(--border);font-size:14px;margin-bottom:6px;">
          <div style="display:flex;gap:6px;">
            <input type="number" id="anniv-month" min="1" max="12" placeholder="月" style="flex:1;padding:10px;border-radius:10px;border:1.5px solid var(--border);font-size:14px;">
            <input type="number" id="anniv-day" min="1" max="31" placeholder="日" style="flex:1;padding:10px;border-radius:10px;border:1.5px solid var(--border);font-size:14px;">
            <button class="btn btn-primary" id="anniv-save" type="button" style="flex:1;font-size:13px;padding:10px;">保存</button>
          </div>
        </div>
```

変更後(`anniv-name` の直後に種類セレクト挿入):
```html
        <div id="anniv-add-form" style="display:none; margin-top:8px;">
          <input type="text" id="anniv-name" placeholder="例: 付き合った日" style="width:100%;padding:10px;border-radius:10px;border:1.5px solid var(--border);font-size:14px;margin-bottom:6px;">
          <select id="anniv-type" style="width:100%;padding:10px;border-radius:10px;border:1.5px solid var(--border);font-size:14px;margin-bottom:6px;background:var(--surface);">
            <option value="birth">🎂 誕生日</option>
            <option value="anniv" selected>💗 記念日</option>
            <option value="other">🌸 その他</option>
          </select>
          <div style="display:flex;gap:6px;">
            <input type="number" id="anniv-month" min="1" max="12" placeholder="月" style="flex:1;padding:10px;border-radius:10px;border:1.5px solid var(--border);font-size:14px;">
            <input type="number" id="anniv-day" min="1" max="31" placeholder="日" style="flex:1;padding:10px;border-radius:10px;border:1.5px solid var(--border);font-size:14px;">
            <button class="btn btn-primary" id="anniv-save" type="button" style="flex:1;font-size:13px;padding:10px;">保存</button>
          </div>
        </div>
```

### Step 1.4: CSS .anniv-chip* を追加

- [ ] **Locate CSS の `</style>` 終端**

Run:
```bash
grep -n "^</style>" "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

- [ ] **`</style>` の直前に anniv-chip 関連 CSS を追加**

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
  width: 12px;
  height: 12px;
  flex-shrink: 0;
}
.anniv-chip span {
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}
.anniv-chip.t-birth { background: linear-gradient(135deg, var(--cheek) 0%, var(--cheek-deep) 100%); }
.anniv-chip.t-anniv { background: linear-gradient(135deg, var(--yui) 0%, var(--yui-meeting) 100%); }
.anniv-chip.t-other { background: linear-gradient(135deg, var(--custom) 0%, #A372C6 100%); }
```

### Step 1.5: renderSettingsAnniv 修正(種類絵文字+上限撤廃)

- [ ] **Locate `function renderSettingsAnniv`**

Run:
```bash
grep -n "function renderSettingsAnniv" "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

Expected: 2799

- [ ] **renderSettingsAnniv 全体を置換**

既存(`build.py:2799-2819`):
```javascript
function renderSettingsAnniv() {
  const list = document.getElementById('anniv-list');
  if (!list) return;
  list.innerHTML = '';
  const annivs = allAnniversaries || [];
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
  const addBtn = document.getElementById('anniv-add-toggle');
  if (addBtn) addBtn.style.display = annivs.length >= 3 ? 'none' : 'inline-flex';
}
```

変更後:
```javascript
function renderSettingsAnniv() {
  const list = document.getElementById('anniv-list');
  if (!list) return;
  list.innerHTML = '';
  const annivs = allAnniversaries || [];
  const typeEmoji = { birth: '🎂', anniv: '💗', other: '🌸' };
  annivs.forEach(a => {
    const row = document.createElement('div');
    row.className = 'anniv-row';
    const emoji = typeEmoji[a.type || 'other'] || '🌸';
    row.innerHTML = `
      <span class="anniv-name">${emoji} ${escapeHtml(a.name)}</span>
      <span class="anniv-date">${a.month}/${a.day}</span>
      <button class="anniv-del" data-id="${a.id}" aria-label="削除">×</button>
    `;
    list.appendChild(row);
  });
  list.querySelectorAll('[data-id]').forEach(b => {
    b.onclick = () => Storage.removeAnniv(b.dataset.id);
  });
  const addBtn = document.getElementById('anniv-add-toggle');
  if (addBtn) addBtn.style.display = 'inline-flex';
}
```

差分: `typeEmoji` マップ追加、row 内に emoji prefix、上限制限を `'inline-flex'` 固定に。

### Step 1.6: anniv-save ハンドラに type 取得

- [ ] **Locate `anniv-save` の onclick**

Run:
```bash
grep -n "annivSave.onclick" "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

Expected: 3032

- [ ] **anniv-save ハンドラを修正**

既存(`build.py:3031-3042`):
```javascript
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

変更後:
```javascript
  const annivSave = document.getElementById('anniv-save');
  if (annivSave) annivSave.onclick = async () => {
    const name = document.getElementById('anniv-name').value.trim();
    const month = parseInt(document.getElementById('anniv-month').value, 10);
    const day = parseInt(document.getElementById('anniv-day').value, 10);
    const type = document.getElementById('anniv-type').value || 'anniv';
    if (!name || !month || !day || month < 1 || month > 12 || day < 1 || day > 31) return;
    await Storage.addAnniv({ name, month, day, type });
    document.getElementById('anniv-name').value = '';
    document.getElementById('anniv-month').value = '';
    document.getElementById('anniv-day').value = '';
    document.getElementById('anniv-add-form').style.display = 'none';
    const addBtn = document.getElementById('anniv-add-toggle');
    if (addBtn) addBtn.style.display = 'inline-flex';
  };
```

差分: type 取得を追加、addAnniv に渡す、フォーム閉じた後 add ボタンを再表示(上限撤廃と整合)。

### Step 1.7: render() グリッドに anniv チップを追加

- [ ] **Locate `dayEvents.slice(0, 3).forEach`**

Run:
```bash
grep -n "dayEvents.slice(0, 3).forEach" "C:\Users\tamah\Desktop\shift_calendar\build.py"
```

Expected: 2472

- [ ] **dayEvents.slice 直前の `const dayEvents = ...` を Read で確認**

`Read build.py offset=2470 limit=20` で render の該当ブロックを確認。

- [ ] **dayEvents 描画ループの直前に anniv チップ追加処理を挿入**

既存(該当箇所):
```javascript
    const dayEvents = eventsForDate(key).filter(e => filters[PERSON_KEY[e.person]]);
    dayEvents.slice(0, 3).forEach(e => {
```

変更後(`dayEvents` 定義の直後、`forEach` の前に挿入):
```javascript
    const dayEvents = eventsForDate(key).filter(e => filters[PERSON_KEY[e.person]]);
    const anniversariesForDay = (allAnniversaries || []).filter(a => a.month === m + 1 && a.day === d);
    anniversariesForDay.forEach(a => {
      const type = a.type || 'other';
      const chip = document.createElement('div');
      chip.className = `anniv-chip t-${type}`;
      const iconId = type === 'birth' ? 'st-cake' : (type === 'anniv' ? 'heart' : 'st-star');
      chip.innerHTML = `<svg><use href="#${iconId}"/></svg><span>${escapeHtml(a.name)}</span>`;
      cell.appendChild(chip);
    });
    dayEvents.slice(0, 3).forEach(e => {
```

注意: ここの `m` と `d` は render() ループ内のセル別 month(0-origin) と day。anniv.month は 1-origin なので `m + 1` でマッチ判定する。anniv チップは `dayEvents` 3件制限の外側に追加(常時表示)。

### Step 1.8: ビルド+検証

- [ ] **Run ビルド**

```bash
python "C:\Users\tamah\Desktop\shift_calendar\build.py" "C:\Users\tamah\CrossDevice\Pixel 10\storage\Download\LINEWORKS\005036@kcsline\k\oneapp\r\jp1.10018843\10018843\v2-10018843-5398951346.390981933\【登別店】2026年6月シフト初稿  (version 1).xlsx"
```

Expected: `index.html (63件のイベント)` 正常終了

- [ ] **Run 差分計測**

```bash
cd "C:\Users\tamah\Desktop\shift_calendar"
git add -A
git diff --cached --stat
```

Expected: build.py +60〜90行(目標70)、150行以内

### Step 1.9: 150行超過なら一部ロールバック

- [ ] **差分が build.py 単体で 150行を超えていたら**

```bash
git checkout build.py index.html manifest.json sw.js
```

その場合は Step 1.5(emoji 表示)と Step 1.7(render 拡張)のみ残し、Step 1.3 の セレクト追加を最小化(`<select>` を1行で潰す)。

### Step 1.10: コミット&プッシュ

- [ ] **Commit**

```bash
cd "C:\Users\tamah\Desktop\shift_calendar"
git commit -m "$(cat <<'EOF'
v9: 毎年の予定(誕生日・記念日)をカレンダーに表示

- 既存 anniversaries collection を「毎年の予定」に拡張
- 3件上限撤廃、設定画面で何件でも追加可
- 種類セレクト追加: 🎂誕生日 / 💗記念日 / 🌸その他
- カレンダーグリッドに該当月日でチップ表示
  - birth=ピンクケーキ(st-cake新規SVG)、anniv=ハート、other=ラベンダー星
- 既存データは type 未設定なら other 扱い(後方互換)
- ヒーローカウントダウンは維持

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git push
```

---

## Self-Review

**Spec coverage:**
- ✅ ラベル変更 → Step 1.2
- ✅ 種類セレクト追加 → Step 1.3 + 1.6
- ✅ 上限撤廃 → Step 1.5 + 1.6(`addBtn.style.display = 'inline-flex'` 固定)
- ✅ カレンダーチップ表示 → Step 1.7
- ✅ 種類別色分け + アイコン → Step 1.4(CSS) + Step 1.7(iconId 分岐)
- ✅ st-cake SVG → Step 1.1
- ✅ 既存データ後方互換 → Step 1.5(`a.type || 'other'`) + Step 1.7(`type = a.type || 'other'`)
- ✅ 設定リストに type 絵文字 → Step 1.5

**Placeholder scan:**
- TBD/TODO なし
- 各ステップに完全コード/コマンド
- 「Similar to」なし

**Type consistency:**
- `anniversaries` フィールド名: `id, name, month, day, type` で一貫
- `type` 値: `'birth' | 'anniv' | 'other'` で一貫
- SVG symbol id: `st-cake / heart / st-star` で renderer と iconId 分岐が整合
- CSS クラス: `anniv-chip` + `t-birth/t-anniv/t-other` 命名統一
- 既存関数: `Storage.addAnniv`, `Storage.removeAnniv`, `renderSettingsAnniv` 名はそのまま使用

---

## 実装の進め方

1. Step 1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 1.6 → 1.7 の順に Edit を適用
2. Step 1.8 でビルド成功確認
3. Step 1.9 で差分行数確認(150以内)
4. Step 1.10 でコミット&プッシュ
5. 完了報告

すべて完了したら、指示役側で preview 起動 → 設定画面で誕生日追加 → カレンダーグリッドに表示確認(誕生日が 5/29 等近い日なら今日のセルに出る)。
