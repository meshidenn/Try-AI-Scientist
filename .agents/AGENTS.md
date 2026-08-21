# Try-AI-Scientist Agent Instructions

<!-- 正本: .agents/AGENTS.md。ルートの AGENTS.md / CLAUDE.md はこのファイルへの symlink。編集は必ずここで行う。 -->

このrepoでは、AI-Scientist風の研究workflowをcoding agentで実行する。

## 基本方針

- 常に日本語で応答する。
- サーベイフェーズとcoding phaseを分ける。
- 重要な状態は会話履歴ではなく、Markdown、JSON、ログ、図、paperなどのfilesystem artifactに残す。
- sub-agent間の正本は `projects/<project-name>/` 以下のartifactである。
- 未実行の実験を実行済みとして扱わない。推測と実測は明確に分ける。

## Personal Opsとの接続

- このrepoは個人プロジェクト管理では `meshidenn/Try-AI-Scientist` として扱う。横断状態の正本はGitHub IssueとPersonalProjectに置く。
- このrepoのChatはIssueなしで開始してよい。Issueは作業開始の必須条件ではない。
- 作業が複数セッションにまたがる、独立した完了条件を持つ、再開・判断・実験成果物の参照が必要になった場合は、Issue化を提案する。
- Issueを作成・更新・クローズする前、またはPersonalProjectを更新する前には、対象、変更内容、理由を示して明示的な承認を得る。
- 既存Issueがある作業では、作業開始、ブロッカー、重要な判断、終了時に結果と次の一手をIssueへ記録する。Project fieldsは横断状態だけに使い、研究artifactの内容を複製しない。
- 朝の横断整理は `personal-ops` で行う。ここでは実験・実装・調査を進め、詳細なIssue運用は `personal-issue-ops` skill と `personal-ops/ops/` を参照する。

## Python Package Management

- 各projectはproject直下の `pyproject.toml` で依存、metadata、build設定を管理する。
- repo rootの `pyproject.toml` はrepo全体のtoolingまたは共通設定に限り、project固有の依存を追加しない。
- 各projectはinstall可能なPython packageとして構成し、標準配置は `src/<package_name>/` とする。projectのtestは `tests/` からpackageをimportして検証する。

- Python依存は対象projectの `pyproject.toml` とproject単位のlockfileで管理する。repo rootのlockfileへproject固有依存を集約しない。
- 新しいPython依存を追加するときは対象projectのディレクトリで `uv add <package>` を使い、`requirements.txt` や個別experimentの依存ファイルを増やさない。
- 実験やscriptは対象projectのpackage entry point、`uv run python -m <package>...`、またはprojectの定義済みscriptで実行する。
- `pip install`、`python -m venv`、手作業の `.venv` 作成は原則使わない。既存環境の都合で一時的に使った場合は、理由をartifactに残す。
- project固有の生成データ、submission、環境ディレクトリはartifact本文に要約し、必要以上にgit管理しない。

## Architecture And Testing

- 新規projectと大規模な再編ではClean Architectureを意識し、依存方向を `interfaces -> application -> domain`、`infrastructure -> application/domain` に保つ。
- `domain/` は業務・研究上の概念、値、ルールを置き、外部ライブラリ、filesystem、HTTP、CLIへ依存させない。
- `application/` はuse case、workflow、portを置き、domainを組み合わせる。具体的なadapterの詳細を直接持たない。
- `infrastructure/` はPDF parser、モデルAPI、filesystem、databaseなどの具体adapterを置く。
- `interfaces/` はCLI、HTTP、入出力schemaなど、外部との境界を置く。
- projectのunit testとintegration testはproject直下の `tests/` に置く。package内や `workspace/` に新しいtestを置かない。

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

- `project-structure` / `literature-search` / `survey-update` / `experiment-logging` / `artifact-audit` / `result-verification` / `archive-run`

## ai_scientist Directory

現状の `ai_scientist/` は実行系ではない。MVPではcoding agentが `.agents/subagents/*.md` の役割定義を読み、project artifactを直接更新する。

- `ai_scientist/references/ref-papers/` はAI-Scientist基盤設計の参考文献置き場として使う。
- project固有の文献やsurveyは `projects/<project-name>/survey/` に置き、基盤設計の参考文献と混ぜない。
- `runner/`、`search/`、`evaluators/`、`reviewers/`、`archive/`、`agent/` は将来構想の境界であり、現時点ではsub-agentが通常参照する実体ではない。
- 新しい実行ロジックや共通契約を追加するまでは、`ai_scientist/references/` 以外に依存を増やさない。

## Project Structure

projectの新規作成、再編、exp配下からのcode移動では `project-structure` skillに従う。

```text
projects/<project-name>/
  project.yaml
  pyproject.toml             # project固有のpackage metadata・依存・tool設定
  src/<package-name>/        # install可能なproject package
    domain/
    application/
    infrastructure/
    interfaces/
  tests/                     # projectのunit/integration test
  workspace/                 # legacy互換script、実験補助、移行中の共有実装
  data/                      # 共有のsource dataとmetadata
  survey/
  paper/                    # project全体の論文・原稿
  experiments/
    exp-001/
      spec.yaml
      README.md
      inputs/                # 実験固有の入力manifest・snapshot
      outputs/               # 生成物。通常はgitignore
      results/
        results.md
        scores.json
        claims.json
      figures/
      logs/
      review/
      manifest.json
```

- `pyproject.toml` はproject固有の依存、package metadata、build設定、test/lint設定の正本とする。
- `src/<package-name>/` はinstall可能なproject本体とし、Clean Architectureの責務別packageを置く。
- `tests/` はprojectのunit/integration testの正本とする。
- `workspace/` はlegacy互換script、実験補助、移行中の共有実装に限定する。新規の本体実装とtestは置かない。
- 実行器は`--root projects/<project-name>/experiments/<exp-id>`で結果保存先を明示する。
- `data/` は共有の入力・metadataを置く。`experiments/<exp-id>/` は設計とevidenceだけを置き、`.py`、`.sh`、notebook、`__pycache__/`を置かない。
- 既存runの追跡性を守るため、legacyの`experiments/<exp-id>/workspace/`はinput/output snapshotとして残せるが、source codeを置かない。新規expは`inputs/`と`outputs/`を使う。
- 既存projectをpackage化するときは、過去artifactのpathを無断で移動・削除しない。互換wrapperまたはmigration READMEを用意し、新規実行の正本だけをpackage pathへ移す。
- `spec.yaml` は実験設計の正本であり、仮説、baseline、入力、評価指標、sample、制約、成功判定を定義する。`experiment-logging`は設計を決めず、実行済みの条件と結果を記録する。

## Workflow

標準フロー:

```text
project-structure
  -> survey
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
