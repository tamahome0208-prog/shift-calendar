"""シフトExcel -> 自己完結HTMLカレンダー生成 (v4)
- Keroppi-inspired premium design (custom SVG, Zen Maru Gothic font)
- Firebase Firestore real-time sync (localStorage fallback)
- Browser notification reminders
- Spring physics animations

Usage: python build.py "<xlsx>"
"""
import sys, os, json

sys.path.insert(0, r"C:\Users\tamah\Desktop\shift_to_ics")
from shift_to_ics import parse_shift, build_salary_events

OUTPUT_DIR = r"C:\Users\tamah\Desktop\shift_calendar"
NAME_MAP = {"安中": "こうき", "恩田": "ゆい"}

TEMPLATE = r"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#FFF8F0">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="シフト">
<title>シフトカレンダー</title>
<link rel="manifest" href="manifest.json">
<link rel="apple-touch-icon" href="icon.png">
<script src="firebase-config.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@500;700;900&family=Plus+Jakarta+Sans:wght@500;700;800&display=swap" rel="stylesheet">
<style>
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
* { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
html, body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-jp);
  font-weight: 500;
  min-height: 100vh;
  overscroll-behavior: none;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
body {
  padding-bottom: calc(var(--safe-bottom) + 96px);
  letter-spacing: 0.005em;
  background-image:
    radial-gradient(circle at 100% 0%, rgba(255, 184, 146, 0.08) 0%, transparent 36%),
    radial-gradient(circle at 0% 100%, rgba(247, 100, 162, 0.04) 0%, transparent 40%);
  background-attachment: fixed;
}
button { font-family: inherit; cursor: pointer; border: none; background: none; color: inherit; }
input, textarea, select { font-family: inherit; }

/* === SVG SPRITE (hidden defs) === */
.sprite { position: absolute; width: 0; height: 0; overflow: hidden; }

/* === HEADER === */
header {
  background: rgba(255, 248, 240, 0.78);
  backdrop-filter: saturate(180%) blur(30px);
  -webkit-backdrop-filter: saturate(180%) blur(30px);
  padding: calc(var(--safe-top) + 16px) 18px 14px;
  position: sticky;
  top: 0;
  z-index: 20;
  border-bottom: 1px solid var(--hairline);
}
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
.top-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.title-block {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}
.mascot {
  width: 46px;
  height: 46px;
  flex-shrink: 0;
  transform-origin: center bottom;
  animation: mascotBreath 4.2s ease-in-out infinite;
  filter: drop-shadow(0 2px 4px rgba(91, 165, 40, 0.18));
}
.mascot.hop { animation: mascotHop 0.7s var(--ease-spring); }
@keyframes mascotBreath {
  0%, 100% { transform: scale(1) translateY(0); }
  50% { transform: scale(1.03) translateY(-1px); }
}
@keyframes mascotHop {
  0% { transform: translateY(0) rotate(0deg) scale(1); }
  25% { transform: translateY(-10px) rotate(-10deg) scale(1.05); }
  50% { transform: translateY(-3px) rotate(6deg) scale(1.02); }
  75% { transform: translateY(-6px) rotate(-3deg) scale(1.03); }
  100% { transform: translateY(0) rotate(0deg) scale(1); }
}
.month-info {
  display: flex;
  align-items: baseline;
  gap: 6px;
  min-width: 0;
}
.year-label {
  font-family: var(--font-en);
  font-size: 11px;
  font-weight: 800;
  color: var(--muted-2);
  letter-spacing: 0.16em;
  text-transform: uppercase;
}
.month-label {
  font-size: 34px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.035em;
  line-height: 1;
}
.month-label .num { font-family: var(--font-en); font-weight: 800; }
.month-label .jp { font-weight: 800; opacity: 0.92; margin-left: -2px; }

.icon-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--text-2);
  transition: background 0.2s var(--ease-out), transform 0.18s var(--ease-spring);
  position: relative;
}
.icon-btn::before {
  content: '';
  position: absolute;
  inset: 6px;
  border-radius: 50%;
  background: transparent;
  transition: background 0.2s var(--ease-out);
}
.icon-btn:active { transform: scale(0.88); }
.icon-btn:active::before { background: var(--surface-2); }
.icon-btn:focus-visible { outline: 2px solid var(--leaf); outline-offset: 2px; }
.icon-btn svg { width: 22px; height: 22px; position: relative; z-index: 1; stroke-width: 2; }
.today-btn {
  background: var(--text);
  color: white;
  font-weight: 800;
  padding: 9px 16px 8px;
  border-radius: 999px;
  font-size: 12.5px;
  letter-spacing: 0.04em;
  box-shadow: var(--shadow-sm);
  transition: transform 0.15s var(--ease-spring), box-shadow 0.18s var(--ease-out);
  position: relative;
}
.today-btn::after {
  content: '';
  position: absolute;
  top: 8px;
  right: 8px;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--leaf);
  box-shadow: 0 0 0 2px var(--text);
}
.today-btn:active { transform: scale(0.94); }

.filters {
  display: flex;
  gap: 6px;
  margin-top: 12px;
  overflow-x: auto;
  scrollbar-width: none;
  padding: 2px 1px;
}
.filters::-webkit-scrollbar { display: none; }
.chip {
  padding: 9px 14px;
  min-height: 36px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
  user-select: none;
  border: 1.2px solid var(--border);
  background: var(--surface);
  color: var(--text-2);
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  flex-shrink: 0;
  cursor: pointer;
  transition: all 0.25s var(--ease-out);
  box-shadow: var(--shadow-xs);
}
.chip:active { transform: scale(0.94); }
.chip:focus-visible { outline: 2px solid var(--leaf); outline-offset: 2px; }
.chip .dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
  transition: background 0.22s var(--ease-out);
}
.chip:not(.active) { color: var(--muted); }
.chip:not(.active) .dot { opacity: 0.55; }
.chip[data-key="kouki"] { color: var(--kouki); }
.chip[data-key="kouki"].active { background: var(--kouki); color: white; border-color: var(--kouki); box-shadow: 0 4px 12px rgba(90, 166, 220, 0.3); }
.chip[data-key="yui"] { color: var(--yui); }
.chip[data-key="yui"].active { background: var(--yui); color: white; border-color: var(--yui); box-shadow: var(--shadow-pink); }
.chip[data-key="pay"] { color: var(--pay); }
.chip[data-key="pay"].active { background: var(--pay); color: white; border-color: var(--pay); box-shadow: var(--shadow-leaf); }
.chip[data-key="custom"] { color: var(--custom); }
.chip[data-key="custom"].active { background: var(--custom); color: white; border-color: var(--custom); box-shadow: 0 4px 12px rgba(197, 138, 224, 0.35); }
.chip.active .dot { background: white; }

/* === WEEKDAYS === */
.weekdays {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  padding: 18px 10px 10px;
  font-family: var(--font-en);
  font-size: 10.5px;
  font-weight: 800;
  text-align: center;
  color: var(--muted-2);
  letter-spacing: 0.16em;
  text-transform: uppercase;
}
.weekdays .sun { color: var(--cheek-deep); }
.weekdays .sat { color: var(--pond-dark); }

