# Results

## Summary

extract roleの`max_tokens`を512から768へ増やした。indexと4件の`hybrid` queryは完走し、queryのfinish reasonはすべて`stop`だった。一方、extractは6/6 callで`length`のままであり、truncationは解消しなかった。graphには98 entity・6 relationが保存された。

## Setup

- exp-002と同じLightRAG revision、UltraDomain入力snapshot、Qwen endpoint、chunking、retrieval設定、hash embeddingを使用した。
- 変更した要因はextract roleの`max_tokens=768`のみである。

## Metrics

| Metric | Value |
| --- | ---: |
| Indexed document / chunks | 1 / 6 |
| Queries completed | 4 / 4 |
| Query non-`stop` finishes | 0 |
| Extract calls at token limit | 6 / 6 |
| Extracted graph entities / relations | 98 / 6 |
| LLM calls | 14 |
| Total tokens | 33,067 |
| Recorded LLM latency | 117.060 s |

## Main Results

512 tokenのexp-002ではrelationが0件だったのに対し、768 tokenでは6件を保存した。ただし全extract callが途中終了しているため、このrelation数を完全な抽出結果やretrieval品質の改善とは解釈できない。

## Figures

図は作成していない。

## Failures And Negative Results

- extractのtruncationは6/6 callで継続した。
- 1 documentのsmoke pilotかつ`deterministic-hash-128-v1` embeddingであり、比較性能やrelation-aware retrieval品質は評価していない。

## Reproduction

```bash
uv run python -m category_grounded_agentic_search.interfaces.lightrag_pilot \
  --root experiments/exp-003 --prepare-inputs
uv run python -m category_grounded_agentic_search.interfaces.lightrag_pilot \
  --root experiments/exp-003 --run --extract-max-tokens 768
```

## Notes For Reviewer

run summary、query結果、LightRAG store、ログを`outputs/`と`logs/`に保存した。次の1024 token試行と同じ入力・条件で比較できる。
