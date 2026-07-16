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
- `artifacts/evaluation/manifest.json`
- `results/eval_nll.json`
- `results/results.md`
- `results/scores.json`
- `logs/build_language_datasets.json`
- `logs/quantize_english_instruction.json`
- `logs/quantize_japanese_instruction.json`
- `logs/quantize_bilingual_mixed.json`
- `logs/eval_nll_base.json`
- `logs/eval_nll_nvfp4_lang_english_instruction.json`
- `logs/eval_nll_nvfp4_lang_japanese_instruction.json`
- `logs/eval_nll_nvfp4_lang_bilingual_mixed.json`

## Blocking Issues

None.

## Warnings For Interpretation

- Evaluation uses only 24 examples per language.
- The English and Japanese datasets are Dolly-style but not perfectly parallel examples.
- Some examples may be truncated to `max_length=768`.
- The metric is NLL only; generation quality was not evaluated.
- vLLM was not used because NLL evaluation completed with Transformers/compressed-tensors.

## Notes

The result files and logs agree that dataset generation, three quantization runs, and four-model NLL evaluation completed successfully.
