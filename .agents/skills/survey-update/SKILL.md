---
name: survey-update
description: Survey markdownを、人間が学習しやすく、coding agentが実験設計に使いやすい形で更新する。
---

# Survey Update Skill

## Purpose

サーベイを単なるリンク集にせず、研究判断に使える知識として更新する。

## Outputs

- `survey/README.md`
- `survey/sources.md`
- `survey/changelog.md`
- `survey/updates/YYYY-MM-DD.md`

## Survey README Structure

推奨構成:

```markdown
# Survey

## Research Question

## Current Understanding

## Relevant Prior Work

## Methods And Design Ideas

## Evaluation And Benchmarks

## Risks And Open Questions

## Implications For Experiments
```

## Update Rules

- `README.md` は統合版として保つ。
- `updates/YYYY-MM-DD.md` には今回追加した内容だけを書く。
- `changelog.md` には変更差分を短く書く。
- 後続の `experiment-runner` と `result-interpreter` が使えるように、最後に実験設計への示唆を書く。
