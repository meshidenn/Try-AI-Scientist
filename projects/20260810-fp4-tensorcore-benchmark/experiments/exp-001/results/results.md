# Results

## Summary

完了したbenchmark resultは6件。数値は各raw JSONと照合できる。

## Setup

vLLM `0.26.0`、NVIDIA GB10、CUDA 13.0。BF16とNVFP4 W4A4を同じserver設定で比較した。

## Metrics

throughputはtokens/s、latencyはms。TTFTはtime to first token、TPOTはtime per output token。vLLM benchの保存JSONにはE2E latency項目がないため、E2Eは集計しない。

## Main Results

| label | concurrency | output tok/s | mean TTFT ms | p99 TTFT ms | mean TPOT ms |
|---|---:|---:|---:|---:|---:|
| gemma4_bf16__latency_short | 1 | 3.679629002956561 | 391.33867499185726 | 411.68104943004437 | 270.8233666297334 |
| gemma4_nvfp4__latency_short | 1 | 7.354649610497015 | 227.20054049932514 | 239.01164015078393 | 135.24800695277938 |
| qwen35_bf16__latency_short | 1 | 21.522755540685964 | 133.3042594997096 | 144.7858537499269 | 45.776925744089176 |
| qwen35_nvfp4__latency_short | 1 | 54.34478061486998 | 93.44381649862044 | 104.05564310960472 | 17.808360307109375 |
| qwen3_moe_bf16__latency_short | 1 | 30.963324911064532 | 173.82498299775762 | 223.02127307972114 | 31.18017361416641 |
| qwen3_moe_nvfp4__latency_short | 1 | 72.9164361088546 | 89.03962299882551 | 103.03269117495802 | 13.11966760628756 |

## Figures

図は未作成。raw JSONから再集計可能。

## Failures And Negative Results

失敗・未実行条件はrun-manifest.jsonと各failure.logを参照する。

## Reproduction

`workspace/quantize_qwen35_nvfp4.py`実行後、`workspace/run_benchmark.py --root experiments/exp-001`を実行する。

## Notes For Reviewer

FP4 Tensor Core利用はserver logのkernel選択で確認し、nvidia-smiのSM使用率だけから命令単位の利用率を推定しない。
