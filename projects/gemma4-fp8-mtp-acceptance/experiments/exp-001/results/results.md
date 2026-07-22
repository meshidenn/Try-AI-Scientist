# Results

## Summary

Status: completed for the current baseline and follow-up sweeps.

The initial hypothesis was partially supported: FP8 target runs can lower MTP acceptance rate, but the measured random benchmark conditions do not show a stable FP8 throughput slowdown. The clearest slowdown so far is `in1024/out1024/spec_tokens=4/concurrency=2`, where FP8 output throughput was 67.24 tok/s vs BF16 67.90 tok/s while acceptance dropped from 51.82% to 29.83%. At higher concurrency, FP8 recovered and became faster than BF16.

## Setup

- Target baseline: `google/gemma-4-26B-A4B-it`
- FP8 target: `RedHatAI/gemma-4-26B-A4B-it-FP8-Dynamic`
- Assistant drafter: `google/gemma-4-26B-A4B-it-assistant`
- Serving stack: `vllm/vllm-openai:v0.24.0`

## Metrics

- Primary: output throughput in tokens/s.
- Secondary: request throughput, total token throughput, TTFT, TPOT, E2E
  latency, and speculative acceptance metrics if exposed by vLLM logs or
  metrics endpoint.

## Main Results

Measured results are summarized below and in `review/final-report.md`. Raw benchmark JSON files are stored under this `results/` directory.

## Figures

No figures generated yet.

## Failures And Negative Results

The original concern, a broad FP8 + MTP slowdown, was not reproduced across most random benchmark settings. A small throughput slowdown was reproduced only for `in1024/out1024/spec_tokens=4/concurrency=2`.

## Reproduction

```bash
bash projects/gemma4-fp8-mtp-acceptance/experiments/exp-001/workspace/run_baseline.sh
```

## Notes For Reviewer

The assistant drafter was selected from the official Gemma 4 26B assistant
model card.

## Additional Runs 2026-07-05

Changed conditions from the first baseline by increasing output length to 512 and then increasing max concurrency to 4. All runs used `vllm/vllm-openai:v0.24.0`, MTP method, and `num_speculative_tokens=4`.

| Variant | input | output | concurrency | prompts | output tok/s | total tok/s | mean TTFT ms | mean TPOT ms | mean ITL ms | acceptance rate | acceptance length |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BF16 + MTP | 128 | 512 | 1 | 6 | 59.01 | 73.76 | 233.67 | 16.52 | 67.99 | 78.26% | 4.13 |
| FP8 Dynamic + MTP | 128 | 512 | 1 | 6 | 92.77 | 115.97 | 141.70 | 10.52 | 44.31 | 80.63% | 4.23 |
| BF16 + MTP | 128 | 512 | 4 | 12 | 160.21 | 200.26 | 399.68 | 21.61 | 91.40 | 81.14% | 4.25 |
| FP8 Dynamic + MTP | 128 | 512 | 4 | 12 | 220.91 | 276.14 | 244.31 | 15.91 | 64.60 | 76.82% | 4.07 |

Interpretation guard: these changed conditions still did not reproduce an FP8 throughput slowdown. The concurrency-4 run did show lower FP8 acceptance rate than BF16, but FP8 output throughput remained higher.

Raw files:

- `bf16_out512_s4.benchmark.json`
- `fp8_out512_s4.benchmark.json`
- `bf16_out512_s4_c4.benchmark.json`
- `fp8_out512_s4_c4.benchmark.json`

## Spec Depth And Long IO Runs 2026-07-05

This run varied `num_speculative_tokens` and added a longer input-output pattern. All runs used `vllm/vllm-openai:v0.24.0`, Gemma 4 MTP method, max concurrency 1, random dataset, `temperature=0`, and `ignore_eos=true`.

### in128 / out512 / concurrency1

| Variant | spec tokens | prompts | output tok/s | total tok/s | mean TTFT ms | mean TPOT ms | mean ITL ms | acceptance rate | acceptance length |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BF16 + MTP | 1 | 6 | 44.44 | 55.55 | 162.41 | 22.23 | 43.88 | 97.55% | 1.98 |
| FP8 Dynamic + MTP | 1 | 6 | 59.83 | 74.79 | 90.74 | 16.57 | 31.55 | 90.75% | 1.91 |
| BF16 + MTP | 2 | 6 | 57.22 | 71.53 | 225.33 | 17.07 | 48.63 | 92.75% | 2.86 |
| FP8 Dynamic + MTP | 2 | 6 | 63.52 | 79.39 | 102.64 | 15.57 | 39.66 | 77.62% | 2.55 |
| BF16 + MTP | 4 | 6 | 59.01 | 73.76 | 233.67 | 16.52 | 67.99 | 78.26% | 4.13 |
| FP8 Dynamic + MTP | 4 | 6 | 92.77 | 115.97 | 141.70 | 10.52 | 44.31 | 80.63% | 4.23 |

