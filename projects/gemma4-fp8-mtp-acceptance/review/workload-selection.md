# Gemma 4 FP8/BF16 MTP Workload Selection

## 結論

今回の実測では、target precisionだけでなく、workload、concurrency、`spec_tokens`をセットで選ぶ必要がある。

Random詳細表:
[128/128/c1](workload-comparison.md#random-in128-out128-c1) /
[128/512/c1](workload-comparison.md#random-in128-out512-c1) /
[128/512/c4](workload-comparison.md#random-in128-out512-c4) /
[1024/1024/c1](workload-comparison.md#random-in1024-out1024-c1) / [c2](workload-comparison.md#random-in1024-out1024-c2) / [c4](workload-comparison.md#random-in1024-out1024-c4) / [c8](workload-comparison.md#random-in1024-out1024-c8) /
[1024/2048/c1](workload-comparison.md#random-in1024-out2048-c1) / [2048/1024/c1](workload-comparison.md#random-in2048-out1024-c1) / [2048/1536/c1](workload-comparison.md#random-in2048-out1536-c1)

Agentic [c1](workload-comparison.md#agentic-concurrency-1) / [c2](workload-comparison.md#agentic-concurrency-2) / [c4](workload-comparison.md#agentic-concurrency-4)

- **agentic synthetic workloadではFP8 + s8を第一候補にする。** concurrency 1/2/4のすべてで、測定した全target/spec構成中の最高throughputだった。
- **random workloadでFP8を使う場合、s4が最も安定した。** 同一specのBF16比較で9条件中8条件が5%以上高速、1条件が同等で、BF16優位はなかった。
- **FP8 + s16をdefaultにしない。** randomでは10条件中3条件でBF16が5%以上高速、agentic c1ではFP8がBF16より23.75%遅かった。
- **長いinputや高concurrencyではs8/s16を固定しない。** `in2048/out1024/c1`と`in1024/out1024/c8`でFP8 slowdownが再現している。

## Decision Table

| Workload | Concurrency | 推奨候補 | 実測根拠 | 避ける候補 |
| --- | ---: | --- | --- | --- |
| agentic synthetic、input 1k-5k、output上限512 | 1 | **FP8 + s8** | 96.67 tok/s。BF16最速のs16は91.88 tok/s | FP8 + s16: BF16比-23.75% |
| agentic synthetic、input 1k-5k、output上限512 | 2 | **FP8 + s8** | 167.87 tok/s。BF16最速のs8比+23.42% | FP8 + s16はs8より遅い |
| agentic synthetic、input 1k-5k、output上限512 | 4 | **FP8 + s8** | 333.42 tok/s。BF16最速のs16比+44.65% | FP8 + s16はs8より遅い |
| random、短いinput、c1 | 1 | **FP8 + s4を起点** | in128/out512の低depth sweepでs4が92.77 tok/s、s1は59.83、s2は63.52 | s16の固定採用 |
| random、長いinput、c1 | 1 | **FP8 + s4を優先検証** | in2048/out1024でs4はBF16比+60.83%。s8は-9.78%、s16は-7.75% | FP8 + s8/s16の無検証採用 |
| random、balanced IO、中高concurrency | 4-8 | **FP8 + s4を優先検証** | in1024/out1024のs4はc4で+72.79%、c8で+40.23% | c8のFP8+s8は-28.11%、s16は-18.26% |
| random、balanced IO、低concurrency | 1-2 | **FP8 + s4/s8を比較** | s4 c2はBF16と同等、s8 c1/c2はFP8優位 | 単一runだけでの固定設定 |

「推奨候補」は今回のoutput throughputに基づく。実agentのE2E latency、tool待ち、短い自然終了を含む最終推奨ではない。

## Target Comparison By Spec Depth

random workloadの全32 BF16/FP8 pairを、FP8/BF16の差が±5%以内なら同等として分類した。

| spec tokens | 比較数 | FP8優位 | 同等 | BF16優位 | 読み方 |
| ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 2 | 2 | 0 | 0 | 測定範囲ではFP8優位だが条件数が少ない |
| 2 | 1 | 1 | 0 | 0 | 条件不足 |
| 4 | 9 | 8 | 1 | 0 | 今回のrandomでは最も安定 |
| 8 | 10 | 6 | 2 | 2 | 長いinputとc8でslowdownあり |
| 16 | 10 | 4 | 3 | 3 | workload依存が強くdefault不向き |

spec 1/2/4とspec 8/16ではprompt数と実施時期が異なる。この表は各spec内のBF16対FP8には使えるが、全random条件を横断したdepthランキングとしては使えない。

## Reproduced FP8 Slowdowns

5%以上のFP8 slowdownに限定すると、randomで5条件、agenticで1条件だった。

| Workload | spec | input/output/c | FP8 vs BF16 | acceptance BF16 -> FP8 | 解釈 |
| --- | ---: | --- | ---: | ---: | --- |
| random | 8 | 1024/1024/8 | -28.11% | 58.36% -> 24.92% | acceptance低下と整合 |
| agentic synthetic | 16 | 1k-5k/512/1 | -23.75% | 85.24% -> 47.99% | 過大なdraft depthと低concurrency |
| random | 16 | 1024/1024/8 | -18.26% | 33.91% -> 35.99% | acceptanceでは説明できない |
| random | 8 | 2048/1024/1 | -9.78% | 46.75% -> 28.48% | 長いprefillと低acceptanceの組合せ |
| random | 16 | 2048/1024/1 | -7.75% | 26.77% -> 17.31% | 深いdraftの回収不足 |
| random | 16 | 1024/1024/4 | -5.28% | 29.83% -> 21.74% | 小さめだが閾値外 |

`random/s16/in1024/out1024/c8`ではFP8 acceptanceがBF16より高いにもかかわらず遅い。このため「FP8 slowdownはacceptance低下だけが原因」という説明は支持されない。scheduler/batching、verification kernel、FP8 kernelのshape依存も候補に残る。

## Agentic Matrix

agentic synthetic workloadでは、output token数が一致した16 pair中、FP8は15 pairで5%以上高速だった。唯一のBF16優位はs16/c1である。

| concurrency | BF16最速 | FP8最速 | 全構成での選択 |
| ---: | --- | --- | --- |
| 1 | s16: 91.88 tok/s | s8: 96.67 tok/s | **FP8 + s8** |
| 2 | s8: 136.02 tok/s | s8: 167.87 tok/s | **FP8 + s8** |
| 4 | s16: 230.50 tok/s | s8: 333.42 tok/s | **FP8 + s8** |

`fp8_off/c4`と`fp8_s2/c2`はEOSによりtotal output tokenがBF16と一致しないため、cross-target判断から除外した。

## Operational Recommendation

1. 現時点のagent設定は**FP8 + s8**をdefault候補にする。
2. tool-callなど短い自然終了が多い場合は**s4もA/B測定**する。現在のsynthetic replayは多くが512 tokenを生成しており、短いtool callを忠実には再現していない。
3. batch/random系で長いinput、またはconcurrency 8付近なら**s4から開始**し、s8を採用する前に同じ実traceで比較する。
4. **s16はopt-in**とし、少なくともFP8+s8およびBF16同depthとの両方に勝つことを確認してから使う。
5. production判断ではoutput throughputだけでなく、request E2E、TTFT、tool round trip、JSON retry率を測る。

## Evidence And Limits

- [全50 pairの詳細表](workload-comparison.md)
- [構造化比較JSON](integrated-comparison.json)
- random raw results: `../experiments/exp-001/results/*.benchmark.json`
- agentic raw results: `../experiments/exp-002/results/*.benchmark.json`
- 各条件は原則1 runで分散未推定。±5%以内は同等扱いとした。
- agentic workloadはsynthetic raw completionで、実際のtool API、tool実行待ち、multi-turn arrival timingは再現していない。
- 結論は`vllm/vllm-openai:v0.24.0`と今回のGPU/software stackに限定される。

