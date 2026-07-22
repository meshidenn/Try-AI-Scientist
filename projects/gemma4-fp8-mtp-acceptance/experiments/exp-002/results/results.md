# Results

## Summary

36/36 run が成功した。agent trace 風 workload では、FP8 target が BF16 target より遅くなる条件を再現した。

最も明確な再現は `spec_tokens=16, concurrency=1` で、BF16 は 91.88 output tok/s、FP8 は 70.05 output tok/sだった。FP8はBF16比で23.75%遅く、acceptance rateも85.24%から47.99%へ低下した。両者のtotal outputは8,192 tokenで同一である。

一方、FP8の最適条件は全concurrencyで`spec_tokens=8`だった。acceptance低下だけでは常に遅くならず、draft depthとconcurrencyの組み合わせが重要である。

## Setup

- Container: `vllm/vllm-openai:v0.24.0`
- BF16 target: `google/gemma-4-26B-A4B-it`
- FP8 target: `RedHatAI/gemma-4-26B-A4B-it-FP8-Dynamic`
- MTP assistant: `google/gemma-4-26B-A4B-it-assistant`
- Matrix: BF16/FP8 x MTP off/1/2/4/8/16 x concurrency 1/2/4
- Requests per run: 16, warmup: 2
- Replay input: 1,006 to 4,993 tokens
- Output limit: 512 tokens, EOS enabled
- GPU memory utilization: 0.78

workloadは長いinstruction、tool schema、tool-call要求、tool result、synthesis historyを含むsynthetic traceである。vLLM imageにcustom loader用のpandasがなかったため、同じpromptをShareGPT JSONへ変換してraw completion endpointへ送った。

## Metrics

Primary metricはoutput throughput (tokens/s)。secondary metricsはTTFT、TPOT、E2E latency、acceptance rate、acceptance length、total output tokens。

## Main Results

### Concurrency 1

| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | BF16 accept | FP8 accept |
| ---: | ---: | ---: | ---: | ---: | ---: |
| off | 23.77 | 39.86 | 1.68x | - | - |
| 1 | 38.74 | 55.90 | 1.44x | 98.45% | 95.79% |
| 2 | 46.93 | 64.84 | 1.38x | 93.82% | 93.82% |
| 4 | 60.90 | 79.60 | 1.31x | 96.46% | 84.62% |
| 8 | 67.17 | 96.67 | 1.44x | 80.62% | 82.90% |
| 16 | 91.88 | 70.05 | 0.76x | 85.24% | 47.99% |

### Best Spec Depth

| target | concurrency 1 | concurrency 2 | concurrency 4 |
| --- | --- | --- | --- |
| BF16 | s16, 91.88 tok/s | s8, 136.02 tok/s | s16, 230.50 tok/s |
| FP8 | s8, 96.67 tok/s | s8, 167.87 tok/s | s8, 333.42 tok/s |

FP8 s16のslowdownはconcurrency 1でのみBF16比として現れた。concurrency 2ではFP8 136.72 vs BF16 120.45 tok/s、concurrency 4ではFP8 291.57 vs BF16 230.50 tok/sだった。

## Figures

なし。

## Failures And Negative Results

- 最初のpreflightはkernel module不整合で停止したが、driver復旧後に全runを完了した。
- vLLM custom dataset loaderはimage内にpandasがなく使用できなかった。package更新は行わず、built-in ShareGPT loaderへ切り替えた。
- `fp8_off_agent_c4` は1,097 token、`fp8_s2_agent_c2` は4,864 tokenでEOS終了し、他条件の8,192 tokenと異なる。この2条件のcross-target throughput比較は公平ではない。
- synthetic traceは実際の職場traceではなく、raw completion promptである。tool-call API自体はreplayしていない。

## Reproduction

```bash
bash projects/gemma4-fp8-mtp-acceptance/experiments/exp-002/workspace/run_agent_replay.sh
python3 projects/gemma4-fp8-mtp-acceptance/experiments/exp-002/workspace/summarize_results.py
python3 projects/gemma4-fp8-mtp-acceptance/experiments/exp-002/workspace/compare_results.py
```

## Notes For Reviewer

数値の正本は`results/scores.json`と`results/comparisons.json`。s16/c1のBF16/FP8比較はtotal output tokenが同一で、直接比較可能である。
