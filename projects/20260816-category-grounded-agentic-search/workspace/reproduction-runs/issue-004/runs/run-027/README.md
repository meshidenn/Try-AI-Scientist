# exp-027: Qwen JSON抽出の反復警告モードでの再現性検証

反復傾向を失敗条件から診断値へ変更し、Qwenの完了応答をLightRAGへ投入した検証である。

## Setup

- Dataset: UltraDomain revision `aa8a51d523f8fc3c5a0ab90dd16b7f6b9dbb5d0d`
- Extractor: `Qwen/Qwen3.6-35B-A3B-FP8`
- JSON extraction、8,192 output tokens、gleaning 0
- Constraints: entity 30、relation 50、既出recordの再出力禁止
- Validation: `stop`かつ非空のcompletionを必須とし、反復率は警告のみ

## Reproduction

```bash
uv run python -m category_grounded_agentic_search.interfaces.lightrag_reproduction \
  --root workspace/reproduction-runs/issue-004/runs/run-027 --prepare-inputs --subset-context-count 1 \
  --include-document-id ultradomain-c58b4831f2d6fec6
uv run python -m category_grounded_agentic_search.interfaces.lightrag_reproduction \
  --root workspace/reproduction-runs/issue-004/runs/run-027 --index-only --extract-json --extract-max-tokens 8192
```
