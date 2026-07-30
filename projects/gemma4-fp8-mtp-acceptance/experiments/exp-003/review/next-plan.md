# Next Plan

## Priority 1: Boundary Cell Repeats

次のcellを最低3回、可能なら異なるrandom seedでも反復し、平均・標準偏差・confidence intervalを出す。

- random `input=1024, output=2048, c2, s8`: 今回唯一のFP8低速cell。
- random `input=2048, output=1024, c1, s8/s16`: 旧2-prompt結果と今回結果の符号が反転。
- agentic `c1, s16`: 合成agent workloadで-23.8%を観測した境界。

## Priority 2: Realistic Agent Replay

匿名化した実traceからprompt token列、output長、request間隔、prefix再利用、tool-call/structured outputを保存し、同一requestをBF16/FP8へreplayする。phase別にprefill、decode、tool waitを分離する。

## Priority 3: Adaptive Spec Depth

FP8を固定し、s4をdefaultとしてrolling acceptanceまたはrequest phaseに応じてs8へ上げ、低acceptance時はs1/s2へ下げるpolicyを比較する。固定s4/s8/s16とend-to-end agent latency、output throughput、p95 latencyで評価する。
