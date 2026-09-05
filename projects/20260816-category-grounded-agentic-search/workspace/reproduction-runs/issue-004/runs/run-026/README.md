# exp-026: Gemma 4 JSON抽出の重複抑止・件数上限・反復検出の統合検証

Qwenで反復生成を検出した1文書をGemma 4へ置換して検証した。

## Setup

- Dataset: UltraDomain revision `aa8a51d523f8fc3c5a0ab90dd16b7f6b9dbb5d0d`
- Extractor: `RedHatAI/gemma-4-26B-A4B-it-FP8-dynamic`
- JSON extraction、8,192 output tokens、gleaning 0
- Constraints: entity 30、relation 50、既出recordの再出力禁止
- Validation: 非空行20行以上かつ一意行率0.5未満を反復生成として失敗扱い

## Reproduction

```bash
uv run python -m category_grounded_agentic_search.interfaces.lightrag_reproduction \
  --root workspace/reproduction-runs/issue-004/runs/run-026 --prepare-inputs --subset-context-count 1 \
  --include-document-id ultradomain-c58b4831f2d6fec6
uv run python -m category_grounded_agentic_search.interfaces.lightrag_reproduction \
  --root workspace/reproduction-runs/issue-004/runs/run-026 --index-only --extract-json --extract-max-tokens 8192
```
