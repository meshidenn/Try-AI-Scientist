# exp-032: Qwen再起動後のrepetition_penalty=1.05再抽出

Qwenを再起動後、`repetition_penalty=1.05`と32,768 output tokensで、過去にlength終了した
36チャンク文書を再抽出した。

## Reproduction

```bash
uv run python -m category_grounded_agentic_search.interfaces.lightrag_reproduction \
  --root workspace/reproduction-runs/issue-004/runs/run-032 --prepare-inputs --subset-context-count 1 \
  --include-document-id ultradomain-6a7cb621a5218266
uv run python -m category_grounded_agentic_search.interfaces.lightrag_reproduction \
  --root workspace/reproduction-runs/issue-004/runs/run-032 --index-only --extract-json --extract-max-tokens 32768 \
  --repetition-penalty 1.05 --embedding-model hash
```