### in1024 / out1024 / concurrency1

| Variant | spec tokens | prompts | output tok/s | total tok/s | mean TTFT ms | mean TPOT ms | mean ITL ms | acceptance rate | acceptance length |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BF16 + MTP | 1 | 3 | 39.97 | 79.94 | 409.73 | 24.64 | 48.76 | 97.87% | 1.98 |
| FP8 Dynamic + MTP | 1 | 3 | 54.49 | 108.99 | 186.64 | 18.19 | 33.70 | 85.39% | 1.85 |

### Interpretation Guard

- The expected FP8 throughput slowdown was still not reproduced.
- FP8 acceptance degradation was reproduced clearly for `spec_tokens=1`, `spec_tokens=2`, and long in/out at `spec_tokens=1`.
- On `in128/out512`, BF16 throughput peaked around spec 4 in this small run, while FP8 throughput also peaked at spec 4 despite lower acceptance in some settings.
- On the long `in1024/out1024` pattern with spec 1, FP8 remained faster but had a substantially lower acceptance rate than BF16.

Raw files added:

- `bf16_s1_in128_out512.benchmark.json`
- `fp8_s1_in128_out512.benchmark.json`
- `bf16_s2_in128_out512.benchmark.json`
- `fp8_s2_in128_out512.benchmark.json`
- `bf16_s1_in1024_out1024.benchmark.json`
- `fp8_s1_in1024_out1024.benchmark.json`

## Longer IO Spec4 Runs 2026-07-05

This run used `num_speculative_tokens=4` and pushed input/output lengths closer to `max_model_len=4096`. All runs used `vllm/vllm-openai:v0.24.0`, random dataset, `temperature=0`, and `ignore_eos=true`.

| Variant | input | output | concurrency | prompts | output tok/s | total tok/s | mean TTFT ms | mean TPOT ms | mean ITL ms | acceptance rate | acceptance length |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BF16 + MTP | 1024 | 2048 | 1 | 2 | 32.04 | 48.06 | 310.72 | 31.08 | 69.18 | 30.66% | 2.23 |
| FP8 Dynamic + MTP | 1024 | 2048 | 1 | 2 | 49.27 | 73.90 | 221.99 | 20.20 | 48.33 | 34.88% | 2.40 |
| BF16 + MTP | 2048 | 1024 | 1 | 2 | 43.30 | 129.91 | 330.28 | 22.79 | 67.58 | 49.17% | 2.97 |
| FP8 Dynamic + MTP | 2048 | 1024 | 1 | 2 | 69.64 | 208.92 | 211.94 | 14.17 | 47.13 | 58.37% | 3.33 |
| BF16 + MTP | 2048 | 1536 | 1 | 2 | 28.05 | 65.45 | 177.10 | 35.56 | 70.57 | 24.63% | 1.99 |
| FP8 Dynamic + MTP | 2048 | 1536 | 1 | 2 | 30.97 | 72.26 | 104.79 | 32.25 | 49.95 | 13.77% | 1.55 |
| BF16 + MTP | 1024 | 1024 | 2 | 4 | 67.90 | 135.79 | 1203.82 | 26.36 | 80.85 | 51.82% | 3.07 |
| FP8 Dynamic + MTP | 1024 | 1024 | 2 | 4 | 67.24 | 134.49 | 1371.05 | 26.51 | 58.01 | 29.83% | 2.19 |

### Interpretation Guard

- Longer IO substantially reduced MTP acceptance for both BF16 and FP8 at `spec_tokens=4`.
- The clearest FP8 acceptance collapse so far is `in2048/out1536/spec4`: FP8 acceptance 13.77% vs BF16 24.63%.
- The first throughput non-win for FP8 appeared at `in1024/out1024/concurrency2/spec4`: FP8 output throughput 67.24 tok/s vs BF16 67.90 tok/s. This is a small slowdown, but it is finally directionally consistent with the original concern.
- In the other long single-concurrency cases, FP8 remained faster despite low acceptance.

Raw files added:

- `bf16_s4_in1024_out2048.benchmark.json`
- `fp8_s4_in1024_out2048.benchmark.json`
- `bf16_s4_in2048_out1024.benchmark.json`
- `fp8_s4_in2048_out1024.benchmark.json`
- `bf16_s4_in2048_out1536.benchmark.json`
- `fp8_s4_in2048_out1536.benchmark.json`
- `bf16_s4_in1024_out1024_c2.benchmark.json`
- `fp8_s4_in1024_out1024_c2.benchmark.json`

## Higher Concurrency Spec4 Runs 2026-07-06

This run extended the `in1024/out1024/spec_tokens=4` condition from concurrency 2 to concurrency 4 and 8. All runs used `vllm/vllm-openai:v0.24.0`, random dataset, `temperature=0`, and `ignore_eos=true`.

