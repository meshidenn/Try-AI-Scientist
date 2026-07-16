# Artifact Audit

## Verdict

PASS

## Checked Artifacts

- `spec.yaml`
- `README.md`
- `workspace/build_real_datasets.py`
- `workspace/quantize_nvfp4.py`
- `workspace/evaluate_nll.py`
- `workspace/evaluate_tasks.py`
- `artifacts/calibration/manifest.json`
- `artifacts/evaluation/manifest.json`
- `results/eval_nll.json`
- `results/eval_tasks.json`
- `results/results.md`
- `results/scores.json`
- `logs/build_real_datasets.json`
- `logs/quantize_general_chat.json`
- `logs/quantize_code.json`
- `logs/quantize_math_reasoning.json`
- `logs/eval_nll_base.json`
- `logs/eval_nll_nvfp4_real_general_chat.json`
- `logs/eval_nll_nvfp4_real_code.json`
- `logs/eval_nll_nvfp4_real_math_reasoning.json`
- `logs/eval_tasks_base.json`
- `logs/eval_tasks_nvfp4_real_general_chat.json`
- `logs/eval_tasks_nvfp4_real_code.json`
- `logs/eval_tasks_nvfp4_real_math_reasoning.json`

## Blocking Issues

None.

## Warnings For Interpretation

- NLL evaluation uses only 12 examples per domain.
- Task pilot uses only 4 GSM8K and 4 MBPP samples per model.
- An initial 8-sample task run with longer generation was manually interrupted because Transformers/compressed-tensors NVFP4 A4 generation made the accuracy evaluation impractically slow; only the completed 4-sample run is reported as a result.
- Some UltraChat examples were truncated to `max_length=768`, as shown by repeated 768-token counts in `results/eval_nll.json`.
- MBPP pass@1 uses restricted local assert execution; it is useful for a smoke check but should not be treated as a full MBPP benchmark harness.
- Model checkpoints are intentionally under `artifacts/models/` and ignored by git.

## Notes

The result files and logs agree that dataset generation, three quantization runs, four-model NLL evaluation, and four-model task smoke evaluation completed successfully.
