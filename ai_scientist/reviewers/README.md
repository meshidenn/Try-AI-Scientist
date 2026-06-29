# reviewers

Audit/review系sub-agentを支えるprompt素材、checklist、検証ロジックを置く層。

実体のsub-agent定義は `.agents/subagents/` に置く。このディレクトリでは、artifact audit、paper review、result interpretation、claim auditに共通する監査観点を管理する。

## 分割方針

- `artifact-auditor`: run直後、interpret前に結果artifactの健全性を確認する
- `paper-reviewer`: paperを書く場合だけ、paperを書く観点で、構成、主張、引用、図表、再現性、noveltyを確認する
- `result-interpreter`: 結果を解釈し、何が分かったか、何が未解決か、次にどの実験を行うべきかをまとめる
- `claim-auditor`: interpret後に、解釈、next plan、paper claimが実際のartifactと一致しているかを検証する

`result-interpreter` は、以前は実行担当、`search/`、review系の間で曖昧だった「結果を解釈して次のplanを考える」責務を明示的に担う。実行担当は `experiment-runner` とする。

## 想定するreview artifact

- `review/paper-review.md`
- `review/artifact-audit.md`
- `review/result-interpretation.md`
- `review/next-plan.md`
- `review/claim-audit.md`
- `review/rebuttal.md`
- `results/claims.json`
