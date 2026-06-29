# Try-AI-Scientist
Coding Agentを使って、AI-Scientistを作る。

# デザイン
1. サーベイフェーズとcoding phaseを分ける。
2. 人間が学習しやすいように、サーベイの結果をMarkdownで残す。
3. 追加でサーベイした場合、更新差分がわかるようにする。
4. 実験結果はcoding agentが読み返しやすいように、Markdownでも残す。
5. 実行は一旦ローカルや自宅サーバーで行う前提にする。

PC環境:

- MacBook Air (2026)
- home-server
- thinkstation

# ディレクトリ構成
`.agents/` はcoding agentに直接読ませるsub-agent/skill定義を置く。実際の役割指示はここに置き、Codex、Claude Code、Gemini CLIなどのagentが参照する。

`ai_scientist/` はAI-Scientistを動かす共通基盤を置く。coding agentそのものを置き換えるのではなく、runner、search、evaluator、reviewer、archive、agent向け共通仕様を管理する。

`projects/` は研究テーマごとの作業場所にする。各projectの中で、サーベイと実験を分ける。

```text
.agents/
  AGENTS.md
  subagents/
    surveyor.md
    experiment-runner.md
    artifact-auditor.md
    paper-reviewer.md
    result-interpreter.md
    claim-auditor.md
    archivist.md
  skills/
    literature-search/
    survey-update/
    experiment-logging/
    artifact-audit/
    result-verification/
    archive-run/

ai_scientist/
  runner/
  search/
  evaluators/
  reviewers/
  archive/
  agent/
    contracts/
    templates/
  references/
    ref-papers/

projects/
  <project-name>/
    project.yaml
    survey/
      README.md
      sources.md
      changelog.md
      updates/
    experiments/
      exp-001/
        spec.yaml
        README.md
        workspace/
        results/
          results.md
          scores.json
          claims.json
        figures/
        logs/
        review/
          artifact-audit.md
          paper-review.md
          result-interpretation.md
          next-plan.md
          claim-audit.md
          rebuttal.md
        paper/
```

# 実行イメージ
`.agents/` は実際のsub-agent定義、`ai_scientist/` はそれを支えるcontrol planeとして扱う。

`python -m ai_scientist ...` のようなCLIは将来の自動化案であり、MVPでは必須ではない。最初はcoding agentが `.agents/subagents/<role>.md` を読み、その役割としてproject内のartifactを更新する。

```text
projects/<project-name>/survey/
  -> surveyorが調査してMarkdownを更新する

projects/<project-name>/experiments/exp-001/spec.yaml
  -> experiment-runner/coding agentが読む
  -> workspaceでコードを書く、実験する
  -> evaluatorがscores.json/results.mdを作る
  -> artifact-auditorが結果artifactを監査する
  -> result-interpreterが結果を解釈し、次のplanを作る
  -> claim-auditorが解釈とclaimをartifactに照合する
  -> archiveがmanifestと成果物を整理する
```

`ai_scientist/` 以下の各dirは、sub-agentそのものではなく、sub-agentが使う機能境界として設計する。実体のsub-agent定義は `.agents/subagents/` に置く。

- `runner/`: sub-agentやcoding agentを起動し、workspaceとログを管理する
- `search/`: 次に試すidea/candidate/runを選ぶ
- `evaluators/`: 実験結果を機械的にscore化する
- `reviewers/`: artifact audit、paper review、result interpretation、claim auditなどの監査ロジックを管理する
- `archive/`: runの成果物、manifest、履歴を整理する
- `agent/`: `.agents/` から参照される共通契約、template、保存形式を置く

# sub-agent間の情報共有
sub-agent間の情報共有は、原則としてファイルベースで行う。直接会話で状態を渡すのではなく、project内のMarkdown、JSON、ログ、図、paperを共有メモリとして扱う。

主な受け渡し:

- `survey/README.md`: 人間とagentが読むサーベイ本文
- `survey/sources.md`: 参照文献とリンク
- `survey/changelog.md`: 追加サーベイ時の更新差分
- `experiments/<exp-id>/spec.yaml`: 実験の目的、仮説、評価指標、制約
- `experiments/<exp-id>/results/results.md`: 人間とagentが読む実験結果
- `experiments/<exp-id>/results/scores.json`: evaluatorが出す機械可読なscore
- `experiments/<exp-id>/results/claims.json`: paper内のclaimとartifactの対応
- `experiments/<exp-id>/review/artifact-audit.md`: interpret前の結果artifact監査
- `experiments/<exp-id>/review/result-interpretation.md`: 結果の解釈
- `experiments/<exp-id>/review/next-plan.md`: 次に試す実験計画
- `experiments/<exp-id>/review/paper-review.md`: paperを書く場合のpaper-reviewerの指摘
- `experiments/<exp-id>/review/claim-audit.md`: interpret後のclaim監査
- `experiments/<exp-id>/review/rebuttal.md`: experiment-runnerの応答と追加実験方針
- `experiments/<exp-id>/logs/`: 実行ログ、tool call、失敗理由

この方式にすると、途中から人間や別のcoding agentが入っても、状態を再構成しやすい。長期的には `archive/` がrunごとのmanifestを作り、どのsub-agentが何を読んで何を更新したかを追跡できるようにする。

# auditとreviewの分割
paperを書くとは限らないため、auditは1つにまとめない。標準フローは以下にする。

```text
survey
  -> spec
  -> experiment-runner
  -> artifact-auditor
  -> result-interpreter
  -> claim-auditor
  -> archivist
```

paperを書く場合だけ、`result-interpreter` の後にpaper draftと `paper-reviewer` を挟む。

```text
...
  -> result-interpreter
  -> paper draft
  -> paper-reviewer
  -> claim-auditor
  -> archivist
```

役割は以下に分ける。

- `artifact-auditor`: run直後、interpret前に `results.md`、`scores.json`、ログ、図、metric対応を確認する
- `paper-reviewer`: paperを書く観点で、構成、主張、引用、図表、再現性、noveltyをレビューする
- `result-interpreter`: 結果を解釈し、何が分かったか、何が未解決か、次にどの実験を行うべきかを `next-plan.md` に落とす
- `claim-auditor`: interpret後に、解釈、next plan、paper claimがartifactに支えられているかを検証する

以前の設計では、結果の解釈と次planの作成が実行担当、`search/`、review系の間に曖昧に分散していた。今後は `experiment-runner` は現在の `spec.yaml` の実行に集中する。`result-interpreter` が次planを明示的に担い、`search/` はその `next-plan.md` を入力として次candidateを選ぶ。

# 参考文献
AI-Scientist基盤そのものの参考文献は `ai_scientist/references/ref-papers/` に置く。

各研究project固有の文献やサーベイ結果は `projects/<project-name>/survey/` に置き、基盤設計の参考文献とは混ぜない。
