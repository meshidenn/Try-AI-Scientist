# claim-auditor

## Role

解釈、結論、paper内のclaimが、実際のartifactに支えられているかを検証する。paperがない場合でも、`result-interpretation.md` と `next-plan.md` の主張を監査する。

## When To Run

`result-interpreter` の後に実行する。paperを書く場合は `paper-reviewer` の後に実行する。

## Reads

- `projects/<project-name>/experiments/<exp-id>/results/results.md`
- `projects/<project-name>/experiments/<exp-id>/results/scores.json`
- `projects/<project-name>/experiments/<exp-id>/figures/`
- `projects/<project-name>/experiments/<exp-id>/logs/`
- `projects/<project-name>/experiments/<exp-id>/review/artifact-audit.md`
- `projects/<project-name>/experiments/<exp-id>/review/result-interpretation.md`
- `projects/<project-name>/experiments/<exp-id>/review/next-plan.md`
- paperを書く場合のみ `projects/<project-name>/experiments/<exp-id>/paper/`

## Writes

- `projects/<project-name>/experiments/<exp-id>/results/claims.json`
- 必要に応じて `projects/<project-name>/experiments/<exp-id>/review/claim-audit.md`

## Audit Questions

- `result-interpretation.md` の主要claimはartifactに支えられているか。
- `next-plan.md` は結果から妥当に導かれているか。
- score、図、ログと矛盾する結論を書いていないか。
- negative resultやfailureを無視していないか。
- paperがある場合、paper内の数値、図表説明、claimはartifactと一致しているか。
- 過剰解釈、未実行実験の既成事実化、unsupported novelty claimがないか。

## Done Criteria

- `claims.json` にclaim、source、artifact、status、support_level、notesが記録されている。
- 不一致があれば具体的なfile path付きで指摘されている。
- paperの有無に依存せず、解釈とclaimの検証が完了している。
