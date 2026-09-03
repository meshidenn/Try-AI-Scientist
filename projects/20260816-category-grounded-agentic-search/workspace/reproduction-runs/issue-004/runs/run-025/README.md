# exp-025: Qwen JSON抽出の重複抑止・件数上限・反復検出の統合検証

既知のlength終了文書 `ultradomain-c58b4831f2d6fec6` を対象に、Qwen JSON抽出の
重複抑止設定を確認した実装検証である。

## Setup

- Dataset: UltraDomain revision `aa8a51d523f8fc3c5a0ab90dd16b7f6b9dbb5d0d`
- Extractor: `Qwen/Qwen3.6-35B-A3B-FP8` via `http://192.168.100.11:8000/v1`
- Extraction: JSON、8,192 output tokens、gleaning 0
- Constraints: entity 30、relation 50、既出recordの再出力禁止
- Validation: 非空行20行以上かつ一意行率0.5未満を反復生成として失敗扱い

## Reproduction

```bash
uv run python -m category_grounded_agentic_search.interfaces.lightrag_reproduction \
  --root workspace/reproduction-runs/issue-004/runs/run-025 --prepare-inputs --subset-context-count 1 \
  --include-document-id ultradomain-c58b4831f2d6fec6
uv run python -m category_grounded_agentic_search.interfaces.lightrag_reproduction \
  --root workspace/reproduction-runs/issue-004/runs/run-025 --index-only --extract-json --extract-max-tokens 8192
```

結果は [results/results.md](results/results.md) を参照する。
