# Gemma 4 FP8/BF16 Workload Comparison

`integrated-comparison.json`の全50比較をMarkdown表へ展開した詳細版。数値の正本は[統合JSON](integrated-comparison.json)。

FP8/BF16のoutput throughput差が±5%以内なら「同等」。output token数が一致しないpairは「比較不能」とする。

## Random Workload

全32 pair。input/output/concurrencyを固定し、各表でspec depthによる変化を示す。spec 1/2/4とspec 8/16はprompt数と実施時期が異なるため、depthをまたぐ絶対throughput比較には注意する。

<a id="random-in128-out128-c1"></a>
### Random input=128 output=128 concurrency=1

| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | 差分 | BF16 accept | FP8 accept | output tokens BF16/FP8 | 判定 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 4 | 51.10 | 66.68 | 1.30x | 30.49% | 64.38% | 55.88% | 1280/1280 | FP8優位 |
| 8 | 49.68 | 66.67 | 1.34x | 34.21% | 47.31% | 45.33% | 同一 | FP8優位 |
| 16 | 39.44 | 40.19 | 1.02x | 1.90% | 30.08% | 22.78% | 同一 | 同等 |

<a id="random-in128-out512-c1"></a>
### Random input=128 output=512 concurrency=1

| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | 差分 | BF16 accept | FP8 accept | output tokens BF16/FP8 | 判定 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | 44.44 | 59.83 | 1.35x | 34.65% | 97.55% | 90.75% | 3072/3072 | FP8優位 |
| 2 | 57.22 | 63.52 | 1.11x | 11.00% | 92.75% | 77.62% | 3072/3072 | FP8優位 |
| 4 | 59.01 | 92.77 | 1.57x | 57.21% | 78.26% | 80.63% | 3072/3072 | FP8優位 |
| 8 | 73.73 | 87.21 | 1.18x | 18.28% | 68.24% | 58.05% | 同一 | FP8優位 |
| 16 | 66.22 | 73.53 | 1.11x | 11.04% | 49.27% | 42.40% | 同一 | FP8優位 |

<a id="random-in128-out512-c4"></a>
### Random input=128 output=512 concurrency=4

| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | 差分 | BF16 accept | FP8 accept | output tokens BF16/FP8 | 判定 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 4 | 160.21 | 220.91 | 1.38x | 37.89% | 81.14% | 76.82% | 6144/6144 | FP8優位 |
| 8 | 104.64 | 270.98 | 2.59x | 158.97% | 49.58% | 76.07% | 同一 | FP8優位 |
| 16 | 201.23 | 200.25 | 1.00x | -0.49% | 61.98% | 48.79% | 同一 | 同等 |

<a id="random-in1024-out1024-c1"></a>
### Random input=1024 output=1024 concurrency=1

| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | 差分 | BF16 accept | FP8 accept | output tokens BF16/FP8 | 判定 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | 39.97 | 54.49 | 1.36x | 36.34% | 97.87% | 85.39% | 3072/3072 | FP8優位 |
| 8 | 37.43 | 66.41 | 1.77x | 77.45% | 29.28% | 43.35% | 同一 | FP8優位 |
| 16 | 30.30 | 62.57 | 2.07x | 106.54% | 19.19% | 35.27% | 同一 | FP8優位 |

<a id="random-in1024-out1024-c2"></a>
### Random input=1024 output=1024 concurrency=2

| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | 差分 | BF16 accept | FP8 accept | output tokens BF16/FP8 | 判定 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 4 | 67.90 | 67.24 | 0.99x | -0.96% | 51.82% | 29.83% | 4096/4096 | 同等 |
| 8 | 84.40 | 90.97 | 1.08x | 7.78% | 49.40% | 35.93% | 同一 | FP8優位 |
| 16 | 40.53 | 59.48 | 1.47x | 46.76% | 15.51% | 18.22% | 同一 | FP8優位 |

<a id="random-in1024-out1024-c4"></a>
### Random input=1024 output=1024 concurrency=4

| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | 差分 | BF16 accept | FP8 accept | output tokens BF16/FP8 | 判定 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 4 | 103.04 | 178.05 | 1.73x | 72.79% | 57.70% | 64.07% | 8192/8192 | FP8優位 |
| 8 | 80.09 | 136.41 | 1.70x | 70.32% | 29.62% | 39.38% | 同一 | FP8優位 |
| 16 | 102.08 | 96.69 | 0.95x | -5.28% | 29.83% | 21.74% | 同一 | BF16優位 |

<a id="random-in1024-out1024-c8"></a>
### Random input=1024 output=1024 concurrency=8

| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | 差分 | BF16 accept | FP8 accept | output tokens BF16/FP8 | 判定 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 4 | 136.92 | 192.01 | 1.40x | 40.24% | 48.73% | 51.09% | 16384/16384 | FP8優位 |
| 8 | 201.99 | 145.20 | 0.72x | -28.11% | 58.36% | 24.92% | 同一 | BF16優位 |
| 16 | 160.34 | 131.06 | 0.82x | -18.26% | 33.91% | 35.99% | 同一 | BF16優位 |

<a id="random-in1024-out2048-c1"></a>
### Random input=1024 output=2048 concurrency=1

| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | 差分 | BF16 accept | FP8 accept | output tokens BF16/FP8 | 判定 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 4 | 32.04 | 49.27 | 1.54x | 53.77% | 30.66% | 34.88% | 4096/4096 | FP8優位 |
| 8 | 69.80 | 70.58 | 1.01x | 1.12% | 61.75% | 46.64% | 同一 | 同等 |
| 16 | 34.62 | 51.76 | 1.50x | 49.51% | 22.42% | 28.10% | 同一 | FP8優位 |