| Variant | input | output | concurrency | prompts | output tok/s | total tok/s | mean TTFT ms | mean TPOT ms | mean ITL ms | acceptance rate | acceptance length |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BF16 + MTP | 1024 | 1024 | 2 | 4 | 67.90 | 135.79 | 1203.82 | 26.36 | 80.85 | 51.82% | 3.07 |
| FP8 Dynamic + MTP | 1024 | 1024 | 2 | 4 | 67.24 | 134.49 | 1371.05 | 26.51 | 58.01 | 29.83% | 2.19 |
| BF16 + MTP | 1024 | 1024 | 4 | 8 | 103.04 | 206.09 | 1420.22 | 33.30 | 109.99 | 57.70% | 3.31 |
| FP8 Dynamic + MTP | 1024 | 1024 | 4 | 8 | 178.05 | 356.10 | 1513.47 | 18.03 | 64.17 | 64.07% | 3.56 |
| BF16 + MTP | 1024 | 1024 | 8 | 16 | 136.92 | 273.83 | 602.75 | 43.51 | 128.17 | 48.73% | 2.95 |
| FP8 Dynamic + MTP | 1024 | 1024 | 8 | 16 | 192.01 | 384.03 | 353.89 | 25.99 | 78.92 | 51.09% | 3.04 |

### Interpretation Guard

- The `concurrency=2` condition reproduced a small FP8 throughput slowdown with a large acceptance drop.
- Increasing concurrency did not preserve that slowdown. At `concurrency=4`, FP8 output throughput was 1.73x BF16; at `concurrency=8`, FP8 output throughput was 1.40x BF16.
- FP8 acceptance also recovered at higher concurrency in this run, so the low-acceptance/low-throughput behavior is not stable across concurrency for this random benchmark setting.
- The next useful sweep should keep the long `in1024/out1024/spec4` shape but vary request mix, prompt count, and possibly `max_model_len`/memory pressure to determine whether the concurrency-2 slowdown is noise, scheduler-sensitive behavior, or a real low-utilization regime.

Raw files added:

- `bf16_s4_in1024_out1024_c4.benchmark.json`
- `fp8_s4_in1024_out1024_c4.benchmark.json`
- `bf16_s4_in1024_out1024_c8.benchmark.json`
- `fp8_s4_in1024_out1024_c8.benchmark.json`



## High Spec Depth Runs 2026-07-18

既存の全10ユニークworkloadへ`spec_tokens=8,16`を追加した。各runは16 prompts、2 warmups、`ignore_eos=true`で、40/40 benchmarkが`completed=16`, `failed=0`だった。

| input/output/c | BF16 s8 | BF16 s16 | s16/s8 | FP8 s8 | FP8 s16 | s16/s8 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 128/128/1 | 49.68 | 39.44 | 0.79x | 66.67 | 40.19 | 0.60x |
| 128/512/1 | 73.73 | 66.22 | 0.90x | 87.21 | 73.53 | 0.84x |
| 128/512/4 | 104.64 | 201.23 | 1.92x | 270.98 | 200.25 | 0.74x |
| 1024/1024/1 | 37.43 | 30.30 | 0.81x | 66.41 | 62.57 | 0.94x |
| 1024/1024/2 | 84.40 | 40.53 | 0.48x | 90.97 | 59.48 | 0.65x |
| 1024/1024/4 | 80.09 | 102.08 | 1.27x | 136.41 | 96.69 | 0.71x |
| 1024/1024/8 | 201.99 | 160.34 | 0.79x | 145.20 | 131.06 | 0.90x |
| 1024/2048/1 | 69.80 | 34.62 | 0.50x | 70.58 | 51.76 | 0.73x |
| 2048/1024/1 | 52.18 | 38.09 | 0.73x | 47.07 | 35.14 | 0.75x |
| 2048/1536/1 | 55.45 | 37.23 | 0.67x | 53.49 | 37.60 | 0.70x |

単位はoutput tok/s。

### Interpretation Guard

- FP8ではs16がs8より10/10条件で遅く、throughput比は0.60x〜0.94xだった。
- BF16でもs16は8/10条件で遅かった。例外はconcurrency 4の2条件で、scheduler/batching依存が強い。
- s16ではacceptance rateが多くの条件で低下した。たとえばFP8の128/128/c1は45.33%から22.78%、2048/1024/c1は28.48%から17.31%へ低下した。
- FP8対BF16ではs8でも3/10条件、s16でも4/10条件でFP8が遅かった。量子化の利得とacceptance/verification costの優劣はworkloadとconcurrencyで反転する。
- s16は無条件に選ぶべきではなく、今回のFP8 random workloadではs8が一貫して優位だった。

Structured artifacts:

- `results/high_spec_comparison.json`
- `results/scores.json`

Reproduction:

```bash
bash projects/gemma4-fp8-mtp-acceptance/experiments/exp-001/workspace/run_spec8_16_matrix.sh
python3 projects/gemma4-fp8-mtp-acceptance/experiments/exp-001/workspace/summarize_all_results.py
```
