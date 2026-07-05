# Try-AI-Scientist Agent Instructions

<!-- 正本: .agents/AGENTS.md。ルートの AGENTS.md / CLAUDE.md はこのファイルへの symlink。編集は必ずここで行う。 -->

このrepoでは、AI-Scientist風の研究workflowをcoding agentで実行する。

## 基本方針

- 常に日本語で応答する。
- サーベイフェーズとcoding phaseを分ける。
- 重要な状態は会話履歴ではなく、Markdown、JSON、ログ、図、paperなどのfilesystem artifactに残す。
- sub-agent間の正本は `projects/<project-name>/` 以下のartifactである。
- 未実行の実験を実行済みとして扱わない。推測と実測は明確に分ける。

## Python Package Management

- Python依存はrepo rootの `pyproject.toml` と `uv.lock` で管理する。
- 新しいPython依存を追加するときは `uv add <package>` を使い、`requirements.txt` や個別experimentの依存ファイルを増やさない。
- 実験やscriptは原則 `uv run python ...` または `uv run <command>` で実行する。
- `pip install`、`python -m venv`、手作業の `.venv` 作成は原則使わない。既存環境の都合で一時的に使った場合は、理由をartifactに残す。
- project固有の生成データ、submission、環境ディレクトリはartifact本文に要約し、必要以上にgit管理しない。

## 有効なAgent定義

実体のsub-agent定義は `.agents/subagents/` に置く。

- `surveyor`: 文献調査とsurvey更新
- `experiment-runner`: 現在の `spec.yaml` に沿ったコード実装、実行、結果整理
- `artifact-auditor`: run直後に結果artifactの健全性を確認
- `result-interpreter`: 結果解釈と次planの作成
- `paper-reviewer`: paperを書く観点でのreview
- `claim-auditor`: 解釈、next plan、paper claimとartifactの照合
- `archivist`: run成果物の整理とmanifest更新

繰り返し使うrepo固有手順は `.agents/skills/` に置く。作業内容がskillに対応する場合は、該当する `SKILL.md` を読んでから作業する。

- `literature-search` / `survey-update` / `experiment-logging` / `artifact-audit` / `result-verification` / `archive-run`

## ai_scientist Directory

現状の `ai_scientist/` は実行系ではない。MVPではcoding agentが `.agents/subagents/*.md` の役割定義を読み、project artifactを直接更新する。

- `ai_scientist/references/ref-papers/` はAI-Scientist基盤設計の参考文献置き場として使う。
- project固有の文献やsurveyは `projects/<project-name>/survey/` に置き、基盤設計の参考文献と混ぜない。
- `runner/`、`search/`、`evaluators/`、`reviewers/`、`archive/`、`agent/` は将来構想の境界であり、現時点ではsub-agentが通常参照する実体ではない。
- 新しい実行ロジックや共通契約を追加するまでは、`ai_scientist/references/` 以外に依存を増やさない。

## Project Artifacts

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

## Workflow

標準フロー:

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

## Safety

- `.env` やAPI keyを成果物に含めない。
- 実験結果をpaperに書くときは、必ず対応するartifactを残す。
- 既存artifactを更新するときは、変更理由が分かるようにMarkdownへ短く記録する。
- 既存の未関係な変更は戻さない。
