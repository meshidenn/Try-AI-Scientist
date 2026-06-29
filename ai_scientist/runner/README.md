# runner

Coding agentの研究jobを起動する層。

最初はローカル実行と自宅サーバー実行を前提にし、後からクラウド実行を追加できる形にする。

MVPでは必ずしもCLIを実装しない。まずはcoding agentが `.agents/subagents/<role>.md` を読み、対象project/experimentのartifactを更新する。将来的にrunnerが `.agents/` の定義と `projects/` の状態を読み、prompt生成、agent起動、ログ保存、再開を自動化する。

想定する責務:

- `project.yaml` と実験 `spec.yaml` を読み込む
- `.agents/subagents/` と `.agents/skills/` の定義を読み込む
- workspaceを初期化する
- coding agentを起動する
- 実行ログとartifactを定期保存する
- timeout後も再開できる状態を残す
