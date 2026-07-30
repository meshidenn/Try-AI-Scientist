# Gemma 4 FP8/BF16 Workload Comparison

重複する旧long-IO 9比較をexp-003の16-prompt結果で置き換え、Random 59比較とAgentic 18比較、計77比較をMarkdown表へ統合した詳細版。
数値の正本は既存条件が[統合JSON](integrated-comparison.json)、long-IO factorialが[exp-003 scores.json](../experiments/exp-003/results/scores.json)。

FP8/BF16のoutput throughput差が±5%以内なら「同等」。output token数が一致しないpairは「比較不能」とする。

## Random Workload

全59 pair。input/output/concurrencyを固定し、各表でspec depthによる変化を示す。末尾の3つのlong-IO workloadはexp-003で各16 promptへ統一して再測定した。その他の表はspec depthによってprompt数と実施時期が異なるため、depthをまたぐ絶対throughput比較には注意する。

long-IO factorialでは72/72 runが成功し、FP8 slowdownは36対応cell中1件（-0.8%、判定は同等）のみだった。絶対throughputへのmarginal rangeはBF16でconcurrency 2.713x対spec 1.439x、FP8で2.699x対1.323x。詳細な要因分析は[exp-003結果](../experiments/exp-003/results/results.md)と[要因分析JSON](../experiments/exp-003/results/factorial-analysis.json)を参照。

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
| 4 | 46.36 | 75.17 | 1.62x | 62.14% | 51.60% | 65.75% | 32768/32768 | FP8優位 |
| 8 | 53.89 | 71.19 | 1.32x | 32.12% | 47.77% | 46.95% | 32768/32768 | FP8優位 |
| 16 | 31.91 | 90.17 | 2.83x | 182.55% | 19.10% | 52.89% | 32768/32768 | FP8優位 |

<a id="random-in1024-out2048-c2"></a>
### Random input=1024 output=2048 concurrency=2

| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | 差分 | BF16 accept | FP8 accept | output tokens BF16/FP8 | 判定 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 4 | 90.48 | 125.83 | 1.39x | 39.07% | 64.06% | 68.10% | 32768/32768 | FP8優位 |
| 8 | 82.51 | 81.84 | 0.99x | -0.82% | 48.50% | 28.74% | 32768/32768 | 同等 |
| 16 | 56.57 | 109.66 | 1.94x | 93.84% | 22.27% | 34.99% | 32768/32768 | FP8優位 |

<a id="random-in1024-out2048-c4"></a>
### Random input=1024 output=2048 concurrency=4

| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | 差分 | BF16 accept | FP8 accept | output tokens BF16/FP8 | 判定 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 4 | 113.56 | 161.11 | 1.42x | 41.87% | 51.21% | 51.10% | 32768/32768 | FP8優位 |
| 8 | 96.75 | 160.51 | 1.66x | 65.91% | 37.17% | 49.05% | 32768/32768 | FP8優位 |
| 16 | 90.60 | 107.35 | 1.18x | 18.49% | 36.35% | 19.86% | 32768/32768 | FP8優位 |

<a id="random-in1024-out2048-c8"></a>
### Random input=1024 output=2048 concurrency=8

| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | 差分 | BF16 accept | FP8 accept | output tokens BF16/FP8 | 判定 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 4 | 131.16 | 226.30 | 1.73x | 72.53% | 48.89% | 49.74% | 32768/32768 | FP8優位 |
| 8 | 112.08 | 219.01 | 1.95x | 95.41% | 34.30% | 51.50% | 32768/32768 | FP8優位 |
| 16 | 92.73 | 186.76 | 2.01x | 101.41% | 23.75% | 40.84% | 32768/32768 | FP8優位 |

<a id="random-in2048-out1024-c1"></a>
### Random input=2048 output=1024 concurrency=1

| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | 差分 | BF16 accept | FP8 accept | output tokens BF16/FP8 | 判定 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 4 | 45.64 | 73.49 | 1.61x | 61.00% | 52.81% | 66.31% | 16384/16384 | FP8優位 |
| 8 | 34.62 | 60.15 | 1.74x | 73.76% | 27.15% | 39.75% | 16384/16384 | FP8優位 |
| 16 | 28.85 | 44.18 | 1.53x | 53.15% | 17.80% | 23.13% | 16384/16384 | FP8優位 |

<a id="random-in2048-out1024-c2"></a>
### Random input=2048 output=1024 concurrency=2

| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | 差分 | BF16 accept | FP8 accept | output tokens BF16/FP8 | 判定 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 4 | 66.68 | 94.94 | 1.42x | 42.38% | 44.49% | 47.00% | 16384/16384 | FP8優位 |
| 8 | 82.04 | 93.22 | 1.14x | 13.63% | 44.43% | 34.23% | 16384/16384 | FP8優位 |
| 16 | 45.39 | 76.95 | 1.70x | 69.52% | 16.18% | 23.24% | 16384/16384 | FP8優位 |

<a id="random-in2048-out1024-c4"></a>
### Random input=2048 output=1024 concurrency=4

| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | 差分 | BF16 accept | FP8 accept | output tokens BF16/FP8 | 判定 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 4 | 138.48 | 153.60 | 1.11x | 10.91% | 67.12% | 50.44% | 16384/16384 | FP8優位 |
| 8 | 78.82 | 134.93 | 1.71x | 71.18% | 26.95% | 36.36% | 16384/16384 | FP8優位 |
| 16 | 76.94 | 102.00 | 1.33x | 32.57% | 24.02% | 22.43% | 16384/16384 | FP8優位 |

<a id="random-in2048-out1024-c8"></a>
### Random input=2048 output=1024 concurrency=8

| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | 差分 | BF16 accept | FP8 accept | output tokens BF16/FP8 | 判定 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 4 | 120.04 | 193.20 | 1.61x | 60.94% | 44.88% | 55.06% | 16384/16384 | FP8優位 |
| 8 | 116.42 | 158.25 | 1.36x | 35.93% | 40.81% | 33.25% | 16384/16384 | FP8優位 |
| 16 | 85.74 | 112.02 | 1.31x | 30.64% | 22.67% | 20.01% | 16384/16384 | FP8優位 |

<a id="random-in2048-out1536-c1"></a>
### Random input=2048 output=1536 concurrency=1

| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | 差分 | BF16 accept | FP8 accept | output tokens BF16/FP8 | 判定 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 4 | 46.20 | 56.88 | 1.23x | 23.12% | 52.84% | 44.03% | 24576/24576 | FP8優位 |
| 8 | 34.91 | 55.11 | 1.58x | 57.87% | 26.41% | 34.36% | 24576/24576 | FP8優位 |
| 16 | 45.60 | 46.36 | 1.02x | 1.67% | 31.54% | 24.39% | 24576/24576 | 同等 |

<a id="random-in2048-out1536-c2"></a>
### Random input=2048 output=1536 concurrency=2

| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | 差分 | BF16 accept | FP8 accept | output tokens BF16/FP8 | 判定 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 4 | 70.70 | 82.70 | 1.17x | 16.98% | 47.47% | 36.84% | 24576/24576 | FP8優位 |
| 8 | 77.12 | 87.98 | 1.14x | 14.08% | 41.37% | 31.86% | 24576/24576 | FP8優位 |
| 16 | 50.28 | 76.06 | 1.51x | 51.26% | 18.90% | 22.86% | 24576/24576 | FP8優位 |

<a id="random-in2048-out1536-c4"></a>
### Random input=2048 output=1536 concurrency=4

| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | 差分 | BF16 accept | FP8 accept | output tokens BF16/FP8 | 判定 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 4 | 130.13 | 150.03 | 1.15x | 15.30% | 62.38% | 50.02% | 24576/24576 | FP8優位 |
| 8 | 82.12 | 130.77 | 1.59x | 59.23% | 30.43% | 35.56% | 24576/24576 | FP8優位 |
| 16 | 81.13 | 101.98 | 1.26x | 25.70% | 28.44% | 21.17% | 24576/24576 | FP8優位 |

<a id="random-in2048-out1536-c8"></a>
### Random input=2048 output=1536 concurrency=8

| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | 差分 | BF16 accept | FP8 accept | output tokens BF16/FP8 | 判定 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 4 | 128.56 | 180.08 | 1.40x | 40.07% | 53.02% | 43.68% | 24576/24576 | FP8優位 |
| 8 | 112.70 | 160.13 | 1.42x | 42.09% | 36.69% | 38.11% | 24576/24576 | FP8優位 |
| 16 | 89.83 | 113.77 | 1.27x | 26.65% | 26.54% | 19.61% | 24576/24576 | FP8優位 |

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
- [Controlled long-IO factorial結果](../experiments/exp-003/results/results.md)
- [Controlled long-IO要因分析](../experiments/exp-003/results/factorial-analysis.json)
