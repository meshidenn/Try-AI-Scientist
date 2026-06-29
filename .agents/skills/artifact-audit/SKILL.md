---
name: artifact-audit
description: Run直後、interpret前に結果artifactの健全性を確認する。
---

# Artifact Audit Skill

## Purpose

`result-interpreter` が壊れた結果や欠けたログを解釈しないようにする。

## Inputs

- `spec.yaml`
- `README.md`
- `workspace/`
- `results/results.md`
- `results/scores.json`
- `figures/`
- `logs/`

## Output

- `review/artifact-audit.md`

## artifact-audit.md Structure

```markdown
# Artifact Audit

## Verdict
PASS | WARN | FAIL

## Checked Artifacts

## Blocking Issues

## Warnings For Interpretation

## Notes
```

## Rules

- `FAIL` の場合、`result-interpreter` が解釈を進めるべきでない理由を書く。
- 実験の研究的な意味づけや次planは書かない。
- metric名、向き、単位、dataset split、baseline名の明らかな矛盾を確認する。
- partial runやtimeoutを成功扱いしない。
