# シフトカレンダー v8「予定追加履歴シート」設計

**日付**: 2026-05-24
**ターゲット**: https://tamahome0208-prog.github.io/shift-calendar/
**スコープ**: ユーザーが追加した予定を時系列で一覧できる別シートを追加
**コミット計画**: 1〜2コミット、合計 ~180行(150行超なら分割)

---

## 0. なぜやるか

現状はユーザーが予定を追加すると、該当日のセルにチップが表示されるだけで「最近何を追加したか」「今後の予定リスト」が一目で分からない。シフトカレンダー本来の月表示は維持しつつ、補助的に**時系列リストビュー**があると2人で予定を確認しやすくなる。

---

## 1. UI 設計

### 1-1. エントリポイント

フィルターチップ行に「📋(履歴アイコン)」ボタンを追加(現「年」ボタンの隣)。タップで履歴シート展開。

```
[こうき][ゆい][給料日][予定][年📅][履歴📋]
```

### 1-2. 履歴シート構成

既存 `.sheet-overlay` パターン踏襲。中身は以下:

```
┌──────────────────────────────┐
│ === ハンドル ===              │
│ 予定リスト             [×]    │
│ 過去 X件 / 未来 Y件           │
│ ──────────────────            │
│                              │
│ ▾ 過去                       │
│ ┌─ [予定]   5/15(月)        │
│ │ 美容院 13:00               │
│ │ 3日前に追加        [✏️]   │
│ └──────                      │
│ ┌─ [こうき] 5/14(日)         │
│ │ デートプラン               │
│ │ 1週間前に追加      [✏️]   │
│ └──────                      │
│                              │
│ ━━━━━ 今日 5/24 ━━━━━        │
│                              │
│ ▾ これから                   │
│ ┌─ [予定]   5/25(火)        │
│ │ 整体 10:00                 │
│ │ 30分前に追加       [✏️]   │
│ └──────                      │
│ ...                          │
└──────────────────────────────┘
```

### 1-3. カード要素

| 要素 | 内容 |
|---|---|
| バッジ | 種類タグ(`person-tag` 再利用、`こうき/ゆい/予定`色分け) |
| 日付 | `5/15(月)` 形式、`var(--text)` |
| タイトル | 14px 太字、必要なら時刻併記 |
| メモ | 12px ミュート、先頭40文字+`…` |
| 相対時刻 | 「X分前/X時間前/X日前/X週間前/それ以前」 |
| 編集ボタン | 既存 row-icon を再利用、タップで該当日にジャンプ+編集フォーム |

カードタップ全体で「該当日のシート(既存 day-overlay)を開く」、編集ボタンタップで「フォームsheet を編集モードで開く」。

---

## 2. データモデル拡張

### 2-1. createdAt フィールド追加

custom event の保存時に `createdAt: Date.now()`(Unix ms)を追加。既存データに無い場合は `undefined` のままで、相対時刻表示は「以前に追加」とフォールバック。

```js
// 既存 saveForm() 内
const event = { date, type, title, desc, start, end, reminderMin,
                createdAt: editingId ? existing.createdAt || Date.now() : Date.now() };
```

編集時は createdAt を維持(上書きしない)。

### 2-2. Firestore スキーマ

`events` コレクションは後方互換で `createdAt` は optional フィールド。`onSnapshot` 受信時にそのまま `allCustomEvents` に反映。セキュリティルール変更不要。

---

## 3. ロジック

### 3-1. ソート

```js
function getHistoryItems() {
  const today = new Date(); today.setHours(0, 0, 0, 0);
  const items = allCustomEvents
    .filter(e => e.type !== 'memo') // メモは履歴に含めない
    .map(e => ({
      ...e,
      _dateObj: new Date(e.date + 'T00:00:00'),
    }))
    .sort((a, b) => a._dateObj - b._dateObj); // 予定日昇順
  const past = items.filter(e => e._dateObj < today);
  const future = items.filter(e => e._dateObj >= today);
  return { past, future, today };
}
```

### 3-2. 相対時刻ヘルパー

```js
function relativeTime(ms) {
  if (!ms) return '以前に追加';
  const diff = (Date.now() - ms) / 1000; // 秒
  if (diff < 60) return 'たった今追加';
  if (diff < 3600) return `${Math.floor(diff/60)}分前に追加`;
  if (diff < 86400) return `${Math.floor(diff/3600)}時間前に追加`;
  if (diff < 604800) return `${Math.floor(diff/86400)}日前に追加`;
  if (diff < 2592000) return `${Math.floor(diff/604800)}週間前に追加`;
  return `${Math.floor(diff/2592000)}ヶ月前に追加`;
}
```

### 3-3. シート開閉

```js
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
```

Escape ハンドラに最上位として組込:
```js
if (document.getElementById('history-overlay').classList.contains('open')) closeHistoryView();
else if (...) // 既存チェーン
```

---

## 4. CSS

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
}
.history-card-title {
  font-size: 14px;
  font-weight: 800;
  color: var(--text);
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

既存 `.person-tag` `.row-icon` `.event-row` 系を再利用するため重複定義は避ける。

---

## 5. HTML

ヘッダーのフィルター行(year-btn 直後)に追加:
```html
<button class="chip" id="history-btn" type="button" aria-label="予定リスト"
        style="background:var(--surface);color:var(--text-2);border-color:var(--border);">
  <svg style="width:14px;height:14px;"><use href="#i-clock"/></svg>
  履歴
</button>
```

オーバーレイ(year-overlay 後に挿入):
```html
<div class="sheet-overlay" id="history-overlay" role="dialog" aria-modal="true"
     aria-labelledby="history-title" aria-hidden="true">
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

---

## 6. 範囲外(YAGNI)

- 編集履歴・削除ログ(別タスク、別仕様書)
- 検索・フィルター(件数増えたら)
- 完了済みチェック(タスク機能ではない)
- 別ルート URL(SPA化は別議論)
- メモ機能の履歴含め(履歴=スケジュール追加に限定)

---

## 7. 実装ファイル

すべて `build.py` 編集のみ。

| ファイル | 役割 | 変更可否 |
|---|---|---|
| `build.py` | HTMLテンプレ + 定数 | ✅ |
| 生成物 | 自動生成 | ❌ |
| Firestore | events スキーマ拡張(後方互換) | 既存 |

---

## 8. コミット計画

| # | 内容 | 推定行数 |
|---|---|---|
| C1 | createdAt追加+履歴シートHTML/CSS/JS+初期動作 | ~180行(目標、150超なら分割) |

200行を超えたら C1a(データ+HTML+CSS) と C1b(JS ロジック+ Escape組込)に分割。

---

## 9. テスト計画

| 観点 | 検証 |
|---|---|
| 追加 | 予定を1個追加 → 履歴シート開く → 表示される + 「たった今追加」 |
| ソート | 過去予定追加→過去セクション末尾、未来→未来先頭 |
| 既存データ | createdAt なしの予定は「以前に追加」表記 |
| メモ除外 | デートメモ追加しても履歴に出ない |
| ジャンプ | カードタップ → 該当日 day-overlay 表示 |
| 編集 | 編集アイコンタップ → form-overlay 編集モード |
| Escape | Escape で履歴シート優先で閉じる |

---

## 10. ロールバック条件

- ビルドエラー / HTMLサイズ30%超変動 / preview起動失敗
- 既存機能(year-overlay, settings-overlay, day-overlay, FAB)の regression
- 1コミット200行超(自動ロールバックして C1a/C1b 分割)