/* === GRID === */
.grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 6px;
  padding: 0 10px 18px;
}
.cell {
  background: var(--surface);
  min-height: 118px;
  min-width: 0;
  padding: 7px 5px 6px;
  display: flex;
  flex-direction: column;
  gap: 3px;
  border-radius: 14px;
  overflow: hidden;
  transition: transform 0.2s var(--ease-spring), background 0.2s var(--ease-out);
  position: relative;
  opacity: 0;
  animation: cellIn 0.4s var(--ease-out) forwards;
  box-shadow: var(--shadow-xs);
}
@keyframes cellIn {
  from { opacity: 0; transform: translateY(6px) scale(0.985); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
.cell:active { transform: scale(0.96); }
.cell.other-month {
  background: transparent;
  box-shadow: none;
}
.cell.other-month .date-num { color: var(--muted-2); opacity: 0.45; }
.cell.today {
  background: linear-gradient(180deg, #ffffff 0%, #F9FFF4 100%);
  box-shadow: 0 2px 8px rgba(91, 165, 40, 0.14), inset 0 0 0 1.5px var(--leaf);
}
.date-num {
  font-family: var(--font-en);
  font-size: 16px;
  font-weight: 800;
  height: 26px;
  display: flex;
  align-items: center;
  padding-left: 3px;
  color: var(--text);
  letter-spacing: -0.01em;
}
.cell.today .date-num {
  color: var(--leaf-deep);
  font-weight: 900;
  position: relative;
  padding-left: 3px;
}
.cell.today .date-num::after {
  content: '';
  display: inline-block;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--leaf);
  margin-left: 4px;
  margin-bottom: 8px;
  vertical-align: middle;
  animation: todayDot 2.4s ease-in-out infinite;
}
@keyframes todayDot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.4); }
}
.date-num.sun { color: var(--cheek-deep); }
.date-num.sat { color: var(--pond); }
.date-num.holiday { color: var(--cheek-deep); }
.date-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 24px;
  padding-right: 2px;
}
.weather-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  opacity: 0.9;
  filter: drop-shadow(0 1px 0 rgba(255, 255, 255, 0.5));
}
.cell.both-off .date-row .weather-icon { display: none; }
/* Day sheet 天気カード */
.day-weather {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 14px;
  background: linear-gradient(135deg, var(--water-mist) 0%, #ffffff 100%);
  border: 1.5px solid var(--pond-light);
  border-radius: 16px;
  margin-bottom: 10px;
}
.day-weather-icon { width: 36px; height: 36px; flex-shrink: 0; }
.day-weather-temp {
  font-family: var(--font-en);
  font-size: 17px;
  font-weight: 900;
  color: var(--text);
  line-height: 1.1;
}
.day-weather-rain {
  font-size: 11.5px;
  color: var(--muted);
  font-weight: 700;
  margin-top: 2px;
}
/* お祝いアニメ */
.celebration-overlay {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 49;
  overflow: hidden;
}
.celebration-heart {
  position: absolute;
  width: 26px;
  height: 26px;
  bottom: -30px;
  animation: floatUp 3.4s ease-out forwards;
  filter: drop-shadow(0 2px 4px rgba(255, 122, 165, 0.5));
}
@keyframes floatUp {
  0% { transform: translateY(0) rotate(0deg) scale(0.6); opacity: 0; }
  10% { opacity: 1; transform: translateY(-40px) rotate(-12deg) scale(1); }
  60% { transform: translateY(-50vh) rotate(15deg) scale(1.1); opacity: 0.9; }
  100% { transform: translateY(-100vh) rotate(-8deg) scale(0.8); opacity: 0; }
}

/* 保存マイクロアニメ */
.save-toast {
  position: fixed;
  bottom: 88px;
  left: 50%;
  transform: translateX(-50%) translateY(16px);
  background: var(--mint, #d4edda);
  color: var(--text-1, #3a3a3a);
  border: 1.5px solid var(--sage, #8fbc8f);
  border-radius: 40px;
  padding: 10px 22px 10px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  box-shadow: 0 4px 16px rgba(0,100,60,0.13);
  pointer-events: none;
  opacity: 0;
  z-index: 9999;
  animation: saveToastIn 1.8s ease forwards;
}
@keyframes saveToastIn {
  0%   { opacity: 0; transform: translateX(-50%) translateY(16px); }
  15%  { opacity: 1; transform: translateX(-50%) translateY(0); }
  75%  { opacity: 1; transform: translateX(-50%) translateY(0); }
  100% { opacity: 0; transform: translateX(-50%) translateY(-10px); }
}

/* 二人とも休み = ハスの葉でハート抱きしめ */
.cell.both-off {
  background:
    radial-gradient(ellipse at top right, rgba(255, 122, 165, 0.16) 0%, transparent 50%),
    linear-gradient(135deg, #FFF6FA 0%, #FBFFF6 60%, #F0F8E3 100%);
  border-color: var(--cheek);
}
.cell.both-off::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 38px;
  height: 38px;
  background:
    radial-gradient(ellipse at center, rgba(255, 217, 230, 0.7) 0%, transparent 65%);
  pointer-events: none;
}
.both-off-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 18px;
  height: 18px;
  pointer-events: none;
  animation: heartFloat 3.6s ease-in-out infinite;
  filter: drop-shadow(0 2px 3px rgba(255, 122, 165, 0.4));
}
@keyframes heartFloat {
  0%, 100% { transform: translateY(0) rotate(-6deg); }
  50% { transform: translateY(-2.5px) rotate(8deg); }
}

.event {
  padding: 4px 3px 4px 3px;
  border-radius: 7px;
  color: white;
  line-height: 1.1;
  min-width: 0;
  max-width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  letter-spacing: -0.03em;
  overflow: hidden;
  text-align: center;
  transition: transform 0.18s var(--ease-spring);
  position: relative;
  box-shadow: 0 1px 2px rgba(0,0,0,0.08);
  text-shadow: 0 1px 1px rgba(0,0,0,0.15);
}
.event-sticker {
  position: absolute;
  top: 1px;
  right: 1px;
  width: 10px;
  height: 10px;
  opacity: 0.92;
  filter: drop-shadow(0 1px 1px rgba(0,0,0,0.18));
  pointer-events: none;
  z-index: 1;
}
.event-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  min-width: 0;
}
.event:active { transform: scale(0.92); }
.event .event-name {
  font-size: 9px;
  font-weight: 800;
  opacity: 0.95;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  letter-spacing: 0;
  max-width: 100%;
}
.event .event-label {
  font-size: 11.5px;
  font-weight: 900;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 1px;
  max-width: 100%;
  letter-spacing: -0.03em;
}
.event.pay { padding: 4px 2px; box-shadow: inset 0 0 0 1px rgba(255,255,255,0.2); }
.event.pay .event-label { font-size: 10px; letter-spacing: -0.06em; }
.event.kouki { background: linear-gradient(135deg, var(--kouki) 0%, var(--pond-dark) 110%); }
.event.kouki.t-meeting { background: linear-gradient(135deg, var(--kouki-meeting) 0%, #1B5577 110%); }
.event.kouki.t-outing { background: linear-gradient(135deg, var(--kouki) 0%, var(--pond-dark) 110%); color: white; }
.event.kouki.t-outing .event-name { opacity: 0.9; color: white; }
.event.yui { background: linear-gradient(135deg, var(--yui) 0%, var(--yui-meeting) 110%); }
.event.yui.t-meeting { background: linear-gradient(135deg, var(--yui-meeting) 0%, #B91C5C 110%); }
.event.yui.t-outing { background: linear-gradient(135deg, var(--yui) 0%, var(--yui-meeting) 110%); color: white; }
.event.yui.t-outing .event-name { opacity: 0.9; color: white; }
/* A番(8:15~17:15シフト)— 黄色 */
.event.t-A {
  background: linear-gradient(135deg, #FCD34D 0%, #F59E0B 100%);
  color: #78350F;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.3);
}
.event.t-A .event-name { opacity: 0.9; color: #78350F; }
.event.t-A .event-label { color: #451A03; font-weight: 900; }
.event.pay { background: linear-gradient(135deg, var(--leaf) 0%, var(--leaf-dark) 100%); }
.event.custom { background: linear-gradient(135deg, var(--custom) 0%, #A372C6 110%); }
.more-events {
  font-size: 10px;
  color: var(--muted);
  font-weight: 700;
  padding: 0 4px;
  letter-spacing: 0;
}
.memo-chip {
  position: absolute;
  bottom: 3px;
  right: 4px;
  font-size: 14px;
  line-height: 1;
  filter: drop-shadow(0 1px 2px rgba(255, 122, 165, 0.35));
  pointer-events: none;
}
.memo-card {
  background: linear-gradient(135deg, #FFF6FA 0%, #FBFFF6 100%);
  border: 1.5px solid var(--cheek);
  border-radius: 16px;
  padding: 14px;
  margin-bottom: 14px;
}
.memo-card-title {
  font-size: 13px;
  font-weight: 900;
  color: #8E3958;
  margin-bottom: 10px;
  letter-spacing: 0.02em;
}
.memo-stamps {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}
.memo-stamp {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  border: 1.5px solid var(--border);
  background: var(--surface);
  font-size: 22px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.15s var(--ease-spring), border-color 0.18s var(--ease-out);
}
.memo-stamp:active { transform: scale(0.9); }
.memo-stamp.selected { border-color: var(--cheek-deep); background: var(--lily-pink); transform: scale(1.05); }
.memo-templates {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}
.memo-template {
  min-height: 44px;
  padding: 10px 16px;
  border-radius: 999px;
  border: 1.5px solid var(--border);
  background: var(--surface);
  font-size: 13px;
  font-weight: 700;
  color: var(--text-2);
  display: inline-flex;
  align-items: center;
}
.memo-template:active { transform: scale(0.95); }
.memo-textarea {
  width: 100%;
  min-height: 64px;
  font-family: inherit;
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: 12px;
  padding: 10px 12px;
  outline: none;
  resize: vertical;
  margin-bottom: 10px;
}
.memo-textarea:focus { border-color: var(--cheek-deep); }
.memo-actions { display: flex; justify-content: flex-end; }
.memo-actions .btn { width: auto; padding: 8px 18px; font-size: 13px; }

/* === HERO CARD === */
.hero-card {
  margin: 14px 14px 6px;
  padding: 18px 16px 16px;
  background:
    radial-gradient(120% 80% at 100% 0%, rgba(255, 183, 211, 0.14) 0%, transparent 50%),
    radial-gradient(120% 80% at 0% 100%, rgba(124, 194, 67, 0.10) 0%, transparent 50%),
    linear-gradient(180deg, #FFFFFF 0%, #FBFAF5 100%);
  border: 1px solid var(--hairline);
  border-radius: 24px;
  box-shadow: var(--shadow-md);
  position: relative;
  overflow: hidden;
  animation: heroIn 0.55s var(--ease-out);
}
.hero-card::before {
  content: '';
  position: absolute;
  inset: 0 0 auto 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.9), transparent);
}
@keyframes heroIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}
.hero-status {
  font-size: 13.5px;
  font-weight: 800;
  color: var(--muted);
  text-align: left;
  margin-bottom: 14px;
  line-height: 1.5;
  letter-spacing: 0.02em;
  padding: 0 2px;
  text-transform: none;
}
.hero-status.hot {
  background: linear-gradient(135deg, var(--cheek-deep) 0%, var(--yui-meeting) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 900;
  font-size: 15px;
  letter-spacing: -0.005em;
}
.hero-stats {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 9px;
}
.hero-stat {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--hairline);
  border-radius: 16px;
  padding: 12px 8px 10px;
  text-align: left;
  cursor: pointer;
  font-family: inherit;
  transition: transform 0.2s var(--ease-spring), box-shadow 0.22s var(--ease-out);
  min-height: 84px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
}
.hero-stat::before {
  content: '';
  position: absolute;
  top: 0;
  left: 12px;
  right: 12px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.9), transparent);
}
.hero-stat:active { transform: scale(0.95); box-shadow: var(--shadow-sm); }
.hero-stat-label {
  font-family: var(--font-en);
  font-size: 9.5px;
  color: var(--muted-2);
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}
.hero-stat-value {
  font-size: 26px;
  font-weight: 800;
  line-height: 1;
  font-family: var(--font-en);
  letter-spacing: -0.035em;
  margin-top: 4px;
}
.hero-stat-value .unit { font-size: 11px; font-weight: 700; margin-left: 1px; letter-spacing: 0; color: var(--muted); }
.hero-stat-sub {
  font-size: 10.5px;
  color: var(--muted);
  font-weight: 700;
  margin-top: 5px;
  font-family: var(--font-en);
  letter-spacing: 0.01em;
}
.hero-stat.date-stat .hero-stat-value { color: var(--cheek-deep); }
.hero-stat.salary-stat .hero-stat-value { color: var(--leaf-deep); }
.hero-stat.count-stat .hero-stat-value { color: var(--yui-meeting); }
.hero-stat.today-flag {
  background: linear-gradient(135deg, #FFF1F9 0%, #FFFBEB 100%);
  border-color: var(--cheek);
  animation: todayGlow 2.6s ease-in-out infinite;
}
@keyframes todayGlow {
  0%, 100% { box-shadow: 0 2px 8px rgba(255, 122, 165, 0.18); }
  50% { box-shadow: 0 4px 16px rgba(255, 122, 165, 0.32); }
}

/* === FAB === */
.fab {
  position: fixed;
  right: 18px;
  bottom: calc(var(--safe-bottom) + 18px);
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--leaf) 0%, var(--leaf-dark) 100%);
  color: white;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-leaf), 0 0 0 4px rgba(255,255,255,0.6);
  z-index: 30;
  transition: transform 0.2s var(--ease-spring), box-shadow 0.2s var(--ease-out);
}
.fab::before {
  content: '';
  position: absolute;
  inset: 4px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 28%, rgba(255,255,255,0.5) 0%, transparent 55%);
  pointer-events: none;
}
.fab:active { transform: scale(0.88) rotate(90deg); }
.fab svg { width: 28px; height: 28px; z-index: 1; }

/* === SHEET / MODAL === */
.sheet-overlay {
  position: fixed;
  inset: 0;
  background: rgba(26, 46, 5, 0.42);
  display: none;
  align-items: flex-end;
  justify-content: center;
  z-index: 50;
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}
.sheet-overlay.open { display: flex; animation: fadeIn 0.2s var(--ease-out); }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.sheet {
  background: var(--surface);
  width: 100%;
  max-width: 480px;
  border-radius: 28px 28px 0 0;
  padding: 10px 0 0;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.42s var(--ease-spring);
  box-shadow: var(--shadow-lg);
}
@keyframes slideUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}
.sheet-handle {
  width: 40px;
  height: 4px;
  background: var(--border-strong);
  border-radius: 999px;
  margin: 4px auto 10px;
}
.sheet-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 18px 14px;
  border-bottom: 1px solid var(--border);
}
.sheet-title {
  font-size: 19px;
  font-weight: 900;
  letter-spacing: -0.01em;
}
.sheet-title .num { font-family: var(--font-en); }
.sheet-subtitle {
  font-size: 12px;
  color: var(--muted);
  font-weight: 700;
  margin-top: 2px;
  letter-spacing: 0.02em;
}
.sheet-body {
  flex: 1;
  overflow-y: auto;
  padding: 14px 16px;
  -webkit-overflow-scrolling: touch;
}
.sheet-footer {
  padding: 12px 16px calc(16px + var(--safe-bottom));
  border-top: 1px solid var(--border);
  background: var(--surface);
}

.both-off-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  background: linear-gradient(135deg, var(--lily-pink) 0%, var(--belly) 100%);
  border: 1.5px solid var(--cheek);
  border-radius: 14px;
  margin-bottom: 14px;
  font-weight: 700;
  font-size: 14px;
  color: #8E3958;
}
.both-off-banner svg { width: 22px; height: 22px; flex-shrink: 0; }

.event-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 14px;
  border-radius: 16px;
  margin-bottom: 8px;
  background: var(--surface-soft);
  border: 1.5px solid var(--border);
  transition: transform 0.18s var(--ease-spring);
  animation: rowIn 0.32s var(--ease-out) backwards;
}
@keyframes rowIn {
  from { opacity: 0; transform: translateX(-8px); }
  to { opacity: 1; transform: translateX(0); }
}
.event-row:active { transform: scale(0.98); }
.event-row .bullet {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}
.event-row .bullet.kouki { background: var(--kouki); }
.event-row .bullet.yui { background: var(--yui); }
.event-row .bullet.pay { background: var(--pay); }
.event-row .bullet.custom { background: var(--custom); }
.event-row .text-block { flex: 1; min-width: 0; }
.event-row .label {
  font-size: 16px;
  font-weight: 900;
  color: var(--text);
  line-height: 1.3;
}
.event-row .meta {
  font-size: 12px;
  color: var(--muted);
  font-weight: 700;
  margin-top: 3px;
  display: flex;
  gap: 6px;
  align-items: center;
  flex-wrap: wrap;
}
.event-row .person-tag {
  font-size: 11px;
  font-weight: 900;
  padding: 3px 10px;
  border-radius: 999px;
  letter-spacing: 0.02em;
}
.event-row .person-tag.kouki { background: var(--kouki-soft); color: var(--kouki-meeting); }
.event-row .person-tag.yui { background: var(--yui-soft); color: var(--yui-meeting); }
.event-row .person-tag.pay { background: var(--pay-soft); color: var(--leaf-deep); }
.event-row .person-tag.custom { background: var(--custom-soft); color: #7C3DA0; }
.event-row .time { font-weight: 700; color: var(--text-2); font-family: var(--font-en); }
.event-row .actions { display: flex; gap: 4px; }
.row-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--muted);
  background: var(--surface);
  border: 1.5px solid var(--border);
  transition: background 0.18s var(--ease-out), transform 0.15s var(--ease-spring);
}
.row-icon:active { background: var(--surface-2); transform: scale(0.9); }
.row-icon svg { width: 18px; height: 18px; }
.empty {
  text-align: center;
  padding: 40px 16px;
  color: var(--muted);
  font-size: 14px;
  font-weight: 700;
}
.empty .lily { width: 56px; height: 56px; margin: 0 auto 10px; opacity: 0.5; }

/* === BUTTONS === */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 18px;
  border-radius: 16px;
  font-weight: 900;
  font-size: 15px;
  letter-spacing: 0;
  border: 1.5px solid transparent;
  transition: transform 0.15s var(--ease-spring), box-shadow 0.18s var(--ease-out);
  width: 100%;
  font-family: inherit;
}
.btn:active { transform: scale(0.97); }
.btn-primary {
  background: linear-gradient(135deg, var(--leaf) 0%, var(--leaf-dark) 100%);
  color: white;
  box-shadow: var(--shadow-leaf);
}
.btn-secondary { background: var(--surface); color: var(--text); border-color: var(--border-strong); }
.btn-danger { background: var(--surface); color: var(--cheek-deep); border-color: var(--cheek); }
.btn-row { display: flex; gap: 10px; }
.btn-row .btn { flex: 1; }
.btn svg { width: 18px; height: 18px; }

/* === FORM === */
.field {
  display: flex;
  flex-direction: column;
  gap: 7px;
  margin-bottom: 16px;
}
.field label {
  font-size: 12px;
  font-weight: 800;
  color: var(--muted);
  letter-spacing: 0.06em;
}
.field input, .field textarea, .field select {
  font-size: 15px;
  font-weight: 700;
  color: var(--text);
  background: var(--surface-soft);
  border: 1.5px solid var(--border);
  border-radius: 14px;
  padding: 14px 16px;
  width: 100%;
  outline: none;
  transition: border 0.18s var(--ease-out), background 0.18s var(--ease-out);
  -webkit-appearance: none;
  appearance: none;
}
.field input:focus, .field textarea:focus, .field select:focus {
  border-color: var(--leaf);
  background: var(--surface);
  box-shadow: 0 0 0 3px rgba(124, 194, 67, 0.15);
}
.field textarea { resize: vertical; min-height: 70px; }
.field-row { display: flex; gap: 10px; }
.field-row .field { flex: 1; }

