"""シフトExcel -> 自己完結HTMLカレンダー生成 (v2 プレミアムデザイン + 予定追加機能)

Usage: python build.py "<xlsx>"
"""
import sys, os, json

sys.path.insert(0, r"C:\Users\tamah\Desktop\shift_to_ics")
from shift_to_ics import parse_shift, build_salary_events

OUTPUT_DIR = r"C:\Users\tamah\Desktop\shift_calendar"

# 表示名マッピング: Excelのヘッダー -> 表示名
NAME_MAP = {"安中": "こうき", "恩田": "ゆい"}

TEMPLATE = r"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover, user-scalable=no">
<meta name="theme-color" content="#ffffff">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="シフト">
<title>シフトカレンダー</title>
<link rel="manifest" href="manifest.json">
<link rel="apple-touch-icon" href="icon.png">
<style>
:root {
  --bg: #ffffff;
  --surface: #ffffff;
  --surface-soft: #fafaf9;
  --surface-2: #f5f5f4;
  --text: #0c0a09;
  --text-2: #44403c;
  --muted: #78716c;
  --border: #e7e5e4;
  --border-strong: #d6d3d1;
  --kouki: #4f46e5;
  --kouki-soft: #eef2ff;
  --yui: #be185d;
  --yui-soft: #fce7f3;
  --pay: #047857;
  --pay-soft: #d1fae5;
  --custom: #c2410c;
  --custom-soft: #ffedd5;
  --today: #0c0a09;
  --sun: #dc2626;
  --sat: #2563eb;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.04);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 16px 48px rgba(0, 0, 0, 0.18);
  --safe-top: env(safe-area-inset-top, 0px);
  --safe-bottom: env(safe-area-inset-bottom, 0px);
}
* { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
html, body {
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Hiragino Sans", "Yu Gothic UI", "Noto Sans JP", sans-serif;
  font-weight: 500;
  min-height: 100vh;
  overscroll-behavior: none;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
body {
  padding-bottom: calc(var(--safe-bottom) + 80px);
  letter-spacing: -0.01em;
}
button { font-family: inherit; cursor: pointer; border: none; background: none; color: inherit; }

/* HEADER */
header {
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  padding: calc(var(--safe-top) + 12px) 16px 10px;
  position: sticky;
  top: 0;
  z-index: 20;
  border-bottom: 1px solid var(--border);
}
.top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.title-block {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0;
}
.year-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--muted);
  letter-spacing: 0.04em;
}
.month-label {
  font-size: 26px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.02em;
  line-height: 1.05;
}
.icon-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--text);
  transition: background 0.15s, transform 0.1s;
}
.icon-btn:active { background: var(--surface-2); transform: scale(0.92); }
.icon-btn svg { width: 22px; height: 22px; }
.today-btn {
  background: var(--text);
  color: white;
  font-weight: 700;
  padding: 8px 14px;
  border-radius: 999px;
  font-size: 13px;
  letter-spacing: 0.02em;
}
.today-btn:active { transform: scale(0.94); }

.filters {
  display: flex;
  gap: 6px;
  margin-top: 12px;
  overflow-x: auto;
  scrollbar-width: none;
  padding-bottom: 2px;
}
.filters::-webkit-scrollbar { display: none; }
.chip {
  padding: 7px 14px;
  border-radius: 999px;
  font-size: 12.5px;
  font-weight: 700;
  user-select: none;
  border: 1.5px solid var(--border);
  background: var(--surface);
  color: var(--muted);
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
  transition: all 0.15s;
}
.chip:active { transform: scale(0.94); }
.chip .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}
.chip[data-key="kouki"] { color: var(--kouki); }
.chip[data-key="kouki"].active { background: var(--kouki); color: white; border-color: var(--kouki); }
.chip[data-key="yui"] { color: var(--yui); }
.chip[data-key="yui"].active { background: var(--yui); color: white; border-color: var(--yui); }
.chip[data-key="pay"] { color: var(--pay); }
.chip[data-key="pay"].active { background: var(--pay); color: white; border-color: var(--pay); }
.chip[data-key="custom"] { color: var(--custom); }
.chip[data-key="custom"].active { background: var(--custom); color: white; border-color: var(--custom); }
.chip:not(.active) .dot { background: currentColor; }
.chip.active .dot { background: white; }

