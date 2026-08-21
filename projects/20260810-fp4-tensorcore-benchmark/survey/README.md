# FP4 Tensor Core Benchmark Survey

このprojectでは、Blackwell GPU上のNVFP4 W4A4とBF16のserving性能を比較する。
NVFP4 W4A4はFP4 weightsとFP4 input activationsを使う条件、BF16はFP4経路を使わない対照条件として扱う。

Gemma 4 31B A4BとQwen3-30B-A3BはMoEモデルであり、Qwen3.5-4Bは通常モデルの比較対象とする。
