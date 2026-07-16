# Results

## Summary

FP32 baseline test accuracy: 0.9733.
Best 4-bit calibration: small_20 at 0.9689.
Worst 4-bit calibration: blank_zeros_200 at 0.0978.
Best 8-bit calibration: representative_200 at 0.9733.
Worst 8-bit calibration: blank_zeros_200 at 0.0978.

## Setup

- Dataset: `sklearn.datasets.load_digits`, pixels scaled to `[0, 1]`.
- Split: stratified 75/25 train/test with `random_state=42`.
- Model: `MLPClassifier(hidden_layer_sizes=(64,), random_state=7)`.
- Quantization: simulated PTQ with per-tensor symmetric weight quantization and per-layer affine activation quantization.
- Calibration changes only activation ranges; the trained model and test split are fixed.

## Metrics

- Primary: test accuracy after quantization.
- Secondary: accuracy drop from FP32, test activation clip rates.

## Main Results

| bits | calibration_dataset | n_cal | test_accuracy | drop_from_fp32 | input_clip_rate | hidden_clip_rate |
|---:|---|---:|---:|---:|---:|---:|
| 4 | small_20 | 20 | 0.9689 | 0.0044 | 0.0000 | 0.0021 |
| 4 | high_intensity_200 | 200 | 0.9689 | 0.0044 | 0.0000 | 0.0000 |
| 4 | class0_only | 133 | 0.9667 | 0.0067 | 0.0000 | 0.0003 |
| 4 | low_intensity_200 | 200 | 0.9644 | 0.0089 | 0.0000 | 0.0007 |
| 4 | gaussian_noise_200 | 200 | 0.9644 | 0.0089 | 0.0000 | 0.0009 |
| 4 | representative_200 | 200 | 0.9622 | 0.0111 | 0.0000 | 0.0002 |
| 4 | blank_zeros_200 | 200 | 0.0978 | 0.8756 | 0.5093 | 0.0000 |
| 8 | representative_200 | 200 | 0.9733 | 0.0000 | 0.0000 | 0.0001 |
| 8 | small_20 | 20 | 0.9733 | 0.0000 | 0.0000 | 0.0016 |
| 8 | class0_only | 133 | 0.9733 | 0.0000 | 0.0000 | 0.0002 |
| 8 | low_intensity_200 | 200 | 0.9733 | 0.0000 | 0.0000 | 0.0004 |
| 8 | high_intensity_200 | 200 | 0.9733 | 0.0000 | 0.0000 | 0.0000 |
| 8 | gaussian_noise_200 | 200 | 0.9733 | 0.0000 | 0.0000 | 0.0006 |
| 8 | blank_zeros_200 | 200 | 0.0978 | 0.8756 | 0.5093 | 0.0000 |

## Figures

No figure was generated in this run.

## Failures And Negative Results

- No execution failure occurred.
- 8-bit quantization showed little sensitivity among non-pathological calibration datasets in this toy setup.
- `gaussian_noise_200` is an out-of-distribution calibration baseline; it is not a valid deployment recommendation.
- `blank_zeros_200` is a pathological sanity check; it verifies that broken calibration ranges can collapse accuracy.

## Reproduction

```bash
uv run python projects/quantization-calibration-data/experiments/exp-001/workspace/run_experiment.py
```

## Notes For Reviewer

- This is a small local MVP experiment, not a claim about LLM-scale quantization.
- Calibration ranges are global per layer, so the experiment intentionally isolates a simple and inspectable PTQ mechanism.