/* WEEKDAYS */
.weekdays {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  padding: 12px 8px 8px;
  font-size: 11px;
  font-weight: 700;
  text-align: center;
  color: var(--muted);
  letter-spacing: 0.06em;
  background: var(--bg);
}
.weekdays .sun { color: var(--sun); }
.weekdays .sat { color: var(--sat); }

/* GRID */
.grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 3px;
  padding: 0 8px 16px;
}
.cell {
  background: var(--surface);
  min-height: 110px;
  min-width: 0;
  padding: 6px 4px 5px;
  display: flex;
  flex-direction: column;
  gap: 3px;
  border-radius: 10px;
  border: 1px solid var(--border);
  overflow: hidden;
  transition: transform 0.1s;
  position: relative;
}
.cell:active { transform: scale(0.97); }
.cell.other-month {
  background: var(--surface-soft);
  border-color: transparent;
}
.cell.other-month .date-num { color: var(--muted); opacity: 0.55; }
.cell.today {
  border-color: var(--text);
  border-width: 1.5px;
}
.date-num {
  font-size: 14px;
  font-weight: 700;
  height: 22px;
  display: flex;
  align-items: center;
  padding-left: 2px;
  color: var(--text-2);
}
.cell.today .date-num {
  background: var(--today);
  color: white;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  justify-content: center;
  padding: 0;
  font-weight: 800;
}
.date-num.sun { color: var(--sun); }
.date-num.sat { color: var(--sat); }
.date-num.holiday { color: var(--sun); }
.cell.today.weekday-0 .date-num,
.cell.today.weekday-6 .date-num,
.cell.today.is-holiday .date-num { background: var(--today); color: white; }
.event {
  padding: 2px 3px 3px;
  border-radius: 5px;
  color: white;
  line-height: 1.05;
  letter-spacing: -0.03em;
  min-width: 0;
  max-width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0;
  overflow: hidden;
  text-align: center;
}
.event .event-name {
  font-size: 8px;
  font-weight: 700;
  opacity: 0.88;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  letter-spacing: 0;
  max-width: 100%;
}
.event .event-label {
  font-size: 9.5px;
  font-weight: 800;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 1px;
  max-width: 100%;
  letter-spacing: -0.04em;
}
.event.pay { padding: 3px 3px; }
.event.pay .event-label { font-size: 10px; letter-spacing: -0.05em; }
.event.kouki { background: var(--kouki); }
.event.yui { background: var(--yui); }
.event.pay { background: var(--pay); }
.event.custom { background: var(--custom); }
.more-events {
  font-size: 9.5px;
  color: var(--muted);
  font-weight: 700;
  padding: 0 4px;
  letter-spacing: 0;
}

/* FAB */
.fab {
  position: fixed;
  right: 20px;
  bottom: calc(var(--safe-bottom) + 20px);
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: var(--text);
  color: white;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-md);
  z-index: 30;
  transition: transform 0.15s;
}
.fab:active { transform: scale(0.92); }
.fab svg { width: 26px; height: 26px; }

