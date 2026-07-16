# exp-001: Baseline Gemma 4 26B MTP BF16 vs FP8

This experiment measures whether the FP8 Gemma 4 26B target loses speculative
decoding efficiency when paired with the official Gemma 4 26B assistant drafter.

Run:

```bash
bash projects/gemma4-fp8-mtp-acceptance/experiments/exp-001/workspace/run_baseline.sh
```

Outputs are written to `results/` and `logs/`.
