# Results

## Summary

extract roleの`max_tokens`を2048へ増やした。indexと4件の`hybrid` queryを完走し、extract 6/6 call、keyword 4/4 call、query 4/4 callのfinish reasonがすべて`stop`だった。graphには101 entity・99 relationが保存された。

## Setup

- exp-002からexp-005と同じLightRAG revision、UltraDomain入力snapshot、Qwen endpoint、chunking、retrieval設定、hash embeddingを使用した。
- 変更した要因はextract roleの`max_tokens=2048`のみである。

## Metrics

| Metric | Value |
| --- | ---: |
| Indexed document / chunks | 1 / 6 |
| Queries completed | 4 / 4 |
| Query non-`stop` finishes | 0 |
| Extract calls completed with `stop` | 6 / 6 |
| Extract calls at token limit | 0 / 6 |
| Extracted graph entities / relations | 101 / 99 |
| LLM calls | 14 |
| Prompt / completion / total tokens | 32,508 / 10,309 / 42,817 |
| Recorded LLM latency | 246.893 s |

## Main Results

1536 tokenではextract `stop`が2/6、`length`が4/6だったが、2048 tokenでは6/6が`stop`になった。比較した上限512、768、1024、1536、2048でrelation数は0、6、24、80、99件だった。したがって、この固定したsmoke pilot条件における「全extract callの完走」という停止条件は2048 tokenで初めて満たされた。

## Figures

図は作成していない。

## Failures And Negative Results

- 最初の2048 token runは1 chunkの`stop`後に実行セッションが途切れたため、partial storeを`partial-outputs-interrupted-20260825T0912/`へ退避した。このpartial runは結果の数値に含めない。
- relation数の増加はrelationの正確性、網羅性、またはretrieval品質を評価したものではない。
- 1 documentのsmoke pilotかつ`deterministic-hash-128-v1` embeddingであり、比較性能は評価していない。

## Reproduction

```bash
uv run python -m category_grounded_agentic_search.interfaces.lightrag_pilot \
  --root experiments/exp-006 --prepare-inputs
uv run python -m category_grounded_agentic_search.interfaces.lightrag_pilot \
  --root experiments/exp-006 --run --extract-max-tokens 2048
```

## Notes For Reviewer

成功runのsummary、query結果、LightRAG storeは`outputs/`、ログは`logs/`に保存した。partial runのoutputは別directoryに退避しており、成功runと混同しない。