/* SHEET / MODAL */
.sheet-overlay {
  position: fixed;
  inset: 0;
  background: rgba(12, 10, 9, 0.45);
  display: none;
  align-items: flex-end;
  justify-content: center;
  z-index: 50;
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}
.sheet-overlay.open { display: flex; animation: fadeIn 0.2s ease-out; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.sheet {
  background: var(--surface);
  width: 100%;
  max-width: 480px;
  border-radius: 24px 24px 0 0;
  padding: 12px 0 0;
  max-height: 88vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.24s cubic-bezier(0.32, 0.72, 0, 1);
  box-shadow: var(--shadow-lg);
}
@keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }
.sheet-handle {
  width: 36px;
  height: 5px;
  background: var(--border-strong);
  border-radius: 999px;
  margin: 0 auto 8px;
}
.sheet-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 18px 14px;
  border-bottom: 1px solid var(--border);
}
.sheet-title {
  font-size: 18px;
  font-weight: 800;
  letter-spacing: -0.01em;
}
.sheet-title-sub {
  font-size: 12px;
  color: var(--muted);
  font-weight: 600;
  margin-top: 2px;
}
.sheet-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
  -webkit-overflow-scrolling: touch;
}
.sheet-footer {
  padding: 12px 16px calc(16px + var(--safe-bottom));
  border-top: 1px solid var(--border);
  background: var(--surface);
}
.event-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 14px;
  border-radius: 14px;
  margin-bottom: 8px;
  background: var(--surface-soft);
  border: 1px solid var(--border);
}
.event-row .bullet {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.event-row .bullet.kouki { background: var(--kouki); }
.event-row .bullet.yui { background: var(--yui); }
.event-row .bullet.pay { background: var(--pay); }
.event-row .bullet.custom { background: var(--custom); }
.event-row .text-block { flex: 1; min-width: 0; }
.event-row .label {
  font-size: 15px;
  font-weight: 700;
  color: var(--text);
  line-height: 1.3;
}
.event-row .meta {
  font-size: 12px;
  color: var(--muted);
  font-weight: 600;
  margin-top: 2px;
  display: flex;
  gap: 6px;
  align-items: center;
}
.event-row .person-tag {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
}
.event-row .person-tag.kouki { background: var(--kouki-soft); color: var(--kouki); }
.event-row .person-tag.yui { background: var(--yui-soft); color: var(--yui); }
.event-row .person-tag.pay { background: var(--pay-soft); color: var(--pay); }
.event-row .person-tag.custom { background: var(--custom-soft); color: var(--custom); }
.event-row .actions {
  display: flex;
  gap: 4px;
}
.row-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--muted);
  background: var(--surface);
  border: 1px solid var(--border);
}
.row-icon:active { background: var(--surface-2); }
.row-icon svg { width: 16px; height: 16px; }
.row-icon.danger { color: var(--yui); }
.empty {
  text-align: center;
  padding: 32px 16px;
  color: var(--muted);
  font-size: 14px;
  font-weight: 600;
}

/* BUTTONS */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 13px 18px;
  border-radius: 14px;
  font-weight: 700;
  font-size: 15px;
  letter-spacing: -0.005em;
  border: 1.5px solid transparent;
  transition: transform 0.1s;
  width: 100%;
}
.btn:active { transform: scale(0.97); }
.btn-primary { background: var(--text); color: white; }
.btn-secondary { background: var(--surface); color: var(--text); border-color: var(--border-strong); }
.btn-danger { background: var(--surface); color: var(--yui); border-color: var(--yui); }
.btn-row { display: flex; gap: 10px; }
.btn-row .btn { flex: 1; }
.btn svg { width: 18px; height: 18px; }

/* FORM */
.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 14px;
}
.field label {
  font-size: 12px;
  font-weight: 700;
  color: var(--muted);
  letter-spacing: 0.04em;
}
.field input, .field textarea, .field select {
  font-family: inherit;
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
  background: var(--surface-soft);
  border: 1.5px solid var(--border);
  border-radius: 12px;
  padding: 13px 14px;
  width: 100%;
  outline: none;
  transition: border 0.15s;
  -webkit-appearance: none;
  appearance: none;
}
.field input:focus, .field textarea:focus, .field select:focus {
  border-color: var(--text);
  background: var(--surface);
}
.field textarea { resize: vertical; min-height: 60px; }
.field select {
  background-image: url("data:image/svg+xml;charset=utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath fill='%2378716c' d='M6 8L0 0h12z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 16px center;
  padding-right: 38px;
}
.type-picker {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
}
.type-option {
  padding: 12px 8px;
  border-radius: 12px;
  border: 1.5px solid var(--border);
  background: var(--surface);
  font-weight: 700;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: var(--text-2);
  transition: all 0.15s;
}
.type-option:active { transform: scale(0.95); }
.type-option .dot { width: 8px; height: 8px; border-radius: 50%; }
.type-option[data-type="kouki"] .dot { background: var(--kouki); }
.type-option[data-type="yui"] .dot { background: var(--yui); }
.type-option[data-type="custom"] .dot { background: var(--custom); }
.type-option.selected[data-type="kouki"] { background: var(--kouki); color: white; border-color: var(--kouki); }
.type-option.selected[data-type="yui"] { background: var(--yui); color: white; border-color: var(--yui); }
.type-option.selected[data-type="custom"] { background: var(--custom); color: white; border-color: var(--custom); }
.type-option.selected .dot { background: white; }
.add-event-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border-radius: 12px;
  background: var(--surface-soft);
  border: 1.5px dashed var(--border-strong);
  color: var(--muted);
  font-weight: 700;
  font-size: 14px;
  justify-content: center;
  margin-top: 4px;
}
.add-event-row:active { background: var(--surface-2); }
.add-event-row svg { width: 18px; height: 18px; }
</style>
</head>
<body>
<header>
  <div class="top-row">
    <div class="title-block">
      <div class="year-label" id="year-label"></div>
      <div class="month-label" id="month-label"></div>
    </div>
    <button class="today-btn" id="today">今日</button>
    <button class="icon-btn" id="prev" aria-label="前月">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
    </button>
    <button class="icon-btn" id="next" aria-label="次月">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
    </button>
  </div>
  <div class="filters">
    <div class="chip active" data-key="kouki"><span class="dot"></span>こうき</div>
    <div class="chip active" data-key="yui"><span class="dot"></span>ゆい</div>
    <div class="chip active" data-key="pay"><span class="dot"></span>給料日</div>
    <div class="chip active" data-key="custom"><span class="dot"></span>予定</div>
  </div>
