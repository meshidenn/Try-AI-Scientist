# Results

## Summary

Status: completed. 72/72 runs succeeded and all 36 BF16/FP8 pairs are available.

FP8 was slower than BF16 in 1/36 cells. The overall geometric-mean FP8/BF16 output-throughput ratio was 1.447x (+44.7%).

## Setup

See [`../spec.yaml`](../spec.yaml). Each cell used 16 measured prompts, 2 warmups, `--ignore-eos`, and vLLM v0.24.0.

## Marginal Effects

Ratios are geometric means of matched FP8/BF16 output throughput. Values below 1 mean FP8 was slower.

### By Spec Tokens

| Spec tokens | FP8/BF16 | Cells |
|---:|---:|---:|
| 4 | 1.391x (+39.1%) | 12 |
| 8 | 1.440x (+44.0%) | 12 |
| 16 | 1.513x (+51.3%) | 12 |

### By Concurrency

| Concurrency | FP8/BF16 | Cells |
|---:|---:|---:|
| 1 | 1.549x (+54.9%) | 9 |
| 2 | 1.349x (+34.9%) | 9 |
| 4 | 1.363x (+36.3%) | 9 |
| 8 | 1.541x (+54.1%) | 9 |

### Factor Range

| Factor | Max/min marginal FP8/BF16 ratio |
|---|---:|
| Spec tokens | 1.088x |
| Concurrency | 1.148x |

The larger max/min range is the stronger marginal modifier of the FP8/BF16 ratio in this matrix. This is descriptive, not a variance-aware significance test.

### Absolute Output Throughput

These ranges describe absolute throughput within each precision. Concurrency and spec-token levels are each averaged geometrically over the other matrix dimensions.

| Precision | Spec-token range | Concurrency range | Stronger absolute factor |
|---|---:|---:|---|
| BF16 | 1.439x | 2.713x | concurrency |
| FP8 | 1.323x | 2.699x | concurrency |

## Detailed Matched Results

<a id="random-in1024-out2048"></a>
### Random input=1024, output=2048

| Concurrency | Spec | BF16 out tok/s | FP8 out tok/s | FP8/BF16 | BF16 accept (%) | FP8 accept (%) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 4 | 46.36 | 75.17 | 1.621x (+62.1%) | 51.604 | 65.748 |
| 1 | 8 | 53.89 | 71.19 | 1.321x (+32.1%) | 47.774 | 46.954 |
| 1 | 16 | 31.91 | 90.17 | 2.826x (+182.6%) | 19.097 | 52.888 |
| 2 | 4 | 90.48 | 125.83 | 1.391x (+39.1%) | 64.064 | 68.105 |
| 2 | 8 | 82.51 | 81.84 | 0.992x (-0.8%) | 48.500 | 28.742 |
| 2 | 16 | 56.57 | 109.66 | 1.938x (+93.8%) | 22.274 | 34.994 |
| 4 | 4 | 113.56 | 161.11 | 1.419x (+41.9%) | 51.209 | 51.100 |
| 4 | 8 | 96.75 | 160.51 | 1.659x (+65.9%) | 37.168 | 49.045 |
| 4 | 16 | 90.60 | 107.35 | 1.185x (+18.5%) | 36.350 | 19.861 |
| 8 | 4 | 131.16 | 226.30 | 1.725x (+72.5%) | 48.891 | 49.738 |
| 8 | 8 | 112.08 | 219.01 | 1.954x (+95.4%) | 34.298 | 51.505 |
| 8 | 16 | 92.73 | 186.76 | 2.014x (+101.4%) | 23.751 | 40.836 |

<a id="random-in2048-out1024"></a>
### Random input=2048, output=1024

