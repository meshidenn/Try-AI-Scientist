---
name: archive-run
description: 完了または中断したrunをmanifest化し、後から比較、再開、reviewできる形で整理する。
---

# Archive Run Skill

## Purpose

各runの入力、出力、score、review、paper、状態を1つのmanifestで追跡する。

## Output

- `experiments/<exp-id>/manifest.json`

## manifest.json Shape

```json
{
  "project": "project-name",
  "experiment_id": "exp-001",
  "status": "completed",
  "objective": "",
  "agent_runs": [],
  "inputs": {
    "spec": "spec.yaml",
    "survey": "../../survey/README.md"
  },
  "artifacts": {
    "workspace": "workspace/",
    "results": "results/results.md",
    "scores": "results/scores.json",
    "claims": "results/claims.json",
    "figures": "figures/",
    "paper": "paper/",
    "review": "review/"
  },
  "summary": "",
  "next_actions": []
}
```

## Rules

- 成功runだけでなく、失敗runもarchiveする。
- secrets、`.env`、不要なcacheをmanifest対象にしない。
- 次に読むagentが、manifestから状態を把握できるようにする。
- `next-plan.md` がある場合は `next_actions` に要約する。
