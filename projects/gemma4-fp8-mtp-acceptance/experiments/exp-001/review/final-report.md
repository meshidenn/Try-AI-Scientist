# Gemma 4 FP8 MTP Acceptance Report

## 要約

Gemma 4 26B A4B の original target と FP8 Dynamic target を、同じ official MTP assistant drafter (`google/gemma-4-26B-A4B-it-assistant`) と組み合わせて比較した。実験の主目的は、FP8 target で MTP acceptance rate が下がり、その結果として throughput も下がるかを確認することだった。

結論として、FP8 で acceptance が下がる条件は複数確認できたが、それが常に throughput 低下へ直結するわけではなかった。多くの random benchmark 条件では FP8 target の output throughput は BF16 target を上回った。一方で、`in1024/out1024/spec_tokens=4/concurrency=2` では FP8 が BF16 よりわずかに遅く、かつ acceptance rate が大きく低下した。

## 実験条件

- Serving stack: `vllm/vllm-openai:v0.24.0`
- BF16 target: `google/gemma-4-26B-A4B-it`
- FP8 target: `RedHatAI/gemma-4-26B-A4B-it-FP8-Dynamic`
- MTP assistant drafter: `google/gemma-4-26B-A4B-it-assistant`
- Benchmark dataset: vLLM `random`
- Main metrics: output throughput, total token throughput, TTFT, TPOT, inter-token latency, speculative acceptance rate, acceptance length

## 主要結果

### Baseline

`in128/out128/spec_tokens=4/concurrency=1` では、FP8 は BF16 より acceptance rate が低かったが、output throughput は高かった。

| Variant | output tok/s | acceptance rate | acceptance length |
| --- | ---: | ---: | ---: |
| BF16 + MTP | 51.10 | 64.38% | 3.58 |
| FP8 Dynamic + MTP | 66.68 | 55.88% | 3.24 |

### Spec depth sweep

`in128/out512/concurrency=1` では、`spec_tokens=1` と `spec_tokens=2` で FP8 の acceptance 低下が見えた。それでも output throughput は FP8 が上回った。

| spec tokens | BF16 output tok/s | FP8 output tok/s | BF16 accept | FP8 accept |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 44.44 | 59.83 | 97.55% | 90.75% |
| 2 | 57.22 | 63.52 | 92.75% | 77.62% |
| 4 | 59.01 | 92.77 | 78.26% | 80.63% |

### Long IO

長い input/output では acceptance が BF16 と FP8 の両方で大きく下がった。特に `in2048/out1536/spec_tokens=4` では FP8 acceptance が 13.77% まで下がったが、throughput は FP8 がわずかに上回った。

| Condition | BF16 output tok/s | FP8 output tok/s | BF16 accept | FP8 accept |
| --- | ---: | ---: | ---: | ---: |
| in1024/out2048/c1 | 32.04 | 49.27 | 30.66% | 34.88% |
| in2048/out1024/c1 | 43.30 | 69.64 | 49.17% | 58.37% |
| in2048/out1536/c1 | 28.05 | 30.97 | 24.63% | 13.77% |

### Concurrency sweep

`in1024/out1024/spec_tokens=4` では、`concurrency=2` で FP8 の小さな slowdown が再現した。しかし concurrency を 4 と 8 に上げると slowdown は消え、FP8 が大きく上回った。

| concurrency | BF16 output tok/s | FP8 output tok/s | BF16 accept | FP8 accept |
| ---: | ---: | ---: | ---: | ---: |
| 2 | 67.90 | 67.24 | 51.82% | 29.83% |
| 4 | 103.04 | 178.05 | 57.70% | 64.07% |
| 8 | 136.92 | 192.01 | 48.73% | 51.09% |

## 解釈

今回の random benchmark からは、「FP8 target にすると MTP acceptance が下がり、そのため常に遅くなる」という単純な説明は支持されない。FP8 acceptance 低下は実測されているが、多くの条件では FP8 の decode/prefill 側の利得がそれを上回った。

ただし `concurrency=2` の長め IO では、FP8 acceptance の大きな低下と小さな throughput 低下が同時に起きた。これは、低めの並列度、長めの request、speculative overhead、scheduler 挙動が重なると FP8 + MTP の利得が消える可能性を示している。

職場の agent workload で FP8 が遅かった場合、random benchmark よりも以下の要因を優先して疑うべきである。

1. Tool-call / JSON などの構造化短生成で、MTP の draft token が受理されにくい。
2. Stop sequence や EOS で generation が短く切られ、MTP overhead を回収できない。
3. BF16 target と official assistant drafter の分布は近いが、FP8 target では quantization により target/assistant mismatch が増える。
4. Agent の逐次実行や低 concurrency により、FP8 kernel の throughput 利得が E2E latency に反映されにくい。
5. Throughput ではなく TTFT、tool round trip、scheduler wait、JSON parse/retry を含む E2E latency を見ていた。

なお、長い prompt/prefix そのものは FP8 に不利とは限らない。むしろ prefill が matmul 支配なら FP8 が有利になりやすい。今回疑うべきなのは、長い prefix ではなく、構造化された短い decode、stop 条件、低 concurrency、assistant/target mismatch の組み合わせである。

## 次の検証計画

次は random benchmark ではなく、実際の agent trace に近い workload で replay する。

- MTP off / MTP spec1 / spec2 / spec4 を比較する。
- BF16 target と FP8 target で同じ tool-call prompt を使う。
- JSON/tool-call 生成、通常文章生成、短い final answer を分けて測る。
- `ignore_eos=false` と実際の stop sequence を使い、固定 output length ではなく自然終了の latency を見る。
- Metrics は output throughput だけでなく、request E2E latency、TTFT、TPOT、acceptance rate、failed/retried structured output を記録する。
- 可能なら FP8 target に近い assistant/drafter、または MTP 無効化との比較で assistant/target mismatch の寄与を分離する。

## Artifact

詳細な実測値は `../results/results.md`、raw benchmark JSON は `../results/*.benchmark.json` に保存した。