| Concurrency | Spec | BF16 out tok/s | FP8 out tok/s | FP8/BF16 | BF16 accept (%) | FP8 accept (%) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 4 | 45.64 | 73.49 | 1.610x (+61.0%) | 52.815 | 66.312 |
| 1 | 8 | 34.62 | 60.15 | 1.738x (+73.8%) | 27.153 | 39.750 |
| 1 | 16 | 28.85 | 44.18 | 1.531x (+53.1%) | 17.798 | 23.127 |
| 2 | 4 | 66.68 | 94.94 | 1.424x (+42.4%) | 44.492 | 46.998 |
| 2 | 8 | 82.04 | 93.22 | 1.136x (+13.6%) | 44.426 | 34.235 |
| 2 | 16 | 45.39 | 76.95 | 1.695x (+69.5%) | 16.177 | 23.236 |
| 4 | 4 | 138.48 | 153.60 | 1.109x (+10.9%) | 67.124 | 50.437 |
| 4 | 8 | 78.82 | 134.93 | 1.712x (+71.2%) | 26.955 | 36.357 |
| 4 | 16 | 76.94 | 102.00 | 1.326x (+32.6%) | 24.020 | 22.427 |
| 8 | 4 | 120.04 | 193.20 | 1.609x (+60.9%) | 44.884 | 55.060 |
| 8 | 8 | 116.42 | 158.25 | 1.359x (+35.9%) | 40.806 | 33.249 |
| 8 | 16 | 85.74 | 112.02 | 1.306x (+30.6%) | 22.669 | 20.014 |

<a id="random-in2048-out1536"></a>
### Random input=2048, output=1536

| Concurrency | Spec | BF16 out tok/s | FP8 out tok/s | FP8/BF16 | BF16 accept (%) | FP8 accept (%) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 4 | 46.20 | 56.88 | 1.231x (+23.1%) | 52.836 | 44.031 |
| 1 | 8 | 34.91 | 55.11 | 1.579x (+57.9%) | 26.411 | 34.359 |
| 1 | 16 | 45.60 | 46.36 | 1.017x (+1.7%) | 31.541 | 24.388 |
| 2 | 4 | 70.70 | 82.70 | 1.170x (+17.0%) | 47.475 | 36.842 |
| 2 | 8 | 77.12 | 87.98 | 1.141x (+14.1%) | 41.374 | 31.861 |
| 2 | 16 | 50.28 | 76.06 | 1.513x (+51.3%) | 18.901 | 22.865 |
| 4 | 4 | 130.13 | 150.03 | 1.153x (+15.3%) | 62.376 | 50.021 |
| 4 | 8 | 82.12 | 130.77 | 1.592x (+59.2%) | 30.428 | 35.560 |
| 4 | 16 | 81.13 | 101.98 | 1.257x (+25.7%) | 28.436 | 21.171 |
| 8 | 4 | 128.56 | 180.08 | 1.401x (+40.1%) | 53.023 | 43.678 |
| 8 | 8 | 112.70 | 160.13 | 1.421x (+42.1%) | 36.688 | 38.106 |
| 8 | 16 | 89.83 | 113.77 | 1.266x (+26.6%) | 26.544 | 19.612 |

## Interaction Diagnostic

A two-way additive model was fitted to log(FP8/BF16) within each workload. The residual reports how much a specific spec-token/concurrency pair departs from independent marginal effects.

| Input | Output | Max residual multiplier | Log RMSE |
|---:|---:|---:|---:|
| 1024 | 2048 | 1.402x | 0.1896 |
| 2048 | 1024 | 1.246x | 0.1311 |
| 2048 | 1536 | 1.243x | 0.1161 |

## Artifacts

- Structured results: [`scores.json`](scores.json)
- Factor analysis: [`factorial-analysis.json`](factorial-analysis.json)
- Raw benchmark JSON: `*.benchmark.json` in this directory
- Server and benchmark logs: [`../logs/`](../logs/)

## Limitations

Each matrix cell was run once. The 16 prompts expose within-cell latency variation, but repeated cell-level runs are still required before treating small ratio differences as stable.

## Reproduction

```bash
bash projects/gemma4-fp8-mtp-acceptance/experiments/exp-003/workspace/run_factorial_matrix.sh
uv run python projects/gemma4-fp8-mtp-acceptance/experiments/exp-003/workspace/summarize_results.py
uv run python projects/gemma4-fp8-mtp-acceptance/experiments/exp-003/workspace/analyze_factorial.py
```
