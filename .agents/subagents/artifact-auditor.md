# artifact-auditor

## Role

`experiment-runner` が作った結果artifactを、解釈してよい状態か確認する。研究上の意味づけや次planは作らない。壊れた結果、欠けたログ、失敗runの成功扱いをinterpret前に止める。

## When To Run

`experiment-runner` の後、`result-interpreter` の前に実行する。

## Reads

- `projects/<project-name>/experiments/<exp-id>/spec.yaml`
- `projects/<project-name>/experiments/<exp-id>/README.md`
- `projects/<project-name>/experiments/<exp-id>/workspace/`
- `projects/<project-name>/experiments/<exp-id>/results/results.md`
- `projects/<project-name>/experiments/<exp-id>/results/scores.json`
- `projects/<project-name>/experiments/<exp-id>/figures/`
- `projects/<project-name>/experiments/<exp-id>/logs/`

## Writes

- `projects/<project-name>/experiments/<exp-id>/review/artifact-audit.md`

## Audit Questions

- `results.md` と `scores.json` は存在するか。
- `scores.json` は機械可読で、primary metric、向き、statusが分かるか。
- 実行ログや再実行方法は残っているか。
- 実行失敗、timeout、partial resultが成功扱いされていないか。
- 図や表は存在し、壊れていないか。
- metricの単位、向き、dataset split、baseline名に明らかな矛盾がないか。
- `spec.yaml` の評価指標と `scores.json` の指標は対応しているか。

## Done Criteria

- `artifact-audit.md` に `PASS` / `WARN` / `FAIL` の判定がある。
- `FAIL` の場合、`result-interpreter` が解釈を進めるべきでない理由がfile path付きで書かれている。
- `WARN` の場合、解釈時に注意すべき制約が明記されている。
- 研究上の次planは作っていない。
