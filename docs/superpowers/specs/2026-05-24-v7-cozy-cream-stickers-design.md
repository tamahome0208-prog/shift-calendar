# シフトカレンダー v7「Cozy Cream + Stickers」設計

**日付**: 2026-05-24
**ターゲット**: https://tamahome0208-prog.github.io/shift-calendar/
**スコープ**: デザイン刷新 — クリーム背景 + ビビッドアクセント + 自作SVGステッカー
**コミット計画**: 2コミット、各150行以内、合計 ~250行

---

## 0. なぜやるか

ユーザー要望「もっと柔らかく可愛く見やすく」+ Web/YouTube 調査結果:

- 2026 カレンダーUI トレンド = soft pastel(クリーム+ピーチ+セージ)+ rounded edge
- かわいい系アプリ定着要素 = hand-drawn 風アイコン、ステッカー
- ただし「見やすさ」優先 → コントラスト維持・本文フォント変えない

現状 v6 は緑+ピンクの面積が広く視覚ノイズが多い。背景をクリームに転換し、アクセント色は彩度キープでメリハリ、ステッカーで絵心を足す。

---

## 1. カラーパレット

ユーザー指示「色はビビッドに、余白・影はそのまま」を反映。背景だけ暖色クリームへ、アクセントは現行同等以上の彩度。

| 役割 | 旧 | 新 |
|---|---|---|
| `--bg` | #FBFBF7 | **#FFF8F0**(クリーム) |
| `--bg-2` | #F5F4EE | **#FFEFDF**(ピーチクリーム) |
| `--surface-soft` | #FAFAF5 | **#FFFAEF** |
| `--surface-2` | #F0EFE8 | **#FFEAD8** |
| `--border` | #EDEBE2 | **#F8E4CC**(暖色境界) |
| `--border-strong` | #D4D1C4 | **#E8C8A0** |
| `--hairline` | rgba(15,26,4,0.06) | rgba(120, 70, 20, 0.08) |
| `--leaf` | #7CC243 | **#84CC16**(明度UP、彩度UP) |
| `--leaf-dark` | #5BA528 | **#65A30D** |
| `--leaf-deep` | #3F7B14 | **#3F6212** |
| `--cheek` | #FFB7D3 | **#FFAFC5**(彩度キープ) |
| `--cheek-deep` | #FF7AA5 | **#F764A2** |
| 追加 | — | **`--peach: #FFB892`** |
| 追加 | — | **`--peach-deep: #FF8E5C`** |
| 追加 | — | **`--sunshine: #FBBF24`**(A番再利用) |
| `--text` | #0F1A04 | **#1F1A0F**(暖色寄り黒) |
| `--text-2` | #2A3A18 | **#3F341F** |
| `--muted` | #7B8170 | **#8A7860** |

メイン3色: クリーム背景 + ビビッドピンク + ビビッドリーフ。ピーチを差し色。

## 2. 影と余白(現状のまま、ただし色相を暖色に)

```css
--shadow-xs: 0 1px 1px rgba(120, 70, 20, 0.05);
--shadow-sm: 0 2px 6px rgba(120, 70, 20, 0.06), 0 1px 2px rgba(120, 70, 20, 0.04);
--shadow-md: 0 4px 12px rgba(120, 70, 20, 0.08), 0 2px 4px rgba(120, 70, 20, 0.05);
--shadow-lg: 0 24px 48px rgba(120, 70, 20, 0.15), 0 8px 16px rgba(120, 70, 20, 0.06);
--shadow-pink: 0 4px 16px rgba(247, 100, 162, 0.3);
--shadow-leaf: 0 4px 16px rgba(132, 204, 22, 0.28);
```

余白・角丸は現行維持(ユーザー指示)。

## 3. 自作 SVG ステッカー(6種類)

イベント種別ごとに `12×12px` の小さな SVG をチップ左に表示。emoji ではなく自作。`stroke-width:1.2`, `stroke-linecap:round` で手描き感、彩色は塗りつぶし+控えめストローク。

| 種類 | アイコン名 | 描画 |
|---|---|---|
| 休 / 有 / 希望休 | `st-leaf` | 葉2枚、ヴェイン入り、leaf色 |
| 会議 / MTG | `st-bubble` | 雲型吹き出し+ドット3つ、pond色 |
| 出店 | `st-bag` | 取っ手付きショップバッグ、peach色 |
| A番 | `st-star` | 4点星(輝き)、sunshine色 |
| 給料日 / ボーナス | `st-coin` | 円マーク入りコイン、leaf-deep色 |
| 予定(custom) | `st-pin` | 画鋲、custom色 |

