# exp-031: repetition_penalty=1.05によるQwen失敗文書の再抽出

`repetition_penalty=1.05` を追加して失敗文書を再抽出する検証。Qwenサーバーへの接続断により、
最初のチャンクで停止した。

## Reproduction

```bash
uv run python -m category_grounded_agentic_search.interfaces.lightrag_reproduction \
  --root workspace/reproduction-runs/issue-004/runs/run-031 --prepare-inputs --subset-context-count 1 \
  --include-document-id ultradomain-6a7cb621a5218266
uv run python -m category_grounded_agentic_search.interfaces.lightrag_reproduction \
  --root workspace/reproduction-runs/issue-004/runs/run-031 --index-only --extract-json --extract-max-tokens 32768 \
  --repetition-penalty 1.05 --embedding-model hash
```
