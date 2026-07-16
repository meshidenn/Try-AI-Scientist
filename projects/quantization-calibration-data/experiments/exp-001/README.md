# exp-001

## Purpose

`sklearn` の digits 分類でFP32のMLPを学習し、学習済み重みを固定したまま、calibration data の違いだけを変えて simulated post-training quantization を行う。

## Reproduction

```bash
uv run python projects/quantization-calibration-data/experiments/exp-001/workspace/run_experiment.py
```

## Outputs

- `results/results.md`
- `results/scores.json`
- `logs/run.log`

No paper draft is produced for this first run.
