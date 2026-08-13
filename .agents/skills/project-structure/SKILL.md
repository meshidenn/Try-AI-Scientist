---
name: project-structure
description: AI研究projectの作成・再編・監査時に、共有コード、共有データ、survey、実験artifactの責務と配置を標準化する。projectの雛形作成、exp配下からのコード移動、構成規約の更新、再現性を保つ移行で使用する。
---

# Project Structure

## Canonical Layout

新規projectでは次を基準にする。

```text
projects/<project-name>/
  project.yaml
  pyproject.toml             # project固有のpackage metadata・依存・tool設定
  src/<package_name>/        # install可能なproject package
    domain/
    application/
    infrastructure/
    interfaces/
  tests/                     # unit/integration test
  workspace/                 # legacy互換script・実験補助・移行中の共有実装
  data/                      # 共有のsource dataとmetadata（必要ならgitignore）
  survey/
    README.md
    sources.md
    changelog.md
    updates/
  experiments/
    exp-001/
      spec.yaml
      README.md
      inputs/                # 実験固有の入力manifest・小さいsnapshot
      outputs/               # 生成物。通常はgitignore
      results/
        results.md
        scores.json
        claims.json
      figures/
      logs/
      review/
      paper/
      manifest.json
```

## Ownership Rules

- `pyproject.toml` にproject固有の依存、package metadata、build設定、test/lint設定を置く。repo rootの設定にproject固有依存を集約しない。
- `src/<package_name>/` にinstall可能なproject本体を置く。標準の責務分離は `domain/`、`application/`、`infrastructure/`、`interfaces/` とする。
- Clean Architectureの依存方向は `interfaces -> application -> domain`、`infrastructure -> application/domain` とする。domainから外部adapterへ依存しない。
- `tests/` にunit/integration testを置く。package内、`workspace/`、`experiments/<exp-id>/`に新しいtestを置かない。
- `workspace/` はlegacy互換script、実験補助、移行中の共有実装に限定する。新規の本体実装とtestを置かない。
- 実行器は`--root projects/<project-name>/experiments/<exp-id>`で結果保存先を明示する。
- `data/` に全expで共有する原資料、source manifest、前処理済み入力を置く。秘密情報や無断取得データを置かない。
- `experiments/<exp-id>/` に仮説、入力条件、run log、生成物、評価、reviewを置く。実装コード、実行script、notebook、`__pycache__/`は置かない。
- `spec.yaml` は実験設計の正本とする。仮説、比較対象、入力、評価指標、sample、制約、成功判定を明記する。
- `experiment-logging` は設計を決めず、実行済みの条件と結果を記録する。このskillは配置と責務を決める。

## Workflow

1. 既存の`project.yaml`、`survey/`、`experiments/`、dirty worktreeを確認する。
2. 新規projectはcanonical layoutとproject固有の`pyproject.toml`を作る。packageは`src/<package_name>/`、testは`tests/`に置く。
3. Clean Architectureの責務と依存方向を確認してから、本体実装・adapter・interfaceを配置する。
4. 既存projectは過去artifactの追跡性を守り、必要なら互換wrapperとmigration READMEを用意して段階的にpackage化する。
5. 新規expでは`spec.yaml`を先に作り、codeからexpを暗黙に選ばない。
6. 入力・出力の場所、gitignore、再現コマンド、manifestを合わせて更新する。
7. `find experiments -type f`で実装codeとtestがexp配下にないこと、`tests/`がproject testの正本であること、package importと再現コマンドが動くことを確認する。

## Legacy Migration

既存runのpathを変えるとlogやmanifestの追跡性を壊す場合がある。移行時は次を守る。

- historical outputは無断で移動・削除しない。移す場合はmanifestと再現手順を同時に更新する。
- 既存の`experiments/<exp-id>/workspace/`はinput/output snapshotとして一時的に残してよいが、source codeを置かない。
- 既存projectの`workspace/`にある実装とtestを移行する場合、旧pathを参照するmanifest・log・READMEを同時に更新する。過去artifactの内容は書き換えない。
- 新規expは`inputs/`と`outputs/`を使う。例外を残す場合はREADMEまたはmanifestに理由を書く。

## Completion Check

- 新規projectの本体codeは`src/<package_name>/`にあり、project固有の`pyproject.toml`からinstallできる。
- projectのunit/integration testは`tests/`にある。
- `workspace/`はlegacy互換script・実験補助・移行中の共有実装に限定する。
- expには設計とevidenceだけがある。
- `spec.yaml`、結果、log、manifestが相互に参照可能である。
- 関連skill、subagent定義、再現手順が同じpath規約を指す。