</header>
<div class="weekdays">
  <div class="sun">日</div><div>月</div><div>火</div><div>水</div><div>木</div><div>金</div><div class="sat">土</div>
</div>
<div class="grid" id="grid"></div>

<button class="fab" id="fab" aria-label="予定を追加">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
</button>

<!-- Day Detail Sheet -->
<div class="sheet-overlay" id="day-overlay">
  <div class="sheet">
    <div class="sheet-handle"></div>
    <div class="sheet-header">
      <div>
        <div class="sheet-title" id="day-title"></div>
        <div class="sheet-title-sub" id="day-subtitle"></div>
      </div>
      <button class="icon-btn" id="day-close" aria-label="閉じる">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>
    <div class="sheet-body" id="day-body"></div>
    <div class="sheet-footer">
      <button class="btn btn-primary" id="day-add">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        この日に予定を追加
      </button>
    </div>
  </div>
</div>

<!-- Add/Edit Form Sheet -->
<div class="sheet-overlay" id="form-overlay">
  <div class="sheet">
    <div class="sheet-handle"></div>
    <div class="sheet-header">
      <div class="sheet-title" id="form-title">予定を追加</div>
      <button class="icon-btn" id="form-close" aria-label="閉じる">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>
    <div class="sheet-body">
      <div class="field">
        <label>日付</label>
        <input type="date" id="f-date">
      </div>
      <div class="field">
        <label>種類</label>
        <div class="type-picker">
          <div class="type-option" data-type="kouki"><span class="dot"></span>こうき</div>
          <div class="type-option" data-type="yui"><span class="dot"></span>ゆい</div>
          <div class="type-option selected" data-type="custom"><span class="dot"></span>予定</div>
        </div>
      </div>
      <div class="field">
        <label>タイトル</label>
        <input type="text" id="f-title" placeholder="例: 美容院、買い物、デート">
      </div>
      <div class="field">
        <label>メモ(任意)</label>
        <textarea id="f-desc" placeholder=""></textarea>
      </div>
    </div>
    <div class="sheet-footer">
      <div class="btn-row">
        <button class="btn btn-danger" id="f-delete" style="display:none;">削除</button>
        <button class="btn btn-secondary" id="f-cancel">キャンセル</button>
        <button class="btn btn-primary" id="f-save">保存</button>
      </div>
    </div>
  </div>
</div>

<script>
const EVENTS = __EVENTS_JSON__;
const HOLIDAYS = __HOLIDAYS_JSON__;

const PERSON_KEY = {"こうき":"kouki","ゆい":"yui","給料":"pay","予定":"custom"};
const PERSON_FROM_KEY = {kouki:"こうき", yui:"ゆい", pay:"給料", custom:"予定"};
const filters = { kouki: true, yui: true, pay: true, custom: true };
const CUSTOM_KEY = 'shift-cal-custom-v1';

let viewYear, viewMonth;
let editingId = null;
let formType = 'custom';

