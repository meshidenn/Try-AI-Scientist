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

## Reproduction Implementation Runs

- token上限探索、endpoint疎通、parser/実装修正、再試行、性能診断は正式な研究実験ではない。`experiments/exp-xxx/`を作らず、`workspace/reproduction-runs/<issue-or-workflow>/runs/run-xxx/`に記録する。
- 各workflowの`README.md`に、目的、正式experimentとの境界、run一覧、旧pathを移した場合の対応表を残す。各runには設定、短い結果要約、判断を残す。
- 独立した仮説、比較、評価指標、成功判定を定めて研究上の結果として扱う段階でのみ、`experiments/exp-xxx/`を新設する。

## Git Tracking

- Gitには設定、manifest、入力hash、集計済み結果、判断記録を置く。raw completion、重複context snapshot、embedding、vector/index、途中storeなど再生成可能な大型生成物は`.gitignore`にする。
- stageは対象ファイルを明示する。`git add .`やproject全体の一括stageを使わず、commit前に`git diff --cached --name-only`と`git diff --cached --stat`で内容と容量を確認する。
- 生成物または非codeファイルが1 MiB以上なら、Git管理の必要性とmanifestによる代替を確認し、利用者の明示承認なしにstageしない。

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
