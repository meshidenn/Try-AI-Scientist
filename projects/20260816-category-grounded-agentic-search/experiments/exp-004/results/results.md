# Results

## Summary

extract roleの`max_tokens`を1024へ増やした。indexと4件の`hybrid` queryは完走し、queryのfinish reasonはすべて`stop`だった。extractのtruncationは6/6 callで残ったが、graphには115 entity・24 relationが保存された。

## Setup

- exp-002/003と同じLightRAG revision、UltraDomain入力snapshot、Qwen endpoint、chunking、retrieval設定、hash embeddingを使用した。
- 変更した要因はextract roleの`max_tokens=1024`のみである。

## Metrics

| Metric | Value |
| --- | ---: |
| Indexed document / chunks | 1 / 6 |
| Queries completed | 4 / 4 |
| Query non-`stop` finishes | 0 |
| Extract calls at token limit | 6 / 6 |
| Extracted graph entities / relations | 115 / 24 |
| LLM calls | 14 |
| Total tokens | 35,858 |
| Recorded LLM latency | 145.876 s |

## Main Results

relation数は768 tokenの6件から24件へ増えた。しかしfinish reasonはすべて`length`であり、上限増加だけでextract出力を完了させられてはいない。

## Figures

図は作成していない。

## Failures And Negative Results

- extractのtruncationは6/6 callで継続した。
- 1 documentのsmoke pilotかつ`deterministic-hash-128-v1` embeddingであり、比較性能やrelation-aware retrieval品質は評価していない。

## Reproduction

```bash
uv run python -m category_grounded_agentic_search.interfaces.lightrag_pilot \
  --root experiments/exp-004 --prepare-inputs
uv run python -m category_grounded_agentic_search.interfaces.lightrag_pilot \
  --root experiments/exp-004 --run --extract-max-tokens 1024
```

## Notes For Reviewer

run summary、query結果、LightRAG store、ログを`outputs/`と`logs/`に保存した。1536 token試行と同じ入力・条件で比較できる。
