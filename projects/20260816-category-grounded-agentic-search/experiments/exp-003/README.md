# exp-003: Qwen entity extraction token上限の段階的増加

## Status

Running. exp-002で観測したextract roleのtoken truncationを、他の条件を固定して解消できるか確認する追試である。

## Reproduction

```bash
uv run python -m category_grounded_agentic_search.interfaces.lightrag_pilot \
  --root experiments/exp-003 --prepare-inputs
uv run python -m category_grounded_agentic_search.interfaces.lightrag_pilot \
  --root experiments/exp-003 --run --extract-max-tokens 768
```

次の上限は、前のrunの`outputs/run_summary.json`を確認してから実行する。各試行は別experiment directoryへ保存する。
