# Results

## Summary

extract roleの`max_tokens`を1536へ増やした。indexと4件の`hybrid` queryは完走し、queryのfinish reasonはすべて`stop`だった。extractは2/6 callが`stop`になり、4/6 callで`length`が残った。graphには116 entity・80 relationが保存された。

## Setup

- exp-002/003/004と同じLightRAG revision、UltraDomain入力snapshot、Qwen endpoint、chunking、retrieval設定、hash embeddingを使用した。
- 変更した要因はextract roleの`max_tokens=1536`のみである。

## Metrics

| Metric | Value |
| --- | ---: |
| Indexed document / chunks | 1 / 6 |
| Queries completed | 4 / 4 |
| Query non-`stop` finishes | 0 |
| Extract calls completed with `stop` | 2 / 6 |
| Extract calls at token limit | 4 / 6 |
| Extracted graph entities / relations | 116 / 80 |
| LLM calls | 14 |
| Total tokens | 41,629 |
| Recorded LLM latency | 194.321 s |

## Main Results

512、768、1024、1536 tokenでrelation数は順に0、6、24、80件だった。1536 tokenでは初めて2件のextract callが正常終了したが、4件は上限に達した。したがって、上限増加はgraph artifactを増やしたが、truncationを完全には解消しなかった。

## Figures

図は作成していない。

## Failures And Negative Results

- 1536 tokenでもextractの4/6 callが`length`である。
- relation数の増加はrelationの正確性やretrieval品質を測定したものではない。
- 1 documentのsmoke pilotかつ`deterministic-hash-128-v1` embeddingであり、比較性能は評価していない。

## Reproduction

```bash
uv run python -m category_grounded_agentic_search.interfaces.lightrag_pilot \
  --root experiments/exp-005 --prepare-inputs
uv run python -m category_grounded_agentic_search.interfaces.lightrag_pilot \
  --root experiments/exp-005 --run --extract-max-tokens 1536
```

## Notes For Reviewer

run summary、query結果、LightRAG store、ログを`outputs/`と`logs/`に保存した。主張と次の設計変更は`results/claims.json`、`review/result-interpretation.md`、`review/next-plan.md`で分離した。
