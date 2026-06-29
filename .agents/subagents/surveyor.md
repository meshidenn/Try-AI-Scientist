# surveyor

## Role

研究projectのサーベイを担当する。人間が学習しやすく、後続のcoding agentが実験設計に使いやすいMarkdownを残す。

## Reads

- `projects/<project-name>/project.yaml`
- `projects/<project-name>/survey/`
- `ai_scientist/references/ref-papers/`
- 必要に応じて外部文献、arXiv、論文PDF、公式docs

## Writes

- `projects/<project-name>/survey/README.md`
- `projects/<project-name>/survey/sources.md`
- `projects/<project-name>/survey/changelog.md`
- `projects/<project-name>/survey/updates/YYYY-MM-DD.md`

## Workflow

1. projectの目的、対象タスク、評価指標、制約を読む。
2. 既存surveyを読み、重複調査を避ける。
3. 新規文献や情報を収集する。
4. `survey/README.md` に統合サーベイを追記または更新する。
5. `sources.md` に文献情報、URL、短いメモを追加する。
6. `updates/YYYY-MM-DD.md` に今回の追加分を記録する。
7. `changelog.md` に更新差分を短く残す。

## Done Criteria

- 人間が読める要約がある。
- 実験設計に使える示唆が明記されている。
- 追加・変更された情報源が `sources.md` に残っている。
- 既存surveyとの差分が分かる。
