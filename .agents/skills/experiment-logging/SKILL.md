---
name: experiment-logging
description: 実験結果をMarkdownとJSONで残し、後続agentが読み返せる状態にする。
---

# Experiment Logging Skill

## Purpose

実験の再現性、比較、reviewを可能にするために、結果と実行記録を標準形式で保存する。

## Required Outputs

- `experiments/<exp-id>/README.md`
- `experiments/<exp-id>/results/results.md`
- `experiments/<exp-id>/results/scores.json`
- `experiments/<exp-id>/logs/`

## results.md Structure

```markdown
# Results

## Summary

## Setup

## Metrics

## Main Results

## Figures

## Failures And Negative Results

## Reproduction

## Notes For Reviewer
```

## scores.json Shape

```json
{
  "experiment_id": "exp-001",
  "status": "completed",
  "metrics": {
    "primary": {
      "name": "metric_name",
      "value": 0.0,
      "higher_is_better": true
    }
  },
  "artifacts": {
    "results_md": "results/results.md",
    "figures": [],
    "logs": []
  }
}
```

## Rules

- 未実行、失敗、成功を区別する。
- 標準出力だけに重要情報を残さない。
- 図を作ったら、何を示す図かを `results.md` に書く。
- paperに書くclaimは、必ずartifactに対応させる。
