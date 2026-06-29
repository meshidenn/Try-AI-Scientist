# ai_scientist

AI-Scientistを動かす共通基盤を置くディレクトリ。

この層はcoding agentを細かく再実装するのではなく、coding agentが研究を進めやすいように、実行、探索、評価、レビュー、保存、再開を支える。

`ai_scientist/` 以下の各dirは、sub-agentそのものではない。実体のsub-agent定義は `.agents/subagents/` に置く。各dirは、sub-agentが研究workflowを進めるときに使う機能モジュール、prompt生成素材、保存形式、検証ロジックを管理する境界である。

## 役割

- `runner/`: coding agentのjob起動、ローカル/SSH実行、再開処理
- `search/`: tree searchやevolutionary searchの管理
- `evaluators/`: scorable taskの評価関数、score出力、検証
- `reviewers/`: artifact audit、paper review、result interpretation、claim auditの監査ロジック
- `archive/`: artifact manifest、run履歴、git/export管理
- `agent/`: `.agents/` から参照される共通契約、template、保存形式
- `references/`: AI-Scientist基盤設計の参考文献

## 想定するsub-agent

sub-agentの役割定義は `.agents/subagents/` に置く。

- `surveyor`: 文献調査を行い、projectの `survey/` を更新する
- `experiment-runner`: `spec.yaml` を読み、workspaceでコードを書き、実験を実行し、観察された事実を記録する
- `artifact-auditor`: run直後に結果artifactの健全性を確認する
- `paper-reviewer`: paperを書く観点で、構成、主張、引用、図表、再現性、noveltyをレビューする
- `result-interpreter`: 結果を解釈し、分かったこと、未解決点、次の実験planをまとめる
- `claim-auditor`: 解釈、next plan、paper claimと実際のartifactを照合し、`claims.json` を確認する
- `archivist`: runの成果物を整理し、manifestと履歴を更新する

## 情報の受け渡し

sub-agent間の受け渡しは、原則として直接会話ではなく、project内のartifactを通じて行う。

```text
surveyor
  -> survey/README.md
  -> survey/sources.md
  -> survey/changelog.md

experiment-runner
  <- survey/
  <- experiments/<exp-id>/spec.yaml
  -> experiments/<exp-id>/workspace/
  -> experiments/<exp-id>/results/results.md
  -> experiments/<exp-id>/results/scores.json
  -> experiments/<exp-id>/paper/

artifact-auditor
  <- experiments/<exp-id>/workspace/
  <- experiments/<exp-id>/results/
  <- experiments/<exp-id>/figures/
  <- experiments/<exp-id>/logs/
  -> experiments/<exp-id>/review/artifact-audit.md

paper-reviewer
  <- experiments/<exp-id>/workspace/
  <- experiments/<exp-id>/results/
  <- experiments/<exp-id>/figures/
  <- experiments/<exp-id>/paper/
  -> experiments/<exp-id>/review/paper-review.md

result-interpreter
  <- experiments/<exp-id>/results/
  <- experiments/<exp-id>/figures/
  <- experiments/<exp-id>/logs/
  <- experiments/<exp-id>/review/artifact-audit.md
  <- experiments/<exp-id>/review/paper-review.md (optional)
  -> experiments/<exp-id>/review/result-interpretation.md
  -> experiments/<exp-id>/review/next-plan.md

claim-auditor
  <- experiments/<exp-id>/results/
  <- experiments/<exp-id>/review/result-interpretation.md
  <- experiments/<exp-id>/review/next-plan.md
  <- experiments/<exp-id>/paper/ (optional)
  -> experiments/<exp-id>/results/claims.json

archivist
  <- experiments/<exp-id>/
  -> manifest and archived snapshot
```

この設計では、各sub-agentは同じrun directoryを共有メモリとして読む。runnerは必要なartifactをpromptに要約して渡すが、正本はMarkdown、JSON、ログ、図、paperとしてfilesystem上に残す。