<a id="random-in2048-out1024-c1"></a>
### Random input=2048 output=1024 concurrency=1

| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | 差分 | BF16 accept | FP8 accept | output tokens BF16/FP8 | 判定 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 4 | 43.30 | 69.64 | 1.61x | 60.82% | 49.17% | 58.37% | 2048/2048 | FP8優位 |
| 8 | 52.18 | 47.07 | 0.90x | -9.78% | 46.75% | 28.48% | 同一 | BF16優位 |
| 16 | 38.09 | 35.14 | 0.92x | -7.75% | 26.77% | 17.31% | 同一 | BF16優位 |

<a id="random-in2048-out1536-c1"></a>
### Random input=2048 output=1536 concurrency=1

| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | 差分 | BF16 accept | FP8 accept | output tokens BF16/FP8 | 判定 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 4 | 28.05 | 30.97 | 1.10x | 10.40% | 24.63% | 13.77% | 3072/3072 | FP8優位 |
| 8 | 55.45 | 53.49 | 0.96x | -3.53% | 49.57% | 33.36% | 同一 | 同等 |
| 16 | 37.23 | 37.60 | 1.01x | 1.01% | 25.40% | 19.03% | 同一 | 同等 |

## Agentic Synthetic Workload

全18 pair。inputは1,006-4,993 token、output上限は512 token。output token数不一致の2 pairはcross-target判定から除外する。

<a id="agentic-concurrency-1"></a>
### Agentic concurrency=1

| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | 差分 | BF16 accept | FP8 accept | output tokens BF16/FP8 | 比較可能 | 判定 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| off | 23.77 | 39.86 | 1.68x | 67.66% | - | - | 8192/8192 | yes | FP8優位 |
| 1 | 38.74 | 55.90 | 1.44x | 44.30% | 98.45% | 95.79% | 8192/8192 | yes | FP8優位 |
| 2 | 46.93 | 64.84 | 1.38x | 38.18% | 93.82% | 93.82% | 8192/8192 | yes | FP8優位 |
| 4 | 60.90 | 79.60 | 1.31x | 30.70% | 96.46% | 84.62% | 8192/8192 | yes | FP8優位 |
| 8 | 67.17 | 96.67 | 1.44x | 43.92% | 80.62% | 82.90% | 8192/8192 | yes | FP8優位 |
| 16 | 91.88 | 70.05 | 0.76x | -23.75% | 85.24% | 47.99% | 8192/8192 | yes | BF16優位 |

<a id="agentic-concurrency-2"></a>
### Agentic concurrency=2

| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | 差分 | BF16 accept | FP8 accept | output tokens BF16/FP8 | 比較可能 | 判定 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| off | 43.51 | 68.54 | 1.58x | 57.55% | - | - | 8192/8192 | yes | FP8優位 |
| 1 | 61.53 | 88.27 | 1.43x | 43.46% | 98.43% | 95.79% | 8192/8192 | yes | FP8優位 |
| 2 | 76.97 | 136.26 | 1.77x | 77.03% | 94.45% | 93.40% | 8192/4864 | no | 比較不能 |
| 4 | 117.69 | 149.10 | 1.27x | 26.69% | 93.75% | 93.52% | 8192/8192 | yes | FP8優位 |
| 8 | 136.02 | 167.87 | 1.23x | 23.42% | 85.61% | 73.17% | 8192/8192 | yes | FP8優位 |
| 16 | 120.45 | 136.72 | 1.14x | 13.51% | 62.36% | 47.99% | 8192/8192 | yes | FP8優位 |

<a id="agentic-concurrency-4"></a>
### Agentic concurrency=4

| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | 差分 | BF16 accept | FP8 accept | output tokens BF16/FP8 | 比較可能 | 判定 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| off | 84.37 | 71.77 | 0.85x | -14.93% | - | - | 8192/1097 | no | 比較不能 |
| 1 | 106.15 | 199.82 | 1.88x | 88.25% | 96.87% | 98.19% | 8192/8192 | yes | FP8優位 |
| 2 | 102.98 | 174.01 | 1.69x | 68.97% | 92.71% | 88.11% | 8192/8192 | yes | FP8優位 |
| 4 | 223.15 | 252.34 | 1.13x | 13.08% | 92.66% | 80.12% | 8192/8192 | yes | FP8優位 |
| 8 | 229.54 | 333.42 | 1.45x | 45.25% | 79.20% | 78.35% | 8192/8192 | yes | FP8優位 |
| 16 | 230.50 | 291.57 | 1.26x | 26.49% | 73.30% | 56.01% | 8192/8192 | yes | FP8優位 |

## Fields

- `FP8/BF16`: output throughput比。1より大きい場合はFP8が高速。
- `差分`: `(FP8/BF16 - 1) * 100`。
- `accept`: speculative decoding acceptance rate。MTP offでは値なし。
- `output tokens`: BF16/FP8のtotal output token。Random high-specは「同一」。
- `判定`: ±5%以内は同等。output token不一致は比較不能。

## Source Artifacts

- [統合JSON](integrated-comparison.json)
- [Random結果](../experiments/exp-001/results/results.md)
- [Random high-spec比較](../experiments/exp-001/results/high_spec_comparison.json)
- [Agentic結果](../experiments/exp-002/results/results.md)
- [Agentic比較JSON](../experiments/exp-002/results/comparisons.json)