.type-picker, .reminder-picker {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
}
.reminder-picker { grid-template-columns: repeat(2, 1fr); }
.type-option, .reminder-option {
  padding: 12px 8px;
  border-radius: 14px;
  border: 1.5px solid var(--border);
  background: var(--surface);
  font-weight: 800;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: var(--text-2);
  transition: all 0.22s var(--ease-out);
}
.type-option:active, .reminder-option:active { transform: scale(0.95); }
.type-option .dot { width: 9px; height: 9px; border-radius: 50%; }
.type-option[data-type="kouki"] .dot { background: var(--kouki); }
.type-option[data-type="yui"] .dot { background: var(--yui); }
.type-option[data-type="custom"] .dot { background: var(--custom); }
.type-option.selected[data-type="kouki"] { background: var(--kouki); color: white; border-color: var(--kouki); }
.type-option.selected[data-type="yui"] { background: var(--yui); color: white; border-color: var(--yui); }
.type-option.selected[data-type="custom"] { background: var(--custom); color: white; border-color: var(--custom); }
.type-option.selected .dot { background: white; }
.reminder-option.selected { background: var(--leaf); color: white; border-color: var(--leaf); }

.time-toggle {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  background: var(--surface-soft);
  border: 1.5px solid var(--border);
  border-radius: 14px;
  font-weight: 800;
  font-size: 14px;
}
.toggle {
  position: relative;
  width: 44px;
  height: 26px;
  background: var(--border-strong);
  border-radius: 999px;
  cursor: pointer;
  transition: background 0.22s var(--ease-out);
  flex-shrink: 0;
  margin-left: auto;
}
.toggle::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  transition: transform 0.22s var(--ease-spring);
  box-shadow: var(--shadow-sm);
}
.toggle.on { background: var(--leaf); }
.toggle.on::after { transform: translateX(18px); }

/* === SYNC STATUS === */
.sync-indicator {
  position: fixed;
  top: calc(var(--safe-top) + 10px);
  right: 14px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--muted);
  z-index: 30;
  opacity: 0;
  transition: opacity 0.3s, background 0.3s;
}
.sync-indicator.online { background: var(--leaf); opacity: 0.8; }
.sync-indicator.syncing {
  background: var(--leaf);
  opacity: 1;
  animation: syncPulse 1s ease-in-out infinite;
}
.sync-indicator.offline { background: var(--muted); opacity: 0.6; }
@keyframes syncPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.4); }
}

/* === SETTINGS LINK === */
.settings-strip {
  padding: 0 16px;
  margin-top: 8px;
}
.settings-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  background: var(--surface-soft);
  border: 1px solid var(--border);
  border-radius: 14px;
  font-weight: 700;
  font-size: 14px;
  color: var(--text-2);
  margin-bottom: 8px;
  transition: background 0.18s var(--ease-out);
}
.settings-row:active { background: var(--surface-2); }
.settings-row svg { width: 18px; height: 18px; color: var(--muted); }

.notice-banner {
  margin: 0 16px 12px;
  padding: 12px 14px;
  background: linear-gradient(135deg, var(--belly) 0%, var(--lily-pink) 100%);
  border: 1.5px solid var(--cheek);
  border-radius: 14px;
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
  display: flex;
  align-items: center;
  gap: 10px;
}
.notice-banner svg { width: 22px; height: 22px; flex-shrink: 0; }
.notice-banner button {
  margin-left: auto;
  background: var(--leaf);
  color: white;
  padding: 6px 12px;
  border-radius: 999px;
  font-weight: 800;
  font-size: 12px;
}
.anniv-list { display: flex; flex-direction: column; gap: 6px; margin-bottom: 8px; }
.anniv-row {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px;
  background: var(--surface-soft);
  border: 1px solid var(--border);
  border-radius: 12px;
  font-size: 13px; font-weight: 700;
}
.anniv-row .anniv-name { flex: 1; color: var(--text); }
.anniv-row .anniv-date { font-family: var(--font-en); color: var(--cheek-deep); font-weight: 800; }
.anniv-row .anniv-del {
  width: 28px; height: 28px; border-radius: 8px;
  background: var(--surface); border: 1px solid var(--border);
  color: var(--muted); font-size: 14px; cursor: pointer;
}
.anniv-row .anniv-del:active { transform: scale(0.92); }

