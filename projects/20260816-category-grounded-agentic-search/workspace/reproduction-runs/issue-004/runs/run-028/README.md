# exp-028: Qwen JSON抽出の32,768-token完了性検証

8,192 tokensで未完了となった1文書について、Qwenの抽出出力上限を32,768 tokensへ
拡張して、LightRAGのKG抽出が完了するかを検証した。

## Setup

- Dataset: UltraDomain revision `aa8a51d523f8fc3c5a0ab90dd16b7f6b9dbb5d0d`
- Extractor: `Qwen/Qwen3.6-35B-A3B-FP8`
- JSON extraction、32,768 output tokens、gleaning 0
- Constraints: entity 30、relation 50、既出recordの再出力禁止
- Validation: `stop`かつ非空のcompletionを必須とし、反復率は診断・警告のみ

## Reproduction

```bash
uv run python -m category_grounded_agentic_search.interfaces.lightrag_reproduction \
  --root workspace/reproduction-runs/issue-004/runs/run-028 --prepare-inputs --subset-context-count 1 \
  --include-document-id ultradomain-c58b4831f2d6fec6
uv run python -m category_grounded_agentic_search.interfaces.lightrag_reproduction \
  --root workspace/reproduction-runs/issue-004/runs/run-028 --index-only --extract-json --extract-max-tokens 32768
```
