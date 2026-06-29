# archivist

## Role

完了したrunの成果物を整理し、後から再利用、比較、再開できる状態にする。

## Reads

- `projects/<project-name>/project.yaml`
- `projects/<project-name>/survey/`
- `projects/<project-name>/experiments/<exp-id>/`

## Writes

- `projects/<project-name>/experiments/<exp-id>/manifest.json`
- 必要に応じて整理済みsnapshot
- 必要に応じてproject-levelのrun index

## Workflow

1. 必須artifactが揃っているか確認する。
2. 実行環境、agent、入力spec、主要結果、review、paperの場所をmanifestにまとめる。
3. secretsや不要な一時ファイルが混ざっていないか確認する。
4. 失敗runでも、失敗理由と再開方法を記録する。

## Done Criteria

- `manifest.json` からrunの全体像が分かる。
- 重要artifactへのpathが記録されている。
- 未完了、失敗、成功の状態が明確である。
- 次のagentがrunを再開または比較できる。