function loadCustom() {
  try { return JSON.parse(localStorage.getItem(CUSTOM_KEY) || '[]'); }
  catch { return []; }
}
function saveCustom(arr) {
  localStorage.setItem(CUSTOM_KEY, JSON.stringify(arr));
}
function eventsForDate(key) {
  const builtin = (EVENTS[key] || []).map(e => ({...e, _builtin: true}));
  const custom = loadCustom().filter(e => e.date === key).map(e => ({
    id: e.id,
    person: PERSON_FROM_KEY[e.type] || "予定",
    summary: e.title,
    desc: e.desc,
    _builtin: false,
  }));
  return [...builtin, ...custom];
}

function pad(n) { return String(n).padStart(2,'0'); }
function dateKey(y,m,d) { return `${y}-${pad(m+1)}-${pad(d)}`; }
function uid() { return Date.now().toString(36) + Math.random().toString(36).slice(2, 7); }

function init() {
  const today = new Date();
  viewYear = today.getFullYear();
  viewMonth = today.getMonth();
  render();
  document.getElementById('prev').onclick = () => shift(-1);
  document.getElementById('next').onclick = () => shift(1);
  document.getElementById('today').onclick = () => { const t=new Date(); viewYear=t.getFullYear(); viewMonth=t.getMonth(); render(); };
  document.querySelectorAll('.chip').forEach(c => {
    c.onclick = () => {
      const k = c.dataset.key;
      filters[k] = !filters[k];
      c.classList.toggle('active');
      render();
    };
  });
  document.getElementById('fab').onclick = () => openForm(null, dateKey(viewYear, viewMonth, new Date().getDate()));
  document.getElementById('day-close').onclick = closeDaySheet;
  document.getElementById('day-overlay').onclick = e => { if (e.target.id==='day-overlay') closeDaySheet(); };
  document.getElementById('day-add').onclick = () => {
    const key = document.getElementById('day-overlay').dataset.dateKey;
    closeDaySheet();
    openForm(null, key);
  };
  document.getElementById('form-close').onclick = closeForm;
  document.getElementById('f-cancel').onclick = closeForm;
  document.getElementById('form-overlay').onclick = e => { if (e.target.id==='form-overlay') closeForm(); };
  document.getElementById('f-save').onclick = saveForm;
  document.getElementById('f-delete').onclick = deleteForm;
  document.querySelectorAll('.type-option').forEach(o => {
    o.onclick = () => {
      document.querySelectorAll('.type-option').forEach(x => x.classList.remove('selected'));
      o.classList.add('selected');
      formType = o.dataset.type;
    };
  });

  let swipeStart = null;
  document.body.addEventListener('touchstart', e => {
    if (e.target.closest('.sheet-overlay')) return;
    swipeStart = { x: e.touches[0].clientX, y: e.touches[0].clientY, time: Date.now() };
  }, { passive: true });
  document.body.addEventListener('touchend', e => {
    if (!swipeStart) return;
    const dx = e.changedTouches[0].clientX - swipeStart.x;
    const dy = e.changedTouches[0].clientY - swipeStart.y;
    const dt = Date.now() - swipeStart.time;
    if (dt < 400 && Math.abs(dx) > 80 && Math.abs(dy) < 50) {
      shift(dx < 0 ? 1 : -1);
    }
    swipeStart = null;
  }, { passive: true });
}

function shift(delta) {
  viewMonth += delta;
  if (viewMonth < 0) { viewMonth = 11; viewYear--; }
  if (viewMonth > 11) { viewMonth = 0; viewYear++; }
  render();
}

