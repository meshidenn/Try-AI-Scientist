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
    reproduction-runs/       # 正式実験ではない実装・再現の試行記録
      <issue-or-workflow>/
        README.md
        runs/
          run-001/
  data/                      # 共有のsource data、metadata、再利用可能な派生data
    raw/                     # 取得元snapshotとsource manifest
    derived/                 # triplet、embedding、indexなどの共有中間生成物
  survey/
    README.md
    sources.md
    changelog.md
    updates/
  paper/                    # project全体の論文・原稿
    draft.md
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
      manifest.json
```

## Ownership Rules

- `pyproject.toml` にproject固有の依存、package metadata、build設定、test/lint設定を置く。repo rootの設定にproject固有依存を集約しない。
- `src/<package_name>/` にinstall可能なproject本体を置く。標準の責務分離は `domain/`、`application/`、`infrastructure/`、`interfaces/` とする。
- Clean Architectureの依存方向は `interfaces -> application -> domain`、`infrastructure -> application/domain` とする。domainから外部adapterへ依存しない。
- `tests/` にunit/integration testを置く。package内、`workspace/`、`experiments/<exp-id>/`に新しいtestを置かない。
- `workspace/` はlegacy互換script、実験補助、移行中の共有実装に限定する。新規の本体実装とtestを置かない。
- `workspace/reproduction-runs/<issue-or-workflow>/runs/run-xxx/` にはtoken探索、endpoint疎通、parser/実装修正、再試行などの試行記録を置く。設定、短い結果要約、判断記録を追跡し、正式experimentと混同しない。
- 実行器は`--root projects/<project-name>/experiments/<exp-id>`で結果保存先を明示する。
- `data/` に全expで共有する原資料、source manifest、前処理済み入力、再利用可能な派生dataを置く。`data/raw/` は取得元snapshotとsource manifest、`data/derived/` はtriplet、embedding、indexなど実験の前提となる中間生成物に使う。秘密情報や無断取得データを置かない。
- `data/derived/` の各artifactは `manifest.json` にcorpus revision、入力hash、生成model・設定、依存artifactを記録する。実験では派生data本体を複製せず、使用artifactのpath・manifest hashを `inputs/` または実験manifestへ記録する。
- `experiments/<exp-id>/` に仮説、入力条件、run log、評価、reviewを置く。実装コード、実行script、notebook、`__pycache__/`は置かない。
- `experiments/<exp-id>/` は独立した仮説、比較、評価指標、成功判定を持つ正式な実験に限る。再現実装の試行錯誤には新しい`exp`番号を割り当てない。
- `<project>/paper/` にproject全体の論文原稿、参考文献整理、投稿用原稿を置く。個別experimentの結果を参照するが、experiment配下に論文原稿を置かない。
- `spec.yaml` は実験設計の正本とする。仮説、比較対象、入力、評価指標、sample、制約、成功判定を明記する。
- `experiment-logging` は設計を決めず、実行済みの条件と結果を記録する。このskillは配置と責務を決める。

## Workflow

1. 既存の`project.yaml`、`survey/`、`experiments/`、dirty worktreeを確認する。
2. 新規projectはcanonical layoutとproject固有の`pyproject.toml`を作る。packageは`src/<package_name>/`、testは`tests/`に置く。
3. Clean Architectureの責務と依存方向を確認してから、本体実装・adapter・interfaceを配置する。
4. 既存projectは過去artifactの追跡性を守り、必要なら互換wrapperとmigration READMEを用意して段階的にpackage化する。
5. 新しいrunが正式experimentか実装試行かを判定する。前者だけ`spec.yaml`を先に作り、後者は`workspace/reproduction-runs/<issue-or-workflow>/README.md`に目的と正式experimentとの境界を記す。
6. 入力・出力の場所、gitignore、再現コマンド、manifestを合わせて更新する。
7. `find experiments -type f`で実装codeとtestがexp配下にないこと、`tests/`がproject testの正本であること、package importと再現コマンドが動くことを確認する。

## Legacy Migration

既存runのpathを変えるとlogやmanifestの追跡性を壊す場合がある。移行時は次を守る。

- historical outputは無断で移動・削除しない。移す場合はmanifestと再現手順を同時に更新する。
- 過去に`experiments/`へ置いた実装試行を移す場合は、`workspace/reproduction-runs/<issue-or-workflow>/README.md`に旧pathと新pathの対応を残す。追跡対象のartifactはGitから外さず、Git上のrenameとして移す。
- 既存の`experiments/<exp-id>/workspace/`はinput/output snapshotとして一時的に残してよいが、source codeを置かない。
- 既存projectの`workspace/`にある実装とtestを移行する場合、旧pathを参照するmanifest・log・READMEを同時に更新する。過去artifactの内容は書き換えない。
- 新規expは`inputs/`と`outputs/`を使う。例外を残す場合はREADMEまたはmanifestに理由を書く。

## Completion Check

- 新規projectの本体codeは`src/<package_name>/`にあり、project固有の`pyproject.toml`からinstallできる。
- projectのunit/integration testは`tests/`にある。
- `workspace/`はlegacy互換script・実験補助・移行中の共有実装に限定する。
- expには設計とevidenceだけがある。
- 再現実装の試行は`workspace/reproduction-runs/`に分離されている。
- `spec.yaml`、結果、log、manifestが相互に参照可能である。
- project全体の論文原稿は`paper/`にあり、experiment配下に重複した論文原稿がない。
- 関連skill、subagent定義、再現手順が同じpath規約を指す。