ステッカーは SVG sprite として `<defs><symbol id="st-leaf">...` 形式でテンプレ上部に定義、各チップで `<use href="#st-leaf"/>` 参照。

## 4. ステッカーの組込み

```css
.event {
  display: grid;
  grid-template-columns: 14px 1fr;
  align-items: center;
  gap: 4px;
  padding: 4px 5px;
  text-align: left;
}
.event .event-sticker {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
  opacity: 0.95;
}
.event .event-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
```

JS側 `eventTypeClass` の延長で `stickerId(summary)` を計算し、innerHTML に組込む。

```js
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

## 5. ヘッダー装飾

```html
<div class="header-deco" aria-hidden="true">
  <svg class="deco-cloud-1"><use href="#deco-cloud"/></svg>
  <svg class="deco-leaf-1"><use href="#deco-leaf-small"/></svg>
</div>
```

```css
.header-deco {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}
.deco-cloud-1 {
  position: absolute;
  top: 12px;
  right: -8px;
  width: 90px;
  height: 36px;
  opacity: 0.35;
  color: var(--peach);
}
.deco-leaf-1 {
  position: absolute;
  bottom: 8px;
  left: 60%;
  width: 24px;
  height: 24px;
  opacity: 0.3;
  color: var(--leaf);
  transform: rotate(-15deg);
}
```

雲は単純な丸2-3個の塊、葉は楕円+葉脈の軽スケッチ。

## 6. フィルターチップへの小ステッカー

`.chip.active` 時のみ、左に色合いに合った小ステッカー(8px)。inactive時は dot だけ。

```css
.chip .sticker { width: 10px; height: 10px; display: none; }
.chip.active .sticker { display: inline-block; }
.chip.active .dot { display: none; }
```

ボタン(`.btn`)はステッカー追加なし(かわいすぎ防止)。

## 7. 各シートのクリーム化

- 設定シート、Day シート、年間ヒート、Recall、ヒーローカード:背景クリーム系に統一
- 影とボーダーは新しい暖色シャドウへ
- リーフ・チーク系のラベルは新色相に追従

## 8. アニメーション

現状のもの維持。新規追加はゼロ。マスコット idle breath、heartFloat、todayDot 等そのまま。

## 9. 実装範囲

| ファイル | 役割 | 変更可否 |
|---|---|---|
| `build.py` | HTMLテンプレ + 定数 | ✅ 編集対象 |
| `index.html` 等生成物 | 自動生成 | ❌ 直接禁止 |
| `firebase-config.js` | 設定 | ❌ 触らない |
| `events.json` `extract_events.py` | 別目的 | ❌ 触らない |
| Firestore 本番データ | events / anniversaries | ❌ 書き込みしない |

## 10. コミット計画

| # | 内容 | 推定行数 | 安全余裕 |
|---|---|---|---|
| C1 | カラーパレット移行(`:root`変数とshadow) | +90/-80 | OK(150内) |
| C2 | SVGステッカー6種+チップ組込み+ヘッダー装飾 | +160/-50 | 監視(180目標) |

両コミットを別個に push、各 build 成功確認 + git diff 行数チェック。200行超で `git checkout` ロールバック → スコープ縮小して再コミット。

## 11. テスト計画

| C# | 確認項目 |
|---|---|
| C1 | クリーム背景確認、チップ色がビビッドに見える、影が暖色寄り、全シート色相整合 |
| C2 | 6種類のステッカーが各イベントチップ左に出る、ヘッダー右上に雲・左下に葉、フィルター active 時のみ小ステッカー |

両方 preview_eval で `document.querySelectorAll('.event-sticker').length` 等で素朴に検証。

## 12. ロールバック条件

- ビルドエラー(`python build.py` 失敗)
- HTMLサイズが30%以上変動
- preview起動でconsole error
- 既存機能(ヒーローカード/天気/同期/年間ヒート/Recall)のregression
- 1コミット差分が180行超

ロールバックは `git checkout build.py index.html manifest.json sw.js` で該当コミットだけ。他コミットは保持。

## 13. 非スコープ(YAGNI)

- フォント全体変更(Klee One/M PLUS Rounded)— 視認性低下リスク
- アジェンダビュー導入 — 別機能、別仕様書
- ユーザー任意ステッカー貼付(Cute Calendar 風)— 別タスク
- セル背景パターン(ノイズ)— 視認性ダウン懸念
- 過剰なアニメーション追加 — Calm Canvas 哲学を維持
