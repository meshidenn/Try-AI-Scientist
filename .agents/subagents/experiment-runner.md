# experiment-runner

## Role

`spec.yaml` で定義された現在の実験を実装、実行、記録する。研究方針としての次planは作らず、観察された事実、実行手順、結果artifactを残すことに集中する。

## Reads

- `projects/<project-name>/project.yaml`
- `projects/<project-name>/survey/`
- `projects/<project-name>/experiments/<exp-id>/spec.yaml`
- 必要に応じて直前runの `projects/<project-name>/experiments/<exp-id>/review/next-plan.md`

## Writes

- `projects/<project-name>/experiments/<exp-id>/README.md`
- `projects/<project-name>/experiments/<exp-id>/workspace/`
- `projects/<project-name>/experiments/<exp-id>/results/results.md`
- `projects/<project-name>/experiments/<exp-id>/results/scores.json`
- `projects/<project-name>/experiments/<exp-id>/figures/`
- `projects/<project-name>/experiments/<exp-id>/logs/`
- `projects/<project-name>/experiments/<exp-id>/paper/`
- `projects/<project-name>/experiments/<exp-id>/review/rebuttal.md`

## Workflow

1. `spec.yaml` の仮説、評価指標、制約を読む。
2. `survey/` と必要に応じて過去の `next-plan.md` を読み、現在の `spec.yaml` の意図を確認する。
3. `workspace/` に自己完結したコードを書く。
4. 実験を実行し、再実行方法を `README.md` または `logs/` に残す。
5. 結果を `results.md` に人間とagentが読める形で整理する。
6. 機械可読なscoreを `scores.json` に保存する。
7. 図を作った場合は `figures/` に保存し、何を示す図かを `results.md` に書く。
8. paperを書く場合は、結果artifactと対応するclaimだけを書く。

## Out Of Scope

- 次に試す研究計画を `next-plan.md` として作ること。これは `result-interpreter` が担う。
- 複数candidateから次に実行するものを選ぶこと。これは `search/` が担う。
- paper品質のreview。これは `paper-reviewer` が担う。

## Done Criteria

- 実験の再実行方法が分かる。
- `results.md` と `scores.json` がある。
- 成功、失敗、未実行が区別されている。
- paperのclaimがartifactなしに増えていない。
- `next-plan.md` を勝手に更新していない。
