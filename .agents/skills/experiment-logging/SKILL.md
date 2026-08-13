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

## Code And Artifact Separation

- 再利用する実装、テスト、起動scriptは `projects/<project-name>/workspace/` に置く。
- `experiments/<exp-id>/` はspec、入力・出力snapshot、log、評価、reviewなどの実験artifactだけを置く。`.py`、`.sh`、notebook、`__pycache__/`を置かない。
- 共通実行器は結果保存先を暗黙に決めず、`--root projects/<project-name>/experiments/<exp-id>` のように対象expを明示して実行する。
- 再現手順は共通workspaceのscriptと明示した`--root`を記載する。実験番号を含む実装pathを参照しない。
- 新規expは`inputs/`と`outputs/`にsnapshotと生成物を置く。legacyの`workspace/` snapshotを残す場合は、READMEまたはmanifestに理由を書く。

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
