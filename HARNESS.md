# シフトカレンダー自動改善ハーネス

## 構成図

```
                ┌──────────────────────────┐
                │  スケジューラ(毎週月曜)  │
                └────────────┬─────────────┘
                             ▼
              ┌────────────────────────────┐
              │  指示役 (Orchestrator)     │
              │  shift-cal-orchestrator    │
              └────┬──────────────┬────────┘
       並列起動    │              │
            ┌─────▼────┐    ┌────▼─────┐
            │情報収集役│    │ レビュー役│
            │Researcher│    │ Reviewer │
            └─────┬────┘    └────┬─────┘
                  └──────┬───────┘
                         ▼
                   ┌──────────┐
                   │ 評価役   │
                   │Evaluator │
                   └────┬─────┘
                        ▼
                   ┌──────────┐
                   │ 変更役   │
                   │ Modifier │
                   └────┬─────┘
                        ▼
                   ┌──────────┐
                   │ 編集役   │ ← 唯一コード編集する役
                   │  Editor  │ ← build→preview→commit→push
                   └──────────┘
```

## 役と責任

| 役 | ファイル | 入力 | 出力 | ツール権限 |
|---|---|---|---|---|
| 指示役 | shift-cal-orchestrator.md | 起動指示 | 最終報告 | Agent, Read, Bash |
| 情報収集役 | shift-cal-researcher.md | (なし) | research-{date}.md | WebSearch, WebFetch, Read |
| レビュー役 | shift-cal-reviewer.md | コード | review-{date}.md | Read, Grep, Glob, Bash |
| 評価役 | shift-cal-evaluator.md | 上記2件 | priorities-{date}.md | Read |
| 変更役 | shift-cal-modifier.md | priorities | plan-{date}.md | Read, Grep, Glob |
| 編集役 | shift-cal-editor.md | plan | コミット | Read, Edit, Write, Bash |

## 安全設計

- **build.py のみ編集**: index.html等は自動生成されるため直接編集禁止
- **1サイクル最大3件の変更**: 過剰修正を防ぐ
- **200行超の差分は中止**: 大規模変更は人手で確認
- **build失敗・preview失敗で即ロールバック**
- **events コレクションは触らない**: 本番データを汚さない
- **`firebase-config.js` 触らない**: API設定保護
- **--no-verify, --force 等の危険フラグ禁止**
- **無限ループ防止**: 5回リトライで諦める

## 起動方法

### 手動実行
```
Agent ツールで shift-cal-orchestrator を呼ぶ:
「自動改善パイプラインを実行」
```

### 自動実行
- `scheduled-tasks` で毎週月曜 09:03 に起動
- タスクID: `shift-cal-weekly-improve`
- アプリ起動中のみ動く(閉じてれば次回起動時)

## キャッシュ

各サイクルの成果物は `.claude/harness-cache/` に日付付きで保存:
- `research-YYYY-MM-DD.md`
- `review-YYYY-MM-DD.md`
- `priorities-YYYY-MM-DD.md`
- `plan-YYYY-MM-DD.md`

過去履歴として残るので、後から「先週何を変えた?」を辿れる。

## 停止方法

スケジューラを止める:
- `mcp__scheduled-tasks__list_scheduled_tasks` で確認
- 該当タスクを削除 or disabled に