.recall-card {
  margin: 6px 14px 6px;
  background: var(--surface);
  border: 1px solid var(--hairline);
  border-radius: 18px;
  overflow: hidden;
  box-shadow: var(--shadow-xs);
}
.recall-header {
  display: flex; align-items: center; gap: 10px;
  width: 100%; padding: 12px 16px;
  background: transparent; border: none; cursor: pointer;
  font-family: inherit; text-align: left;
}
.recall-header:active { background: var(--surface-soft); }
.recall-label {
  flex: 1; font-size: 13px; font-weight: 800;
  color: var(--text-2); letter-spacing: 0.04em;
}
.recall-count {
  font-family: var(--font-en); font-size: 11px; font-weight: 800;
  padding: 2px 8px; background: var(--cheek); color: white;
  border-radius: 999px; letter-spacing: 0;
}
.recall-chevron {
  width: 16px; height: 16px; color: var(--muted);
  transition: transform 0.2s var(--ease-out);
}
.recall-header[aria-expanded="true"] .recall-chevron { transform: rotate(180deg); }
.recall-body {
  padding: 0 16px 14px;
  display: flex; flex-direction: column; gap: 8px;
}
.recall-item {
  padding: 10px 12px;
  background: var(--surface-soft); border-radius: 12px;
  font-size: 13px; font-weight: 600;
  color: var(--text-2); line-height: 1.5;
}
.recall-item-when {
  font-family: var(--font-en); font-size: 11px; font-weight: 800;
  color: var(--muted); letter-spacing: 0.06em;
  margin-bottom: 4px; display: block;
}
.year-grid { display: flex; flex-direction: column; gap: 6px; }
.year-month-row { display: flex; align-items: center; gap: 6px; }
.year-month-label {
  font-family: var(--font-en); font-size: 10px; font-weight: 800;
  color: var(--muted); letter-spacing: 0.06em;
  width: 26px; flex-shrink: 0;
}
.year-cells { display: grid; grid-template-columns: repeat(31, 1fr); gap: 2px; flex: 1; }
.year-cell {
  aspect-ratio: 1;
  background: var(--surface);
  border: 0.5px solid var(--border);
  border-radius: 2px;
  position: relative;
  cursor: pointer;
  padding: 0;
}
.year-cell.empty { visibility: hidden; cursor: default; }
.year-cell.full { background: var(--cheek-deep); border-color: var(--cheek-deep); }
.year-cell.half { background: var(--cheek); border-color: var(--cheek); }
.year-cell.a::after {
  content: ''; position: absolute; inset: -1px;
  border: 1.5px solid #F59E0B; border-radius: 3px;
}
.year-cell.pay::before {
  content: ''; position: absolute; bottom: 1px; right: 1px;
  width: 3px; height: 3px;
  background: var(--leaf); border-radius: 50%;
}
.year-legend {
  display: flex; gap: 14px; flex-wrap: wrap; justify-content: center;
  margin-top: 16px; font-size: 11px; font-weight: 700; color: var(--muted);
}
.year-leg { display: inline-flex; align-items: center; gap: 5px; }
.year-swatch { width: 12px; height: 12px; border-radius: 3px; display: inline-block; }
.year-swatch.full { background: var(--cheek-deep); }
.year-swatch.half { background: var(--cheek); }
.year-swatch.a { background: white; border: 1.5px solid #F59E0B; }
.year-swatch.pay { background: var(--leaf); border-radius: 50%; }
.history-section-title {
  font-size: 13px; font-weight: 800; color: var(--muted);
  letter-spacing: 0.06em; margin: 14px 0 6px;
  display: flex; align-items: center; gap: 6px;
}
.history-divider {
  text-align: center; font-size: 11px; font-weight: 800;
  color: var(--cheek-deep); letter-spacing: 0.1em;
  padding: 12px 0; position: relative;
}
.history-divider::before, .history-divider::after {
  content: ''; position: absolute; top: 50%;
  width: calc(50% - 60px); height: 1px; background: var(--border);
}
.history-divider::before { left: 0; }
.history-divider::after { right: 0; }
.history-card {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 14px; background: var(--surface-soft);
  border: 1px solid var(--border); border-radius: 14px;
  margin-bottom: 8px;
  transition: transform 0.15s var(--ease-spring);
  cursor: pointer;
}
.history-card:active { transform: scale(0.98); }
.history-card.past { opacity: 0.78; }
.history-card-body { flex: 1; min-width: 0; }
.history-card-meta {
  font-size: 11px; font-weight: 700; color: var(--muted);
  margin-top: 3px; display: flex; gap: 6px; align-items: center;
}
.history-card-date {
  font-family: var(--font-en); font-weight: 800;
  color: var(--text-2); font-size: 12px;
}
.history-card-title {
  font-size: 14px; font-weight: 800; color: var(--text);
  margin-top: 2px;
}
.history-card-time {
  font-family: var(--font-en); font-weight: 700;
  color: var(--muted); font-size: 12px; margin-left: 4px;
}
.history-empty {
  text-align: center; padding: 32px 16px;
  color: var(--muted); font-weight: 700;
}
.history-counts {
  font-size: 12px; font-weight: 700; color: var(--muted);
  padding: 6px 16px 8px; border-bottom: 1px solid var(--border);
}
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
.anniv-chip svg { width: 12px; height: 12px; flex-shrink: 0; }
.anniv-chip span { overflow: hidden; text-overflow: ellipsis; min-width: 0; }
.anniv-chip.t-birth { background: linear-gradient(135deg, var(--cheek) 0%, var(--cheek-deep) 100%); }
.anniv-chip.t-anniv { background: linear-gradient(135deg, var(--yui) 0%, var(--yui-meeting) 100%); }
.anniv-chip.t-other { background: linear-gradient(135deg, var(--custom) 0%, #A372C6 100%); }

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
</style>
</head>
<body>

<!-- SVG sprites -->
<svg class="sprite" aria-hidden="true">
  <defs>
    <!-- Keroppi-inspired Frog mascot -->
    <symbol id="frog" viewBox="0 0 48 48">
      <!-- Body -->
      <ellipse cx="24" cy="30" rx="17" ry="13" fill="#7CC243"/>
      <!-- Belly -->
      <ellipse cx="24" cy="33" rx="11" ry="7" fill="#FDF6D8"/>
      <!-- Left eye bulge -->
      <circle cx="16" cy="16" r="7" fill="#7CC243"/>
      <!-- Right eye bulge -->
      <circle cx="32" cy="16" r="7" fill="#7CC243"/>
      <!-- Left eye white -->
      <circle cx="16" cy="16" r="4.5" fill="white"/>
      <!-- Right eye white -->
      <circle cx="32" cy="16" r="4.5" fill="white"/>
      <!-- Left pupil -->
      <circle cx="17" cy="17" r="2.2" fill="#1a2e05"/>
      <!-- Right pupil -->
      <circle cx="33" cy="17" r="2.2" fill="#1a2e05"/>
      <!-- Eye sparkles -->
      <circle cx="17.8" cy="16" r="0.8" fill="white"/>
      <circle cx="33.8" cy="16" r="0.8" fill="white"/>
      <!-- Mouth (smile) -->
      <path d="M 18 32 Q 24 36 30 32" stroke="#1a2e05" stroke-width="1.4" fill="none" stroke-linecap="round"/>
      <!-- Cheeks -->
      <ellipse cx="11" cy="28" rx="2.6" ry="2" fill="#FFB7D3" opacity="0.85"/>
      <ellipse cx="37" cy="28" rx="2.6" ry="2" fill="#FFB7D3" opacity="0.85"/>
    </symbol>
    <!-- Lily pad -->
    <symbol id="lily" viewBox="0 0 64 64">
      <path d="M 32 8 C 12 12 8 28 12 44 C 16 56 32 60 32 60 C 32 60 48 56 52 44 C 56 28 52 12 32 8 Z M 32 8 L 32 60" fill="#7CC243"/>
      <path d="M 32 8 C 20 14 16 28 18 42" stroke="#5BA528" stroke-width="0.6" fill="none" opacity="0.7"/>
      <path d="M 32 8 C 44 14 48 28 46 42" stroke="#5BA528" stroke-width="0.6" fill="none" opacity="0.7"/>
      <circle cx="32" cy="32" r="3" fill="#FFD9E6"/>
    </symbol>
    <!-- Heart -->
    <symbol id="heart" viewBox="0 0 24 24">
      <path d="M 12 21.5 C 8 17.5 3 14.5 3 9 C 3 6 5.5 4 8 4 C 9.8 4 11 5 12 6.6 C 13 5 14.2 4 16 4 C 18.5 4 21 6 21 9 C 21 14.5 16 17.5 12 21.5 Z" fill="#FF7AA5"/>
      <path d="M 7 8 Q 9 6.5 11 8" stroke="white" stroke-width="0.8" fill="none" stroke-linecap="round" opacity="0.5"/>
    </symbol>
    <!-- Plus -->
    <symbol id="i-plus" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/></symbol>
    <symbol id="i-x" viewBox="0 0 24 24"><path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></symbol>
    <symbol id="i-left" viewBox="0 0 24 24"><path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/></symbol>
    <symbol id="i-right" viewBox="0 0 24 24"><path d="M9 6l6 6-6 6" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/></symbol>
    <symbol id="i-edit" viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></symbol>
    <symbol id="i-bell" viewBox="0 0 24 24"><path d="M18 8a6 6 0 1 0-12 0c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 0 1-3.46 0" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></symbol>
    <symbol id="i-cloud" viewBox="0 0 24 24"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></symbol>
    <symbol id="i-grid" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="2" fill="none"/><rect x="14" y="3" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="2" fill="none"/><rect x="3" y="14" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="2" fill="none"/><rect x="14" y="14" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="2" fill="none"/></symbol>
    <symbol id="i-settings" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" fill="none"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></symbol>
    <symbol id="i-clock" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/><polyline points="12 6 12 12 16 14" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/></symbol>
    <symbol id="i-note" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z M14 2v6h6 M16 13H8 M16 17H8 M10 9H8" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></symbol>
    <!-- 天気アイコン -->
    <symbol id="w-sunny" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="4.2" fill="#FCD34D" stroke="#F59E0B" stroke-width="0.5"/>
      <g stroke="#F59E0B" stroke-width="1.7" stroke-linecap="round">
        <line x1="12" y1="2.8" x2="12" y2="4.6"/>
        <line x1="12" y1="19.4" x2="12" y2="21.2"/>
        <line x1="2.8" y1="12" x2="4.6" y2="12"/>
        <line x1="19.4" y1="12" x2="21.2" y2="12"/>
        <line x1="5.4" y1="5.4" x2="6.7" y2="6.7"/>
        <line x1="17.3" y1="17.3" x2="18.6" y2="18.6"/>
        <line x1="5.4" y1="18.6" x2="6.7" y2="17.3"/>
        <line x1="17.3" y1="6.7" x2="18.6" y2="5.4"/>
      </g>
    </symbol>
    <symbol id="w-partly" viewBox="0 0 24 24">
      <circle cx="8" cy="8" r="3.4" fill="#FCD34D" stroke="#F59E0B" stroke-width="0.4"/>
      <g stroke="#F59E0B" stroke-width="1.2" stroke-linecap="round">
        <line x1="8" y1="2.3" x2="8" y2="3.4"/>
        <line x1="2.3" y1="8" x2="3.4" y2="8"/>
        <line x1="4" y1="4" x2="4.8" y2="4.8"/>
      </g>
      <path d="M 7.5 16 a 4 4 0 0 1 4-4 a 4.5 4.5 0 0 1 9 0.5 a 3 3 0 0 1 -1.5 5.5 h-11 a 3.2 3.2 0 0 1 -0.5 -2 z" fill="#E2E8F0" stroke="#94A3B8" stroke-width="0.7" stroke-linejoin="round"/>
    </symbol>
    <symbol id="w-cloudy" viewBox="0 0 24 24">
      <path d="M 5 16 a 4 4 0 0 1 4-4 a 4.5 4.5 0 0 1 9 0.5 a 3.2 3.2 0 0 1 -1.5 5.5 h-11 a 3.2 3.2 0 0 1 -0.5 -2 z" fill="#CBD5E1" stroke="#94A3B8" stroke-width="0.7" stroke-linejoin="round"/>
    </symbol>
    <symbol id="w-rainy" viewBox="0 0 24 24">
      <path d="M 5 11 a 4 4 0 0 1 4-4 a 4.5 4.5 0 0 1 9 0.5 a 3.2 3.2 0 0 1 -1.5 5.5 h-11 a 3.2 3.2 0 0 1 -0.5 -2 z" fill="#94A3B8" stroke="#64748B" stroke-width="0.6"/>
      <g stroke="#3B82F6" stroke-width="1.6" stroke-linecap="round">
        <line x1="8" y1="15" x2="7" y2="18.5"/>
        <line x1="12" y1="15" x2="11" y2="18.5"/>
        <line x1="16" y1="15" x2="15" y2="18.5"/>
      </g>
    </symbol>
    <symbol id="w-snowy" viewBox="0 0 24 24">
      <path d="M 5 11 a 4 4 0 0 1 4-4 a 4.5 4.5 0 0 1 9 0.5 a 3.2 3.2 0 0 1 -1.5 5.5 h-11 a 3.2 3.2 0 0 1 -0.5 -2 z" fill="#E0E7EB" stroke="#94A3B8" stroke-width="0.6"/>
      <g fill="#60A5FA">
        <circle cx="8" cy="17" r="0.9"/>
        <circle cx="12" cy="19" r="0.9"/>
        <circle cx="16" cy="17" r="0.9"/>
      </g>
    </symbol>
    <symbol id="w-thundery" viewBox="0 0 24 24">
      <path d="M 5 11 a 4 4 0 0 1 4-4 a 4.5 4.5 0 0 1 9 0.5 a 3.2 3.2 0 0 1 -1.5 5.5 h-11 a 3.2 3.2 0 0 1 -0.5 -2 z" fill="#475569"/>
      <polygon points="12,12 9,18 11.5,18 10,22 14.5,15.5 12,15.5" fill="#FCD34D" stroke="#D97706" stroke-width="0.4" stroke-linejoin="round"/>
    </symbol>
    <symbol id="w-foggy" viewBox="0 0 24 24">
      <g stroke="#94A3B8" stroke-width="1.8" stroke-linecap="round">
        <line x1="4" y1="8" x2="20" y2="8"/>
        <line x1="6" y1="12" x2="18" y2="12"/>
        <line x1="3" y1="16" x2="21" y2="16"/>
        <line x1="6" y1="20" x2="18" y2="20"/>
      </g>
    </symbol>
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
    <symbol id="st-cake" viewBox="0 0 24 24">
      <rect x="4" y="12" width="16" height="9" rx="1.5" fill="#FFD9E6" stroke="#F764A2" stroke-width="0.8"/>
      <path d="M 4 15 Q 8 17 12 15 Q 16 17 20 15" stroke="#F764A2" stroke-width="1" fill="none"/>
      <rect x="11" y="6" width="2" height="6" fill="#FBBF24" rx="0.5"/>
      <path d="M12 4 L 12.5 6 L 11.5 6 Z" fill="#FF8E5C"/>
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
  </defs>
</svg>

<div class="sync-indicator" id="sync-indicator" title="同期状態"></div>

<header>
  <div class="header-deco" aria-hidden="true">
    <svg class="deco-cloud-1"><use href="#deco-cloud"/></svg>
    <svg class="deco-leaf-1"><use href="#deco-leaf-small"/></svg>
  </div>
  <div class="top-row">
    <div class="title-block">
      <svg class="mascot" id="mascot"><use href="#frog"/></svg>
      <div class="month-info">
        <div class="month-label"><span class="num" id="month-num"></span><span class="jp">月</span></div>
        <div class="year-label" id="year-label"></div>
      </div>
    </div>
    <button class="today-btn" id="today">今日</button>
    <button class="icon-btn" id="prev" aria-label="前月">
      <svg><use href="#i-left"/></svg>
    </button>
    <button class="icon-btn" id="next" aria-label="次月">
      <svg><use href="#i-right"/></svg>
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
    <div class="chip active" data-key="kouki" role="switch" aria-checked="true" tabindex="0"><span class="dot"></span>こうき</div>
    <div class="chip active" data-key="yui" role="switch" aria-checked="true" tabindex="0"><span class="dot"></span>ゆい</div>
    <div class="chip active" data-key="pay" role="switch" aria-checked="true" tabindex="0"><span class="dot"></span>給料日</div>
    <div class="chip active" data-key="custom" role="switch" aria-checked="true" tabindex="0"><span class="dot"></span>予定</div>
    <button class="chip" id="year-btn" type="button" aria-label="年間ビュー" style="background:var(--surface);color:var(--text-2);border-color:var(--border);">
      <svg style="width:14px;height:14px;"><use href="#i-grid"/></svg>
      年
    </button>
    <button class="chip" id="history-btn" type="button" aria-label="予定リスト" style="background:var(--surface);color:var(--text-2);border-color:var(--border);">
      <svg style="width:14px;height:14px;"><use href="#i-clock"/></svg>
      履歴
    </button>
  </div>
</header>

<div id="notice-area"></div>

<section class="hero-card" id="hero-card">
  <div class="hero-status" id="hero-status">…</div>
  <div class="hero-stats">
    <button class="hero-stat date-stat" id="hero-stat-date" type="button" aria-label="次のデート日にジャンプ">
      <div class="hero-stat-label">NEXT DATE</div>
      <div class="hero-stat-value" id="hero-stat-date-value">—</div>
      <div class="hero-stat-sub" id="hero-stat-date-sub"></div>
    </button>
    <button class="hero-stat salary-stat" id="hero-stat-salary" type="button" aria-label="次の給料日にジャンプ">
      <div class="hero-stat-label">NEXT 給料</div>
      <div class="hero-stat-value" id="hero-stat-salary-value">—</div>
      <div class="hero-stat-sub" id="hero-stat-salary-sub"></div>
    </button>
    <button class="hero-stat count-stat" id="hero-stat-count" type="button" aria-label="この月のデート可能日数">
      <div class="hero-stat-label">今月デート</div>
      <div class="hero-stat-value" id="hero-stat-count-value">—</div>
      <div class="hero-stat-sub">回</div>
    </button>
  </div>
</section>

<section class="recall-card" id="recall-card" hidden>
  <button class="recall-header" id="recall-toggle" type="button" aria-expanded="false">
    <span class="recall-label">ふりかえり</span>
    <span class="recall-count" id="recall-count">0</span>
    <svg class="recall-chevron" viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/></svg>
  </button>
  <div class="recall-body" id="recall-body" hidden></div>
</section>

<div class="weekdays">
  <div class="sun">SUN</div><div>MON</div><div>TUE</div><div>WED</div><div>THU</div><div>FRI</div><div class="sat">SAT</div>
</div>
<div class="grid" id="grid"></div>

<div class="settings-strip">
  <div class="settings-row" id="settings-btn">
    <span>同期と通知の設定</span>
    <svg><use href="#i-settings"/></svg>
  </div>
</div>

<button class="fab" id="fab" aria-label="予定を追加">
  <svg><use href="#i-plus"/></svg>
</button>

<!-- Day Detail Sheet -->
<div class="sheet-overlay" id="day-overlay" role="dialog" aria-modal="true" aria-labelledby="day-title" aria-hidden="true">
  <div class="sheet">
    <div class="sheet-handle"></div>
    <div class="sheet-header">
      <div>
        <div class="sheet-title" id="day-title"></div>
        <div class="sheet-subtitle" id="day-subtitle"></div>
      </div>
      <button class="icon-btn" id="day-close" aria-label="閉じる">
        <svg><use href="#i-x"/></svg>
      </button>
    </div>
    <div class="sheet-body" id="day-body"></div>
    <div class="sheet-footer">
      <button class="btn btn-primary" id="day-add">
        <svg><use href="#i-plus"/></svg>
        この日に予定を追加
      </button>
    </div>
  </div>
</div>

<!-- Form Sheet -->
<div class="sheet-overlay" id="form-overlay" role="dialog" aria-modal="true" aria-labelledby="form-title" aria-hidden="true">
  <div class="sheet">
    <div class="sheet-handle"></div>
    <div class="sheet-header">
      <div class="sheet-title" id="form-title">予定を追加</div>
      <button class="icon-btn" id="form-close" aria-label="閉じる">
        <svg><use href="#i-x"/></svg>
      </button>
    </div>
    <div class="sheet-body">
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
        <label>日付</label>
        <input type="date" id="f-date">
      </div>
      <div class="time-toggle">
        <svg style="width:18px;height:18px;color:var(--muted);"><use href="#i-clock"/></svg>
        <span>時刻を指定</span>
        <div class="toggle" id="f-time-toggle"></div>
      </div>
      <div id="f-time-fields" style="display:none; margin-top: 12px;">
        <div class="field-row">
          <div class="field">
            <label>開始</label>
            <input type="time" id="f-start" value="10:00">
          </div>
          <div class="field">
            <label>終了</label>
            <input type="time" id="f-end" value="11:00">
          </div>
        </div>
      </div>
      <div class="field" style="margin-top: 4px;">
        <label>リマインダー</label>
        <div class="reminder-picker">
          <div class="reminder-option selected" data-min="0">なし</div>
          <div class="reminder-option" data-min="30">30分前</div>
          <div class="reminder-option" data-min="60">1時間前</div>
          <div class="reminder-option" data-min="1440">1日前</div>
        </div>
      </div>
      <div class="field">
        <label>メモ</label>
        <textarea id="f-desc" placeholder="任意のメモ"></textarea>
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

<!-- Settings Sheet -->
<div class="sheet-overlay" id="settings-overlay" role="dialog" aria-modal="true" aria-hidden="true">
  <div class="sheet">
    <div class="sheet-handle"></div>
    <div class="sheet-header">
      <div class="sheet-title">設定</div>
      <button class="icon-btn" id="settings-close" aria-label="閉じる">
        <svg><use href="#i-x"/></svg>
      </button>
    </div>
    <div class="sheet-body">
      <div class="field">
        <label style="display:flex;align-items:center;gap:6px;"><svg style="width:16px;height:16px;"><use href="#i-cloud"/></svg> Firebase 設定 (同期用)</label>
        <textarea id="fb-config" placeholder='Firebaseコンソールからコピーしたconfig JSON を貼り付け' style="min-height: 140px; font-family: ui-monospace, monospace; font-size: 12px;"></textarea>
        <div style="font-size: 12px; color: var(--muted); margin-top: 4px;">空欄=この端末のみ保存 / 入力=2台で自動同期</div>
      </div>
      <div class="field">
        <label style="display:flex;align-items:center;gap:6px;">毎年の予定(誕生日・記念日など)</label>
        <div id="anniv-list" class="anniv-list"></div>
        <div id="anniv-add-area">
          <button class="btn btn-secondary" id="anniv-add-toggle" type="button" style="font-size:13px;padding:10px;">+ 追加</button>
        </div>
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
      </div>
      <div class="field">
        <label style="display:flex;align-items:center;gap:6px;"><svg style="width:16px;height:16px;"><use href="#i-bell"/></svg> ブラウザ通知</label>
        <button class="btn btn-secondary" id="enable-notif" style="font-size:14px;padding:11px;">通知を許可する</button>
        <div id="notif-status" style="font-size: 12px; color: var(--muted); margin-top: 4px;"></div>
      </div>
    </div>
    <div class="sheet-footer">
      <div class="btn-row">
        <button class="btn btn-secondary" id="settings-cancel">閉じる</button>
        <button class="btn btn-primary" id="settings-save">保存</button>
      </div>
    </div>
  </div>
</div>

<!-- Confirm Sheet -->
<div class="sheet-overlay" id="confirm-overlay" role="dialog" aria-modal="true" aria-labelledby="confirm-title" aria-hidden="true">
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

<!-- Year View Sheet -->
<div class="sheet-overlay" id="year-overlay" role="dialog" aria-modal="true" aria-labelledby="year-title" aria-hidden="true">
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

<script type="module">
const EVENTS = __EVENTS_JSON__;
const HOLIDAYS_BY_YEAR = __HOLIDAYS_JSON__;

const PERSON_KEY = {"こうき":"kouki","ゆい":"yui","給料":"pay","予定":"custom"};
const PERSON_FROM_KEY = {kouki:"こうき", yui:"ゆい", pay:"給料", custom:"予定"};
const filters = { kouki: true, yui: true, pay: true, custom: true };
const REST_LABELS = ['休', '希望休', '有'];
const MEETING_LABELS = ['会議', 'MTG', 'ミーティング'];
const OUTING_LABELS = ['出店'];
const A_SHIFT_LABELS = ['A', 'Ａ', 'A番'];
const LS_CUSTOM = 'shift-cal-custom-v2';
const LS_FBCONFIG = 'shift-cal-fb-config';
const LS_REMINDERS = 'shift-cal-reminder-state';
const LS_WEATHER = 'shift-cal-weather-v1';
const LS_ANNIV = 'shift-cal-anniversaries-v1';
const LS_LAST_VIEW = 'shift-cal-last-view-v1';
let allAnniversaries = [];
let unsubscribeAnniv = null;
const WEATHER_TTL_MS = 6 * 60 * 60 * 1000; // 6時間キャッシュ
const NOBORIBETSU_LAT = 42.42;
const NOBORIBETSU_LON = 141.11;
let weatherData = {};

async function fetchWeather() {
  try {
    const cached = JSON.parse(localStorage.getItem(LS_WEATHER) || 'null');
    if (cached && (Date.now() - cached.t) < WEATHER_TTL_MS) {
      return cached.d;
    }
  } catch {}
  try {
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${NOBORIBETSU_LAT}&longitude=${NOBORIBETSU_LON}&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=Asia%2FTokyo&forecast_days=16`;
    const res = await fetch(url);
    if (!res.ok) return {};
    const json = await res.json();
    const map = {};
    const days = json.daily;
    for (let i = 0; i < days.time.length; i++) {
      map[days.time[i]] = {
        code: days.weather_code[i],
        tmax: Math.round(days.temperature_2m_max[i]),
        tmin: Math.round(days.temperature_2m_min[i]),
        rain: days.precipitation_probability_max[i] ?? 0,
      };
    }
    try { localStorage.setItem(LS_WEATHER, JSON.stringify({ t: Date.now(), d: map })); } catch {}
    return map;
  } catch (e) {
    console.warn('Weather fetch failed:', e);
    return {};
  }
}

function weatherIconType(code) {
  if (code == null) return null;
  if (code === 0) return 'sunny';
  if (code >= 1 && code <= 3) return 'partly';
  if (code >= 45 && code <= 48) return 'foggy';
  if ((code >= 51 && code <= 67) || (code >= 80 && code <= 82)) return 'rainy';
  if ((code >= 71 && code <= 77) || (code >= 85 && code <= 86)) return 'snowy';
  if (code >= 95) return 'thundery';
  return 'cloudy';
}
function weatherLabelJa(code) {
  if (code == null) return '';
  if (code === 0) return '快晴';
  if (code <= 3) return 'くもり時々晴れ';
  if (code <= 48) return '霧';
  if ((code >= 51 && code <= 67) || (code >= 80 && code <= 82)) return '雨';
  if ((code >= 71 && code <= 77) || (code >= 85 && code <= 86)) return '雪';
  if (code >= 95) return '雷雨';
  return 'くもり';
}

let viewYear, viewMonth;
let editingId = null;
let formType = 'custom';
let formReminder = 0;
let formTimeOn = false;
let openDayKey = null;
let firestoreDb = null;
let unsubscribe = null;
let allCustomEvents = [];

// ====================  STORAGE  ====================
const Storage = {
  events() { return allCustomEvents; },
  anniversaries() { return allAnniversaries; },
  async addAnniv(a) {
    if (firestoreDb) {
      const { collection } = await import('https://www.gstatic.com/firebasejs/10.13.0/firebase-firestore.js');
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
  async init() {
    // 優先順: 1) localStorageで手動上書き 2) firebase-config.js(window) 3) ローカルのみ
    let cfg = null;
    const cfgStr = localStorage.getItem(LS_FBCONFIG);
    if (cfgStr) {
      try { cfg = JSON.parse(cfgStr); } catch {}
    }
    if (!cfg && window.FIREBASE_CONFIG && window.FIREBASE_CONFIG.apiKey) {
      cfg = window.FIREBASE_CONFIG;
    }
    if (cfg) {
      try {
        await this.initFirebase(cfg);
      } catch (e) {
        console.warn('Firebase init failed, fallback to local', e);
        this.initLocal();
      }
    } else {
      this.initLocal();
    }
  },
  initLocal() {
    setSync('offline');
    try { allCustomEvents = JSON.parse(localStorage.getItem(LS_CUSTOM) || '[]'); }
    catch { allCustomEvents = []; }
    try { allAnniversaries = JSON.parse(localStorage.getItem(LS_ANNIV) || '[]'); }
    catch { allAnniversaries = []; }
    render();
  },
  async initFirebase(cfg) {
    setSync('syncing');
    const { initializeApp } = await import('https://www.gstatic.com/firebasejs/10.13.0/firebase-app.js');
    const { getAuth, signInAnonymously, onAuthStateChanged } = await import('https://www.gstatic.com/firebasejs/10.13.0/firebase-auth.js');
    const { getFirestore, collection, onSnapshot, addDoc, deleteDoc, doc, setDoc, query, orderBy } = await import('https://www.gstatic.com/firebasejs/10.13.0/firebase-firestore.js');
    const app = initializeApp(cfg);
    // 匿名認証: ルールが request.auth != null を要求する場合に必要
    try {
      const auth = getAuth(app);
      if (!auth.currentUser) {
        await signInAnonymously(auth);
      }
    } catch (e) {
      console.warn('Anonymous sign-in failed, continuing without auth', e);
    }
    firestoreDb = getFirestore(app);
    this._coll = collection(firestoreDb, 'events');
    this._addDoc = addDoc; this._deleteDoc = deleteDoc; this._doc = doc; this._setDoc = setDoc;
    if (unsubscribe) unsubscribe();
    unsubscribe = onSnapshot(this._coll,
      snap => {
        allCustomEvents = snap.docs.map(d => ({ id: d.id, ...d.data() }));
        try { localStorage.setItem(LS_CUSTOM, JSON.stringify(allCustomEvents)); } catch {}
        setSync('online');
        render();
        if (openDayKey) refreshDaySheet();
        if (typeof scheduleReminders === 'function') scheduleReminders();
      },
      err => {
        console.warn('Firestore error, using local cache', err);
        setSync('offline');
      }
    );
    this._collAnniv = collection(firestoreDb, 'anniversaries');
    if (unsubscribeAnniv) unsubscribeAnniv();
    unsubscribeAnniv = onSnapshot(this._collAnniv, snap => {
      allAnniversaries = snap.docs.map(d => ({ id: d.id, ...d.data() }));
      try { localStorage.setItem(LS_ANNIV, JSON.stringify(allAnniversaries)); } catch {}
      renderSettingsAnniv();
      render();
    });
  },
  async add(ev) {
    if (firestoreDb) {
      await this._addDoc(this._coll, ev);
    } else {
      const item = { id: uid(), ...ev };
      allCustomEvents.push(item);
      localStorage.setItem(LS_CUSTOM, JSON.stringify(allCustomEvents));
      render();
    }
  },
  async update(id, ev) {
    if (firestoreDb) {
      await this._setDoc(this._doc(firestoreDb, 'events', id), ev);
    } else {
      const idx = allCustomEvents.findIndex(e => e.id === id);
      if (idx >= 0) allCustomEvents[idx] = { id, ...ev };
      localStorage.setItem(LS_CUSTOM, JSON.stringify(allCustomEvents));
      render();
    }
  },
  async remove(id) {
    if (firestoreDb) {
      await this._deleteDoc(this._doc(firestoreDb, 'events', id));
    } else {
      allCustomEvents = allCustomEvents.filter(e => e.id !== id);
      localStorage.setItem(LS_CUSTOM, JSON.stringify(allCustomEvents));
      render();
    }
  },
};

function setSync(state) {
  const ind = document.getElementById('sync-indicator');
  ind.classList.remove('online', 'syncing', 'offline');
  ind.classList.add(state);
}

// ====================  UTILS  ====================
function pad(n) { return String(n).padStart(2,'0'); }
function dateKey(y,m,d) { return `${y}-${pad(m+1)}-${pad(d)}`; }
function uid() { return Date.now().toString(36) + Math.random().toString(36).slice(2, 7); }
function haptic(pattern) {
  try { if (navigator.vibrate) navigator.vibrate(pattern); } catch {}
}
function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function relativeTime(ms) {
  if (!ms) return '以前に追加';
  const diff = (Date.now() - ms) / 1000;
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
function eventTypeClass(summary) {
  if (A_SHIFT_LABELS.includes(summary)) return 't-A';
  if (MEETING_LABELS.includes(summary)) return 't-meeting';
  if (OUTING_LABELS.includes(summary)) return 't-outing';
  return '';
}
function stickerId(summary, person) {
  if (A_SHIFT_LABELS.includes(summary)) return 'st-star';
  if (MEETING_LABELS.includes(summary)) return 'st-bubble';
  if (OUTING_LABELS.includes(summary)) return 'st-bag';
  if (REST_LABELS.includes(summary)) return 'st-leaf';
  if (person === '給料') return 'st-coin';
  if (person === '予定') return 'st-pin';
  return null;
}
function isBothOff(builtinEvents) {
  const k = builtinEvents.some(e => e.person === 'こうき' && REST_LABELS.includes(e.summary));
  const y = builtinEvents.some(e => e.person === 'ゆい' && REST_LABELS.includes(e.summary));
  return k && y;
}
function eventsForDate(key) {
  const builtin = (EVENTS[key] || []).map(e => ({...e, _builtin: true}));
  const custom = allCustomEvents.filter(e => e.date === key && e.type !== 'memo').map(e => ({
    id: e.id,
    person: PERSON_FROM_KEY[e.type] || '予定',
    summary: e.title,
    desc: e.desc,
    start: e.start,
    end: e.end,
    reminderMin: e.reminderMin || 0,
    _builtin: false,
  }));
  return [...builtin, ...custom];
}
function fmtTime(t) { return t ? t : ''; }

// ====================  HERO CARD  ====================
function renderHero() {
  const today = new Date();
  const todayKey = dateKey(today.getFullYear(), today.getMonth(), today.getDate());
  const WD = ['日','月','火','水','木','金','土'];

  // 次のデート(両方休み)を365日先まで探索
  let nextDate = null;
  for (let i = 0; i < 366; i++) {
    const d = new Date(today.getFullYear(), today.getMonth(), today.getDate() + i);
    const k = dateKey(d.getFullYear(), d.getMonth(), d.getDate());
    const builtin = EVENTS[k] || [];
    if (isBothOff(builtin)) { nextDate = { d, k, days: i }; break; }
  }
  // 次の給料日(ボーナス含む)
  let nextSalary = null;
  for (let i = 0; i < 366; i++) {
    const d = new Date(today.getFullYear(), today.getMonth(), today.getDate() + i);
    const k = dateKey(d.getFullYear(), d.getMonth(), d.getDate());
    const builtin = EVENTS[k] || [];
    if (builtin.some(e => e.person === '給料')) { nextSalary = { d, k, days: i }; break; }
  }
  // 今月の両方休み回数
  let monthCount = 0;
  const dim = new Date(viewYear, viewMonth+1, 0).getDate();
  for (let dd = 1; dd <= dim; dd++) {
    const k = dateKey(viewYear, viewMonth, dd);
    if (isBothOff(EVENTS[k] || [])) monthCount++;
  }

  // 今日のステータスメッセージ
  const todayBuiltin = EVENTS[todayKey] || [];
  let statusMsg = '今日もおつかれさま';
  let hot = false;
  if (isBothOff(todayBuiltin)) {
    statusMsg = '今日は二人ともおやすみ。デート日です';
    hot = true;
  } else if (todayBuiltin.some(e => e.person === '給料' && e.summary === 'ボーナス')) {
    statusMsg = '今日はボーナス支給日';
    hot = true;
  } else if (todayBuiltin.some(e => e.person === '給料' && e.summary === '給料日')) {
    statusMsg = '今日は給料日';
    hot = true;
  } else if (todayBuiltin.some(e => e.summary === 'A')) {
    const aPersons = todayBuiltin.filter(e => e.summary === 'A').map(e => e.person);
    statusMsg = `${aPersons.join('・')} は今日A番 (8:15〜17:15)`;
  } else {
    // 記念日カウントダウン(30日以内)
    if (statusMsg === '今日もおつかれさま' && !hot) {
      let nextAnniv = null;
      for (const a of (allAnniversaries || [])) {
        let target = new Date(today.getFullYear(), a.month - 1, a.day);
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
  }
  if (!hot && statusMsg === '今日もおつかれさま' && nextDate && nextDate.days > 0 && nextDate.days <= 7) {
    statusMsg = `あと ${nextDate.days} 日で二人のおやすみ`;
  } else if (!hot && statusMsg === '今日もおつかれさま' && nextSalary && nextSalary.days > 0 && nextSalary.days <= 5) {
    statusMsg = `あと ${nextSalary.days} 日で給料日`;
  }
  const status = document.getElementById('hero-status');
  status.textContent = statusMsg;
  status.classList.toggle('hot', hot);

  // 数値セット
  const setStat = (id, days, d, todayClass) => {
    const valEl = document.getElementById(`hero-stat-${id}-value`);
    const subEl = document.getElementById(`hero-stat-${id}-sub`);
    const card = document.getElementById(`hero-stat-${id}`);
    if (days == null) {
      valEl.textContent = '—';
      subEl.textContent = '';
      card.classList.remove('today-flag');
      return;
    }
    if (days === 0) {
      valEl.innerHTML = `今日`;
      card.classList.add('today-flag');
    } else {
      valEl.innerHTML = `${days}<span class="unit">日後</span>`;
      card.classList.remove('today-flag');
    }
    subEl.textContent = `${d.getMonth()+1}/${d.getDate()} (${WD[d.getDay()]})`;
  };
  setStat('date', nextDate?.days, nextDate?.d);
  setStat('salary', nextSalary?.days, nextSalary?.d);

  const countEl = document.getElementById('hero-stat-count-value');
  countEl.innerHTML = `${monthCount}`;
  document.getElementById('hero-stat-count').classList.toggle('today-flag', monthCount >= 5);

  // ジャンプ動作
  const jumpTo = (date, key) => {
    if (!date) return;
    viewYear = date.getFullYear();
    viewMonth = date.getMonth();
    render();
    saveLastView();
    setTimeout(() => openDaySheet(key, viewYear, viewMonth, date.getDate()), 80);
  };
  document.getElementById('hero-stat-date').onclick = () => nextDate && jumpTo(nextDate.d, nextDate.k);
  document.getElementById('hero-stat-salary').onclick = () => nextSalary && jumpTo(nextSalary.d, nextSalary.k);
  document.getElementById('hero-stat-count').onclick = () => {
    // 今月の両方休み日の一覧を出す: 最初の日にジャンプ
    for (let dd = 1; dd <= dim; dd++) {
      const k = dateKey(viewYear, viewMonth, dd);
      if (isBothOff(EVENTS[k] || [])) {
        const d = new Date(viewYear, viewMonth, dd);
        setTimeout(() => openDaySheet(k, viewYear, viewMonth, dd), 80);
        return;
      }
    }
  };
}

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
    const customForKey = (allCustomEvents || []).filter(e => e.date === key);
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

let yearViewYear = null;
function openYearView() {
  yearViewYear = viewYear;
  renderYearView();
  const yo = document.getElementById('year-overlay');
  yo.classList.add('open');
  yo.removeAttribute('aria-hidden');
  if (typeof lockBodyScroll === 'function') lockBodyScroll('year-overlay');
}
function closeYearView() {
  const yo = document.getElementById('year-overlay');
  yo.classList.remove('open');
  yo.setAttribute('aria-hidden', 'true');
  if (typeof releaseBodyScroll === 'function') releaseBodyScroll('year-overlay');
}
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
      if (d > dim) { cell.classList.add('empty'); cells.appendChild(cell); continue; }
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
        viewYear = yearViewYear; viewMonth = m;
        render();
        saveLastView();
        setTimeout(() => openDaySheet(key, viewYear, viewMonth, d), 120);
      };
      cells.appendChild(cell);
    }
    row.appendChild(cells);
    grid.appendChild(row);
  }
}

// ====================  RENDER  ====================
function render() {
  document.getElementById('year-label').textContent = `${viewYear}`;
  document.getElementById('month-num').textContent = `${viewMonth+1}`;
  renderSummary();
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
    cell.style.animationDelay = `${Math.min(i * 18, 540)}ms`;
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

    const num = document.createElement('div');
    num.className = 'date-num';
    if (weekday === 0) num.classList.add('sun');
    if (weekday === 6) num.classList.add('sat');
    if ((HOLIDAYS_BY_YEAR[y] || []).includes(key)) num.classList.add('holiday');
    num.textContent = d;
    if (key === todayKey) cell.classList.add('today');

    const builtinForDay = (EVENTS[key] || []);
    if (isBothOff(builtinForDay)) {
      cell.classList.add('both-off');
      const heart = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      heart.setAttribute('class', 'both-off-badge');
      heart.setAttribute('viewBox', '0 0 24 24');
      const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
      use.setAttributeNS('http://www.w3.org/1999/xlink', 'href', '#heart');
      use.setAttribute('href', '#heart');
      heart.appendChild(use);
      cell.appendChild(heart);
      const memoRec = allCustomEvents.find(ev => ev.type === 'memo' && ev.date === key);
      if (memoRec && (memoRec.stamp || memoRec.memo)) {
        const chip = document.createElement('div');
        chip.className = 'memo-chip';
        chip.textContent = memoRec.stamp || '📝';
        chip.title = memoRec.memo || '';
        cell.appendChild(chip);
      }
    }

    // 天気アイコン(取得済みかつ未来16日以内の日付のみ)
    const w = weatherData[key];
    if (w) {
      const dateRow = document.createElement('div');
      dateRow.className = 'date-row';
      dateRow.appendChild(num);
      const wType = weatherIconType(w.code);
      if (wType) {
        const wsvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        wsvg.setAttribute('class', 'weather-icon');
        wsvg.setAttribute('viewBox', '0 0 24 24');
        const wuse = document.createElementNS('http://www.w3.org/2000/svg', 'use');
        wuse.setAttributeNS('http://www.w3.org/1999/xlink', 'href', '#w-' + wType);
        wuse.setAttribute('href', '#w-' + wType);
        wsvg.appendChild(wuse);
        dateRow.appendChild(wsvg);
      }
      cell.appendChild(dateRow);
    } else {
      cell.appendChild(num);
    }

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
      const ev = document.createElement('div');
      const typeCls = eventTypeClass(e.summary);
      ev.className = 'event ' + PERSON_KEY[e.person] + (typeCls ? ' ' + typeCls : '');
      const sId = stickerId(e.summary, e.person);
      const stickerSvg = sId ? `<svg class="event-sticker"><use href="#${sId}"/></svg>` : '<span></span>';
      if (e.person === '給料') {
        ev.innerHTML = `${stickerSvg}<span class="event-text"><span class="event-label">${escapeHtml(e.summary)}</span></span>`;
      } else {
        ev.innerHTML = `${stickerSvg}<span class="event-text"><span class="event-name">${e.person}</span><span class="event-label">${escapeHtml(e.summary)}</span></span>`;
      }
      cell.appendChild(ev);
    });
    if (dayEvents.length > 3) {
      const more = document.createElement('div');
      more.className = 'more-events';
      more.textContent = `+${dayEvents.length - 3}件`;
      cell.appendChild(more);
    }

    cell.setAttribute('role', 'button');
    cell.setAttribute('tabindex', '0');
    cell.setAttribute('aria-label', `${y}年${m+1}月${d}日`);
    cell.onclick = () => { haptic(15); openDaySheet(key, y, m, d); };
    cell.onkeydown = (ev) => {
      if (ev.key === 'Enter' || ev.key === ' ') {
        ev.preventDefault();
        openDaySheet(key, y, m, d);
      }
    };
    grid.appendChild(cell);
  }
  renderHero();
  renderRecall();
}

// ====================  DAY SHEET  ====================
function openDaySheet(key, y, m, d) {
  const wd = ['日','月','火','水','木','金','土'][new Date(y, m, d).getDay()];
  document.getElementById('day-title').innerHTML = `<span class="num">${m+1}</span>月<span class="num">${d}</span>日`;
  document.getElementById('day-subtitle').textContent = `${y}年 ${wd}曜日`;
  openDayKey = key;
  refreshDaySheet();
  document.getElementById('day-overlay').classList.add('open');
  document.getElementById('day-overlay').setAttribute('aria-hidden', 'false');
  lockBodyScroll('day');
}
function refreshDaySheet() {
  if (!openDayKey) return;
  const key = openDayKey;
  const body = document.getElementById('day-body');
  body.innerHTML = '';
  // 天気カード(取得できていれば最上部に)
  const w = weatherData[key];
  if (w) {
    const wType = weatherIconType(w.code);
    const wcard = document.createElement('div');
    wcard.className = 'day-weather';
    wcard.innerHTML = `
      <svg class="day-weather-icon" viewBox="0 0 24 24"><use href="#w-${wType}"/></svg>
      <div>
        <div class="day-weather-temp">${w.tmax}° / ${w.tmin}°</div>
        <div class="day-weather-rain">${weatherLabelJa(w.code)} ・ 降水 ${w.rain}%</div>
      </div>
    `;
    body.appendChild(wcard);
  }
  const evs = eventsForDate(key);
  const builtin = (EVENTS[key] || []);
  // 該当月日の毎年の予定(誕生日・記念日)を抽出
  const [_y, _m, _d] = key.split('-').map(Number);
  const annivsForDay = (allAnniversaries || []).filter(a => a.month === _m && a.day === _d);
  if (isBothOff(builtin)) {
    spawnConfetti();
    const banner = document.createElement('div');
    banner.className = 'both-off-banner';
    banner.innerHTML = `<svg><use href="#heart"/></svg><span>二人ともお休み 💗</span>`;
    body.appendChild(banner);
    body.appendChild(buildDateMemoCard(key));
  }
  if (evs.length === 0 && annivsForDay.length === 0) {
    const empty = document.createElement('div');
    empty.className = 'empty';
    empty.innerHTML = `<svg class="lily"><use href="#lily"/></svg>予定なし`;
    body.appendChild(empty);
  } else {
    evs.forEach((e, idx) => {
      const cls = PERSON_KEY[e.person];
      const row = document.createElement('div');
      row.className = 'event-row';
      row.style.animationDelay = `${idx * 50}ms`;
      const actionsHtml = !e._builtin ? `<div class="actions"><button class="row-icon" data-edit="${e.id}" aria-label="編集"><svg><use href="#i-edit"/></svg></button></div>` : '';
      const timeStr = (e.start && e.end) ? `<span class="time">${e.start}–${e.end}</span>` : '';
      const reminderStr = e.reminderMin ? `<span style="display:inline-flex;align-items:center;gap:2px;"><svg style="width:12px;height:12px;"><use href="#i-bell"/></svg>${e.reminderMin}分前</span>` : '';
      row.innerHTML = `
        <div class="bullet ${cls}"></div>
        <div class="text-block">
          <div class="label">${escapeHtml(e.summary)}</div>
          <div class="meta">
            <span class="person-tag ${cls}">${e.person}</span>
            ${timeStr}
            ${reminderStr}
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
  // 毎年の予定(誕生日・記念日など)カード
  const typeEmoji = { birth: '🎂', anniv: '💗', other: '🌸' };
  const typeLabel = { birth: '誕生日', anniv: '記念日', other: '毎年の予定' };
  annivsForDay.forEach((a, idx) => {
    const type = a.type || 'other';
    const cls = type === 'birth' ? 'yui' : (type === 'anniv' ? 'yui' : 'custom');
    const iconId = type === 'birth' ? 'st-cake' : (type === 'anniv' ? 'heart' : 'st-star');
    const row = document.createElement('div');
    row.className = 'event-row';
    row.style.animationDelay = `${(evs.length + idx) * 50}ms`;
    row.innerHTML = `
      <div class="bullet ${cls}"><svg style="width:14px;height:14px;color:white;"><use href="#${iconId}"/></svg></div>
      <div class="text-block">
        <div class="label">${typeEmoji[type] || '🌸'} ${escapeHtml(a.name)}</div>
        <div class="meta">
          <span class="person-tag ${cls}">${typeLabel[type] || '毎年の予定'}</span>
          <span>毎年 ${a.month}/${a.day}</span>
        </div>
      </div>
    `;
    body.appendChild(row);
  });
}
function findDateMemo(key) {
  return allCustomEvents.find(e => e.type === 'memo' && e.date === key);
}

const STAMP_OPTIONS = ['💗', '🍰', '🎬', '🍣', '☕', '🌸', '🛍️', '🌊'];
const MEMO_TEMPLATES = [
  'カフェでまったり',
  '映画デート',
  'お買い物',
  'お家でゆっくり',
  'お出かけ',
];

function buildDateMemoCard(key) {
  const wrap = document.createElement('div');
  wrap.className = 'memo-card';
  const existing = findDateMemo(key);
  const currentStamp = existing?.stamp || '';
  const currentMemo = existing?.memo || '';
  wrap.innerHTML = `
    <div class="memo-card-title">二人のひとことメモ</div>
    <div class="memo-stamps" role="radiogroup" aria-label="スタンプを選ぶ">
      ${STAMP_OPTIONS.map(s => `<button class="memo-stamp${s===currentStamp?' selected':''}" data-stamp="${s}" role="radio" aria-checked="${s===currentStamp}" aria-label="スタンプ ${s}">${s}</button>`).join('')}
    </div>
    <div class="memo-templates" aria-label="テンプレート">
      ${MEMO_TEMPLATES.map(t => `<button class="memo-template" data-tpl="${escapeHtml(t)}">${escapeHtml(t)}</button>`).join('')}
    </div>
    <textarea class="memo-textarea" id="memo-text-${key}" placeholder="今日のデートプランを書こう…" aria-label="デートプランメモ">${escapeHtml(currentMemo)}</textarea>
    <div class="memo-actions">
      <button class="btn btn-primary memo-save">保存</button>
    </div>
  `;
  let pickedStamp = currentStamp;
  wrap.querySelectorAll('.memo-stamp').forEach(btn => {
    btn.onclick = () => {
      pickedStamp = (pickedStamp === btn.dataset.stamp) ? '' : btn.dataset.stamp;
      wrap.querySelectorAll('.memo-stamp').forEach(b => {
        const on = b.dataset.stamp === pickedStamp;
        b.classList.toggle('selected', on);
        b.setAttribute('aria-checked', on ? 'true' : 'false');
      });
    };
  });
  wrap.querySelectorAll('.memo-template').forEach(btn => {
    btn.onclick = () => {
      const ta = wrap.querySelector('.memo-textarea');
      ta.value = ta.value ? ta.value + ' ' + btn.dataset.tpl : btn.dataset.tpl;
      ta.focus();
    };
  });
  wrap.querySelector('.memo-save').onclick = async () => {
    const memo = wrap.querySelector('.memo-textarea').value.trim();
    const stamp = pickedStamp;
    const ex = findDateMemo(key);
    if (!memo && !stamp) {
      if (ex) await Storage.remove(ex.id);
    } else {
      const payload = { type: 'memo', date: key, memo, stamp, title: '', desc: '' };
      if (ex) await Storage.update(ex.id, payload);
      else await Storage.add(payload);
    }
    if (!firestoreDb) render();
  };
  return wrap;
}

function closeDaySheet() {
  document.getElementById('day-overlay').classList.remove('open');
  document.getElementById('day-overlay').setAttribute('aria-hidden', 'true');
  openDayKey = null;
  releaseBodyScroll('day');
}

// === Sheet helpers (scroll lock + ESC) ===
const _lockedSheets = new Set();
function lockBodyScroll(tag) {
  _lockedSheets.add(tag);
  document.body.style.overflow = 'hidden';
}
function releaseBodyScroll(tag) {
  _lockedSheets.delete(tag);
  if (_lockedSheets.size === 0) document.body.style.overflow = '';
}
function topMostOpenSheet() {
  const ids = ['form-overlay', 'settings-overlay', 'day-overlay'];
  for (const id of ids) {
    const el = document.getElementById(id);
    if (el && el.classList.contains('open')) return id;
  }
  return null;
}

// ====================  FORM  ====================
function openForm(id, dateKeyHint) {
  editingId = id;
  document.getElementById('form-title').textContent = id ? '予定を編集' : '予定を追加';
  document.getElementById('f-delete').style.display = id ? 'flex' : 'none';
  let date, type, title, desc, start, end, reminderMin;
  if (id) {
    const item = allCustomEvents.find(e => e.id === id);
    if (!item) return;
    date = item.date; type = item.type; title = item.title; desc = item.desc || '';
    start = item.start; end = item.end; reminderMin = item.reminderMin || 0;
  } else {
    date = dateKeyHint || dateKey(viewYear, viewMonth, new Date().getDate());
    type = 'custom'; title = ''; desc = '';
    start = ''; end = ''; reminderMin = 0;
  }
  document.getElementById('f-date').value = date;
  document.getElementById('f-title').value = title;
  document.getElementById('f-desc').value = desc;
  formType = type;
  document.querySelectorAll('.type-option').forEach(o => o.classList.toggle('selected', o.dataset.type === type));
  formReminder = reminderMin;
  document.querySelectorAll('.reminder-option').forEach(o => o.classList.toggle('selected', Number(o.dataset.min) === reminderMin));
  formTimeOn = !!(start && end);
  document.getElementById('f-time-toggle').classList.toggle('on', formTimeOn);
  document.getElementById('f-time-fields').style.display = formTimeOn ? 'block' : 'none';
  if (start) document.getElementById('f-start').value = start;
  if (end) document.getElementById('f-end').value = end;
  document.getElementById('form-overlay').classList.add('open');
  document.getElementById('form-overlay').setAttribute('aria-hidden', 'false');
  lockBodyScroll('form');
  setTimeout(() => document.getElementById('f-title').focus(), 300);
}
function closeForm() {
  document.getElementById('form-overlay').classList.remove('open');
  document.getElementById('form-overlay').setAttribute('aria-hidden', 'true');
  editingId = null;
  releaseBodyScroll('form');
}
async function saveForm() {
  const date = document.getElementById('f-date').value;
  const title = document.getElementById('f-title').value.trim();
  const desc = document.getElementById('f-desc').value.trim();
  const start = formTimeOn ? document.getElementById('f-start').value : '';
  const end = formTimeOn ? document.getElementById('f-end').value : '';
  if (!date || !title) {
    document.getElementById('f-title').focus();
    return;
  }
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
  haptic(15);
  (function showSaveToast() {
    const t = document.createElement('div');
    t.className = 'save-toast';
    t.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>保存しました';
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 1900);
  })();
  closeForm();
  scheduleReminders();
  const [y, mm, d] = date.split('-').map(Number);
  viewYear = y; viewMonth = mm - 1;
  if (!firestoreDb) render();
  setTimeout(() => openDaySheet(date, y, mm - 1, d), 80);
}
async function deleteForm() {
  if (!editingId) return;
  const ok = await showConfirm('予定を削除', 'この予定を削除します。よろしいですか?', '削除する');
  if (!ok) return;
  haptic([40, 30, 40]);
  const date = document.getElementById('f-date').value;
  await Storage.remove(editingId);
  closeForm();
  if (!firestoreDb) render();
  if (date) {
    const [y, mm, d] = date.split('-').map(Number);
    setTimeout(() => openDaySheet(date, y, mm - 1, d), 80);
  }
}

// ====================  NOTIFICATIONS  ====================
const reminderTimers = new Map();
function scheduleReminders() {
  reminderTimers.forEach(t => clearTimeout(t));
  reminderTimers.clear();
  if (!('Notification' in window) || Notification.permission !== 'granted') return;
  const now = Date.now();
  allCustomEvents.forEach(e => {
    if (!e.reminderMin) return;
    let when;
    if (e.start) {
      when = new Date(`${e.date}T${e.start}`).getTime();
    } else {
      when = new Date(`${e.date}T09:00`).getTime();
    }
    const fireAt = when - e.reminderMin * 60000;
    const delay = fireAt - now;
    if (delay > 0 && delay < 86400000 * 7) {
      const t = setTimeout(() => {
        new Notification('シフトカレンダー', {
          body: `${e.title}${e.start ? ' ('+e.start+')' : ''}`,
          icon: 'icon.png',
        });
      }, delay);
      reminderTimers.set(e.id, t);
    }
  });
}

// ====================  SETTINGS  ====================
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
function openSettings() {
  const cfg = localStorage.getItem(LS_FBCONFIG) || '';
  document.getElementById('fb-config').value = cfg;
  updateNotifStatus();
  renderSettingsAnniv();
  document.getElementById('settings-overlay').classList.add('open');
  document.getElementById('settings-overlay').setAttribute('aria-hidden', 'false');
  lockBodyScroll('settings');
}
function closeSettings() {
  document.getElementById('settings-overlay').classList.remove('open');
  document.getElementById('settings-overlay').setAttribute('aria-hidden', 'true');
  releaseBodyScroll('settings');
}
function updateNotifStatus() {
  const status = document.getElementById('notif-status');
  if (!('Notification' in window)) {
    status.textContent = 'このブラウザは通知に対応していません';
    document.getElementById('enable-notif').style.display = 'none';
    return;
  }
  if (Notification.permission === 'granted') {
    status.textContent = '✓ 通知が有効です';
    document.getElementById('enable-notif').textContent = '通知をテスト送信';
  } else if (Notification.permission === 'denied') {
    status.textContent = '通知はブロックされています。ブラウザ設定から有効化してください';
  } else {
    status.textContent = '通知は未設定です';
  }
}
async function enableNotifications() {
  if (Notification.permission === 'granted') {
    new Notification('シフトカレンダー', { body: '通知のテストです 🐸', icon: 'icon.png' });
    return;
  }
  const perm = await Notification.requestPermission();
  updateNotifStatus();
  if (perm === 'granted') {
    new Notification('シフトカレンダー', { body: '通知が有効になりました 🐸', icon: 'icon.png' });
    scheduleReminders();
  }
}
async function saveSettings() {
  const cfgStr = document.getElementById('fb-config').value.trim();
  if (cfgStr) {
    try {
      const cfg = JSON.parse(cfgStr);
      if (!cfg.apiKey || !cfg.projectId) throw new Error('apiKey/projectIdが必要です');
      localStorage.setItem(LS_FBCONFIG, JSON.stringify(cfg));
      await Storage.initFirebase(cfg);
    } catch (e) {
      await showConfirm('設定エラー', 'Firebase configの形式エラー: ' + e.message, '閉じる');
      return;
    }
  } else {
    localStorage.removeItem(LS_FBCONFIG);
    if (unsubscribe) { unsubscribe(); unsubscribe = null; }
    firestoreDb = null;
    Storage.initLocal();
  }
  closeSettings();
}

// ====================  CONFIRM SHEET  ====================
let _confirmResolver = null;
function showConfirm(title, message, okLabel) {
  return new Promise((resolve) => {
    document.getElementById('confirm-title').textContent = title;
    document.getElementById('confirm-message').textContent = message;
    document.getElementById('confirm-ok').textContent = okLabel || '削除する';
    _confirmResolver = resolve;
    const co = document.getElementById('confirm-overlay');
    co.classList.add('open');
    co.removeAttribute('aria-hidden');
    if (typeof lockBodyScroll === 'function') lockBodyScroll('confirm-overlay');
  });
}
function _resolveConfirm(ok) {
  const co = document.getElementById('confirm-overlay');
  co.classList.remove('open');
  co.setAttribute('aria-hidden', 'true');
  if (typeof releaseBodyScroll === 'function') releaseBodyScroll('confirm-overlay');
  if (_confirmResolver) { _confirmResolver(ok); _confirmResolver = null; }
}

// ====================  INIT  ====================
function celebrateBothOff() {
  // 今日が両方休みなら、ハートを画面下から舞わせる(セッション中1回のみ)
  const today = new Date();
  const todayKey = dateKey(today.getFullYear(), today.getMonth(), today.getDate());
  if (!isBothOff(EVENTS[todayKey] || [])) return;
  if (sessionStorage.getItem('celebrated-' + todayKey)) return;
  sessionStorage.setItem('celebrated-' + todayKey, '1');
  const overlay = document.createElement('div');
  overlay.className = 'celebration-overlay';
  document.body.appendChild(overlay);
  for (let i = 0; i < 9; i++) {
    setTimeout(() => {
      const h = document.createElement('div');
      h.className = 'celebration-heart';
      h.innerHTML = '<svg viewBox="0 0 24 24"><use href="#heart"/></svg>';
      h.style.left = (Math.random() * 88 + 6) + '%';
      overlay.appendChild(h);
      setTimeout(() => h.remove(), 3600);
    }, i * 220);
  }
  setTimeout(() => overlay.remove(), 5500);
}

function saveLastView() {
  try { localStorage.setItem(LS_LAST_VIEW, JSON.stringify({y: viewYear, m: viewMonth, ts: Date.now()})); } catch(e) {}
}

async function init() {
  const today = new Date();
  viewYear = today.getFullYear();
  viewMonth = today.getMonth();
  try {
    const lv = JSON.parse(localStorage.getItem(LS_LAST_VIEW) || 'null');
    if (lv && typeof lv.y === 'number' && typeof lv.m === 'number' && Date.now() - lv.ts < 86400000) {
      viewYear = lv.y; viewMonth = lv.m;
    }
  } catch(e) {}
  await Storage.init();
  render();

  // 天気を取得(完了したら再描画)
  fetchWeather().then(data => {
    weatherData = data;
    render();
    if (openDayKey) refreshDaySheet();
  });

  // お祝いアニメ
  setTimeout(celebrateBothOff, 600);

  document.getElementById('prev').onclick = () => shift(-1);
  document.getElementById('next').onclick = () => shift(1);
  document.getElementById('today').onclick = () => {
    const t = new Date();
    viewYear = t.getFullYear(); viewMonth = t.getMonth();
    render();
    saveLastView();
  };
  document.getElementById('mascot').onclick = () => {
    const m = document.getElementById('mascot');
    m.classList.remove('hop');
    void m.offsetWidth;
    m.classList.add('hop');
  };
  document.querySelectorAll('.chip').forEach(c => {
    if (!c.dataset.key) return;
    const toggle = () => {
      filters[c.dataset.key] = !filters[c.dataset.key];
      c.classList.toggle('active');
      c.setAttribute('aria-checked', filters[c.dataset.key] ? 'true' : 'false');
      render();
    };
    c.onclick = toggle;
    c.onkeydown = (ev) => {
      if (ev.key === 'Enter' || ev.key === ' ') {
        ev.preventDefault();
        toggle();
      }
    };
  });
  document.getElementById('fab').onclick = () => openForm(null);
  document.getElementById('day-close').onclick = closeDaySheet;
  document.getElementById('day-overlay').onclick = e => { if (e.target.id==='day-overlay') closeDaySheet(); };
  document.getElementById('day-add').onclick = () => { const k = openDayKey; closeDaySheet(); openForm(null, k); };
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
  document.querySelectorAll('.reminder-option').forEach(o => {
    o.onclick = () => {
      document.querySelectorAll('.reminder-option').forEach(x => x.classList.remove('selected'));
      o.classList.add('selected');
      formReminder = Number(o.dataset.min);
    };
  });
  document.getElementById('f-time-toggle').onclick = () => {
    formTimeOn = !formTimeOn;
    document.getElementById('f-time-toggle').classList.toggle('on', formTimeOn);
    document.getElementById('f-time-fields').style.display = formTimeOn ? 'block' : 'none';
  };
  document.getElementById('settings-btn').onclick = openSettings;
  document.getElementById('settings-close').onclick = closeSettings;
  document.getElementById('settings-cancel').onclick = closeSettings;
  document.getElementById('settings-overlay').onclick = e => { if (e.target.id==='settings-overlay') closeSettings(); };
  document.getElementById('settings-save').onclick = saveSettings;
  document.getElementById('enable-notif').onclick = enableNotifications;
  document.getElementById('confirm-ok').onclick = () => _resolveConfirm(true);
  document.getElementById('confirm-cancel').onclick = () => _resolveConfirm(false);
  document.getElementById('confirm-overlay').onclick = e => {
    if (e.target.id === 'confirm-overlay') _resolveConfirm(false);
  };

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

  const recallToggle = document.getElementById('recall-toggle');
  if (recallToggle) recallToggle.onclick = () => {
    const expanded = recallToggle.getAttribute('aria-expanded') === 'true';
    recallToggle.setAttribute('aria-expanded', String(!expanded));
    document.getElementById('recall-body').hidden = expanded;
  };

  document.getElementById('year-btn').onclick = openYearView;
  document.getElementById('year-close').onclick = closeYearView;
  document.getElementById('year-overlay').onclick = e => {
    if (e.target.id === 'year-overlay') closeYearView();
  };
  document.getElementById('year-prev').onclick = () => { yearViewYear--; renderYearView(); };
  document.getElementById('year-next').onclick = () => { yearViewYear++; renderYearView(); };
  const histBtn = document.getElementById('history-btn');
  if (histBtn) histBtn.onclick = openHistoryView;
  const histClose = document.getElementById('history-close');
  if (histClose) histClose.onclick = closeHistoryView;
  document.getElementById('history-overlay').onclick = e => {
    if (e.target.id === 'history-overlay') closeHistoryView();
  };

  // Swipe gestures for month nav
  let swipeStart = null;
  document.body.addEventListener('touchstart', e => {
    if (e.target.closest('.sheet-overlay')) return;
    if (e.target.closest('input, textarea, select')) return;
    swipeStart = { x: e.touches[0].clientX, y: e.touches[0].clientY, time: Date.now() };
  }, { passive: true });
  document.body.addEventListener('touchend', e => {
    if (!swipeStart) return;
    const dx = e.changedTouches[0].clientX - swipeStart.x;
    const dy = e.changedTouches[0].clientY - swipeStart.y;
    const dt = Date.now() - swipeStart.time;
    if (dt < 400 && Math.abs(dx) > 80 && Math.abs(dy) < 60) {
      shift(dx < 0 ? 1 : -1);
    }
    swipeStart = null;
  }, { passive: true });

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

  scheduleReminders();
}
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
  if (document.querySelector('.confetti-wrap')) return;  // rapid tap ガード
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

function shift(delta) {
  viewMonth += delta;
  if (viewMonth < 0) { viewMonth = 11; viewYear--; }
  if (viewMonth > 11) { viewMonth = 0; viewYear++; }
  render();
  saveLastView();
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
    "background_color": "#FFF8F0",
    "theme_color": "#FFF8F0",
    "orientation": "portrait",
    "icons": [
        {"src": "icon.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icon.png", "sizes": "512x512", "type": "image/png"},
    ],
}

SW = """const CACHE = 'shift-cal-__BUILD_TS__';
self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(['./','./index.html','./manifest.json','./icon.png'])));
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


import datetime as _dt

# PDF由来のA番(8:15~17:15シフト)。Excelには未収録のためここで補う。
# 同じファイル名のPDFがあれば extract_a_shifts_from_pdf() で自動上書き
# 構造: {(year, month): {person: [day, ...]}}
A_SHIFTS_FALLBACK_BY_MONTH = {
    (2026, 6): {
        "こうき": [2, 16, 19, 28],
        "ゆい":   [8, 13, 15, 24],
    },
    (2026, 7): {
        "こうき": [10, 19, 25],
        "ゆい":   [16],
    },
}

# 2026年7月分シフト(PDF抽出済、xlsx無いため直接埋め込む)
# A番は上の A_SHIFTS_FALLBACK_BY_MONTH 側で処理するためここでは除外
EXTRA_EVENTS_BY_DATE = {
    "2026-07-01": [{"person": "こうき", "summary": "休"}, {"person": "ゆい", "summary": "休"}],
    "2026-07-02": [{"person": "ゆい", "summary": "希望休"}],
    "2026-07-03": [{"person": "こうき", "summary": "出店"}],
    "2026-07-04": [{"person": "こうき", "summary": "出店"}],
    "2026-07-05": [{"person": "こうき", "summary": "出店"}],
    "2026-07-06": [{"person": "こうき", "summary": "希望休"}],
    "2026-07-07": [{"person": "こうき", "summary": "会議"}, {"person": "ゆい", "summary": "会議"}],
    "2026-07-08": [{"person": "こうき", "summary": "休"}, {"person": "ゆい", "summary": "有"}],
    "2026-07-09": [{"person": "こうき", "summary": "休"}, {"person": "ゆい", "summary": "休"}],
    "2026-07-10": [{"person": "ゆい", "summary": "MTG"}],
    "2026-07-11": [{"person": "ゆい", "summary": "休"}],
    "2026-07-12": [{"person": "こうき", "summary": "休"}],
    "2026-07-13": [{"person": "こうき", "summary": "会議"}, {"person": "ゆい", "summary": "休"}],
    "2026-07-15": [{"person": "こうき", "summary": "出張"}, {"person": "ゆい", "summary": "有"}],
    "2026-07-16": [{"person": "こうき", "summary": "希望休"}],
    "2026-07-17": [{"person": "こうき", "summary": "休"}],
    "2026-07-18": [{"person": "こうき", "summary": "休"}, {"person": "ゆい", "summary": "休"}],
    "2026-07-20": [{"person": "こうき", "summary": "会議"}],
    "2026-07-21": [{"person": "こうき", "summary": "有"}, {"person": "ゆい", "summary": "有"}],
    "2026-07-22": [{"person": "こうき", "summary": "休"}],
    "2026-07-23": [{"person": "ゆい", "summary": "有"}],
    "2026-07-24": [{"person": "こうき", "summary": "会議"}, {"person": "ゆい", "summary": "希望休"}],
    "2026-07-25": [{"person": "ゆい", "summary": "希望休"}],
    "2026-07-26": [{"person": "こうき", "summary": "有"}, {"person": "ゆい", "summary": "希望休"}],
    "2026-07-27": [{"person": "こうき", "summary": "会議"}],
    "2026-07-28": [{"person": "こうき", "summary": "出店"}],
    "2026-07-29": [{"person": "こうき", "summary": "出店"}, {"person": "ゆい", "summary": "休"}],
    "2026-07-30": [{"person": "こうき", "summary": "休"}],
    "2026-07-31": [{"person": "ゆい", "summary": "希望休"}],
}


def get_fallback_a_shifts(year, month):
    """指定年月のフォールバックA番を取得。なければ空辞書。"""
    raw = A_SHIFTS_FALLBACK_BY_MONTH.get((year, month), {})
    return {person: [(year, month, d) for d in days] for person, days in raw.items()}


def extract_a_shifts_from_pdf(pdf_path, year=None, month=None):
    """PDFのシフト表からA番の日付を抽出。失敗時は空辞書を返す。"""
    try:
        import pdfplumber
    except ImportError:
        print("  warn: pdfplumber未インストール、A番PDF抽出スキップ")
        return {}
    try:
        with pdfplumber.open(pdf_path) as pdf:
            t = pdf.pages[0].extract_tables()[0]
        kouki_col = 2  # 安中
        yui_col = 8    # 恩田
        kouki, yui = [], []
        for row in t:
            if row[0] and str(row[0]).isdigit():
                d = int(row[0])
                if (row[kouki_col] or '').strip() in ('A', 'Ａ'):
                    kouki.append(d)
                if (row[yui_col] or '').strip() in ('A', 'Ａ'):
                    yui.append(d)
        return {"こうき": [(year, month, d) for d in kouki],
                "ゆい":   [(year, month, d) for d in yui]}
    except Exception as e:
        print(f"  warn: PDF抽出失敗({e})、A番は空")
        return {}


def main():
    if len(sys.argv) < 2:
        print("Usage: python build.py <xlsx_path>")
        sys.exit(1)
    xlsx = sys.argv[1]
    shift_events, year = parse_shift(xlsx)
    salary_events = build_salary_events(year)

    # xlsxから取得した月(shift_eventsの最初の日付から)
    shift_month = shift_events[0][1].month if shift_events else 1

    # 対応するPDFがあればA番を取得、なければ A_SHIFTS_FALLBACK_BY_MONTH からフォールバック
    pdf_path = os.path.splitext(xlsx)[0] + ".pdf"
    a_shifts = {}
    if os.path.exists(pdf_path):
        a_shifts = extract_a_shifts_from_pdf(pdf_path, year=year, month=shift_month)
    if not a_shifts:
        fallback = get_fallback_a_shifts(year, shift_month)
        if fallback:
            print(f"  info: PDF未使用、{year}/{shift_month}のフォールバック辞書からA番取得")
            a_shifts = fallback
        else:
            print(f"  warn: PDFなし+フォールバックなし、A番は空 (year={year}, month={shift_month})")
    print(f"  A番: こうき={[d for _,_,d in a_shifts.get('こうき', [])]}, ゆい={[d for _,_,d in a_shifts.get('ゆい', [])]}")

    by_date = {}
    for name, d, label in shift_events:
        k = d.strftime("%Y-%m-%d")
        display_name = NAME_MAP.get(name, name)
        by_date.setdefault(k, []).append({"person": display_name, "summary": label})
    for d, title, desc in salary_events:
        k = d.strftime("%Y-%m-%d")
        by_date.setdefault(k, []).append({"person": "給料", "summary": title, "desc": desc})

    # A番をイベントとして追加(同日に「会議」等がある場合はA番を先頭に来るよう挿入)
    for person, dates in a_shifts.items():
        for y, m, dnum in dates:
            d = _dt.date(y, m, dnum)
            k = d.strftime("%Y-%m-%d")
            existing = by_date.setdefault(k, [])
            # 既に A 追加済みかチェック
            if any(e.get("person") == person and e.get("summary") == "A" for e in existing):
                continue
            existing.insert(0, {"person": person, "summary": "A"})

    # 追加イベント(xlsx範囲外の月分、PDF抽出済データを直接埋め込み)
    if EXTRA_EVENTS_BY_DATE:
        extra_count = 0
        for k, evs in EXTRA_EVENTS_BY_DATE.items():
            existing = by_date.setdefault(k, [])
            for ev in evs:
                # 重複チェック(同person+summary)
                if any(e.get("person") == ev["person"] and e.get("summary") == ev["summary"] for e in existing):
                    continue
                existing.append(ev)
                extra_count += 1
        # EXTRA データに含まれる月のA番(他月)も追加
        extra_months = set()
        for k in EXTRA_EVENTS_BY_DATE:
            ey, em, _ = k.split("-")
            extra_months.add((int(ey), int(em)))
        for (ey, em) in extra_months:
            if (ey, em) == (year, shift_month):
                continue  # メイン月は既処理
            extra_a = get_fallback_a_shifts(ey, em)
            for person, dates in extra_a.items():
                for y, m, dnum in dates:
                    d = _dt.date(y, m, dnum)
                    k = d.strftime("%Y-%m-%d")
                    existing = by_date.setdefault(k, [])
                    if any(e.get("person") == person and e.get("summary") == "A" for e in existing):
                        continue
                    existing.insert(0, {"person": person, "summary": "A"})
        print(f"  info: EXTRA_EVENTS から {extra_count}件 追加({len(extra_months)}ヶ月分のA番含む)")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    html = TEMPLATE.replace("__EVENTS_JSON__", json.dumps(by_date, ensure_ascii=False))
    html = html.replace("__HOLIDAYS_JSON__", json.dumps(HOLIDAYS_BY_YEAR))

    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    with open(os.path.join(OUTPUT_DIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(MANIFEST, f, ensure_ascii=False, indent=2)
    build_ts = _dt.datetime.now().strftime("%Y%m%d%H%M%S")
    sw_text = SW.replace("__BUILD_TS__", build_ts)
    with open(os.path.join(OUTPUT_DIR, "sw.js"), "w", encoding="utf-8") as f:
        f.write(sw_text)

    total_events = sum(len(v) for v in by_date.values())
    print(f"出力先: {OUTPUT_DIR}")
    print(f"  index.html ({total_events}件のイベント)")


if __name__ == "__main__":
    main()
