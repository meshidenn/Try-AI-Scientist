# Try-AI-Scientist Agent Instructions

このrepoでは、AI-Scientistをcoding agentで実現する。

## 基本方針

- 常に日本語で応答する。
- サーベイフェーズとcoding phaseを分ける。
- 人間とagentが後から読み返せるように、重要な状態はMarkdown、JSON、ログ、図、paperとしてfilesystemに残す。
- sub-agent間の正本は会話履歴ではなく、`projects/<project-name>/` 以下のartifactである。
- `ai_scientist/references/ref-papers/` はAI-Scientist基盤設計の参考文献であり、project固有の文献とは混ぜない。

## Sub-agent

実体のsub-agent定義は `.agents/subagents/` に置く。

- `surveyor`: 文献調査とsurvey更新
- `experiment-runner`: 現在の `spec.yaml` に沿ったコード実装、実行、結果整理
- `artifact-auditor`: run直後に結果artifactの健全性を確認
- `paper-reviewer`: paperを書く観点でのreview
- `result-interpreter`: 結果解釈と次planの作成
- `claim-auditor`: 解釈、next plan、paper claimとartifactの照合
- `archivist`: run成果物の整理とmanifest更新

## Skills

繰り返し使うrepo固有手順は `.agents/skills/` に置く。

- `literature-search`
- `survey-update`
- `experiment-logging`
- `artifact-audit`
- `result-verification`
- `archive-run`

## Artifact Rules

projectは以下の形を基本にする。

```text
projects/<project-name>/
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

## Safety

- `.env` やAPI keyを成果物に含めない。
- 実験結果をpaperに書くときは、必ず対応するartifactを残す。
- 推測で実験済みと書かない。未実行なら未実行と明記する。
- 既存artifactを更新するときは、変更理由が分かるようにMarkdownへ短く記録する。