function render() {
  document.getElementById('year-label').textContent = `${viewYear}`;
  document.getElementById('month-label').textContent = `${viewMonth+1}月`;
  const first = new Date(viewYear, viewMonth, 1);
  const startWeekday = first.getDay();
  const daysInMonth = new Date(viewYear, viewMonth+1, 0).getDate();
  const prevDays = new Date(viewYear, viewMonth, 0).getDate();
  const today = new Date();
  const todayKey = dateKey(today.getFullYear(), today.getMonth(), today.getDate());

  const grid = document.getElementById('grid');
  grid.innerHTML = '';

  const totalCells = Math.ceil((startWeekday + daysInMonth) / 7) * 7;
  for (let i = 0; i < totalCells; i++) {
    const cell = document.createElement('div');
    cell.className = 'cell';
    let y, m, d;
    if (i < startWeekday) {
      d = prevDays - startWeekday + i + 1;
      m = viewMonth - 1; y = viewYear;
      if (m < 0) { m = 11; y--; }
      cell.classList.add('other-month');
    } else if (i >= startWeekday + daysInMonth) {
      d = i - startWeekday - daysInMonth + 1;
      m = viewMonth + 1; y = viewYear;
      if (m > 11) { m = 0; y++; }
      cell.classList.add('other-month');
    } else {
      d = i - startWeekday + 1;
      m = viewMonth; y = viewYear;
    }
    const key = dateKey(y, m, d);
    const weekday = i % 7;
    cell.classList.add('weekday-' + weekday);

    const num = document.createElement('div');
    num.className = 'date-num';
    if (weekday === 0) num.classList.add('sun');
    if (weekday === 6) num.classList.add('sat');
    if (HOLIDAYS.includes(key)) { num.classList.add('holiday'); cell.classList.add('is-holiday'); }
    num.textContent = d;
    if (key === todayKey) cell.classList.add('today');
    cell.appendChild(num);

    const dayEvents = eventsForDate(key).filter(e => filters[PERSON_KEY[e.person]]);
    dayEvents.slice(0, 3).forEach(e => {
      const ev = document.createElement('div');
      ev.className = 'event ' + PERSON_KEY[e.person];
      if (e.person === '給料') {
        ev.innerHTML = `<span class="event-label">${escapeHtml(e.summary)}</span>`;
      } else {
        ev.innerHTML = `<span class="event-name">${e.person}</span><span class="event-label">${escapeHtml(e.summary)}</span>`;
      }
      cell.appendChild(ev);
    });
    if (dayEvents.length > 3) {
      const more = document.createElement('div');
      more.className = 'more-events';
      more.textContent = `+${dayEvents.length - 3}件`;
      cell.appendChild(more);
    }

    cell.onclick = () => openDaySheet(key, y, m, d);
    grid.appendChild(cell);
  }
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function openDaySheet(key, y, m, d) {
  const wd = ['日','月','火','水','木','金','土'][new Date(y, m, d).getDay()];
  document.getElementById('day-title').textContent = `${m+1}月${d}日`;
  document.getElementById('day-subtitle').textContent = `${y}年 ${wd}曜日`;
  const body = document.getElementById('day-body');
  body.innerHTML = '';
  const events = eventsForDate(key);
  if (events.length === 0) {
    body.innerHTML = '<div class="empty">予定なし</div>';
  } else {
    events.forEach(e => {
      const cls = PERSON_KEY[e.person];
      const row = document.createElement('div');
      row.className = 'event-row';
      const actionsHtml = !e._builtin ? `
        <div class="actions">
          <button class="row-icon" data-edit="${e.id}" aria-label="編集">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
          </button>
        </div>` : '';
      row.innerHTML = `
        <div class="bullet ${cls}"></div>
        <div class="text-block">
          <div class="label">${escapeHtml(e.summary)}</div>
          <div class="meta">
            <span class="person-tag ${cls}">${e.person}</span>
            ${e.desc ? '<span>' + escapeHtml(e.desc) + '</span>' : ''}
          </div>
        </div>
        ${actionsHtml}
      `;
      body.appendChild(row);
    });
    body.querySelectorAll('[data-edit]').forEach(b => {
      b.onclick = (ev) => {
        ev.stopPropagation();
        const id = b.dataset.edit;
        closeDaySheet();
        openForm(id);
      };
    });
  }
  document.getElementById('day-overlay').dataset.dateKey = key;
  document.getElementById('day-overlay').classList.add('open');
}

function closeDaySheet() {
  document.getElementById('day-overlay').classList.remove('open');
}

function openForm(id, dateKeyHint) {
  editingId = id;
  document.getElementById('form-title').textContent = id ? '予定を編集' : '予定を追加';
  document.getElementById('f-delete').style.display = id ? 'flex' : 'none';

  let date, type, title, desc;
  if (id) {
    const item = loadCustom().find(e => e.id === id);
    if (!item) return;
    date = item.date;
    type = item.type;
    title = item.title;
    desc = item.desc || '';
  } else {
    date = dateKeyHint || dateKey(viewYear, viewMonth, new Date().getDate());
    type = 'custom';
    title = '';
    desc = '';
  }
  document.getElementById('f-date').value = date;
  document.getElementById('f-title').value = title;
  document.getElementById('f-desc').value = desc;
  formType = type;
  document.querySelectorAll('.type-option').forEach(o => {
    o.classList.toggle('selected', o.dataset.type === type);
  });
  document.getElementById('form-overlay').classList.add('open');
  setTimeout(() => document.getElementById('f-title').focus(), 240);
}

function closeForm() {
  document.getElementById('form-overlay').classList.remove('open');
  editingId = null;
}

function saveForm() {
  const date = document.getElementById('f-date').value;
  const title = document.getElementById('f-title').value.trim();
  const desc = document.getElementById('f-desc').value.trim();
  if (!date || !title) {
    document.getElementById('f-title').focus();
    return;
  }
  const arr = loadCustom();
  if (editingId) {
    const idx = arr.findIndex(e => e.id === editingId);
    if (idx >= 0) arr[idx] = { id: editingId, date, type: formType, title, desc };
  } else {
    arr.push({ id: uid(), date, type: formType, title, desc });
  }
  saveCustom(arr);
  closeForm();
  const [y, mm, d] = date.split('-').map(Number);
  viewYear = y; viewMonth = mm - 1;
  render();
  setTimeout(() => openDaySheet(date, y, mm - 1, d), 100);
}

function deleteForm() {
  if (!editingId) return;
  if (!confirm('この予定を削除します。よろしいですか?')) return;
  const arr = loadCustom().filter(e => e.id !== editingId);
  saveCustom(arr);
  const date = document.getElementById('f-date').value;
  closeForm();
  render();
  if (date) {
    const [y, mm, d] = date.split('-').map(Number);
    setTimeout(() => openDaySheet(date, y, mm - 1, d), 100);
  }
}

init();

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js').catch(()=>{});
}
</script>
</body>
</html>
"""

MANIFEST = {
    "name": "シフトカレンダー",
    "short_name": "シフト",
    "start_url": ".",
    "display": "standalone",
    "background_color": "#ffffff",
    "theme_color": "#ffffff",
    "orientation": "portrait",
    "icons": [
        {"src": "icon.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icon.png", "sizes": "512x512", "type": "image/png"},
    ],
}

SW = """const CACHE = 'shift-cal-v3';
self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(['./','./manifest.json'])));
});
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim())
  );
});
self.addEventListener('fetch', e => {
  e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
});
"""

HOLIDAYS_2026 = [
    "2026-01-01", "2026-01-12", "2026-02-11", "2026-02-23", "2026-03-20",
    "2026-04-29", "2026-05-03", "2026-05-04", "2026-05-05", "2026-05-06",
    "2026-07-20", "2026-08-11", "2026-09-21", "2026-09-23",
    "2026-10-12", "2026-11-03", "2026-11-23",
]


def main():
    if len(sys.argv) < 2:
        print("Usage: python build.py <xlsx_path>")
        sys.exit(1)
    xlsx = sys.argv[1]
    shift_events, year = parse_shift(xlsx)
    salary_events = build_salary_events(year)

    by_date = {}
    for name, d, label in shift_events:
        k = d.strftime("%Y-%m-%d")
        display_name = NAME_MAP.get(name, name)
        by_date.setdefault(k, []).append({"person": display_name, "summary": label})
    for d, title, desc in salary_events:
        k = d.strftime("%Y-%m-%d")
        by_date.setdefault(k, []).append({"person": "給料", "summary": title, "desc": desc})

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    html = TEMPLATE.replace("__EVENTS_JSON__", json.dumps(by_date, ensure_ascii=False))
    html = html.replace("__HOLIDAYS_JSON__", json.dumps(HOLIDAYS_2026))

    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    with open(os.path.join(OUTPUT_DIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(MANIFEST, f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUTPUT_DIR, "sw.js"), "w", encoding="utf-8") as f:
        f.write(SW)

    total_events = sum(len(v) for v in by_date.values())
    print(f"出力先: {OUTPUT_DIR}")
    print(f"  index.html ({total_events}件のイベント)")
    print(f"  manifest.json")
    print(f"  sw.js")


if __name__ == "__main__":
    main()
