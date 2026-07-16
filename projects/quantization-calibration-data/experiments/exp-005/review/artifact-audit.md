# Artifact Audit

## Verdict

PASS

## Checked Artifacts

- `spec.yaml`
- `README.md`
- `workspace/build_language_datasets.py`
- `workspace/quantize_nvfp4.py`
- `workspace/evaluate_nll.py`
- `artifacts/calibration/manifest.json`
- `results/eval_nll.json`
- `results/scores.json`
- `logs/`

## Blocking Issues

None.

## Warnings For Interpretation

- The primary metric is NLL only; do not claim generation-task accuracy.
- Japanese data is loaded through the converted parquet URL because the normal dataset loader path had a split-name mismatch in this environment.
- All quantized variants are worse than base, so conclusions are about relative degradation among quantized variants.

## Notes

Dataset names, split/source information, calibration sample counts, evaluation sample counts, model IDs, and metric direction are recorded in `scores.json` and dataset manifests.
