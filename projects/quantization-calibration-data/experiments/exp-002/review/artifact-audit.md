# Artifact Audit

## Verdict

PASS

## Checked Artifacts

- `spec.yaml`
- `README.md`
- `workspace/build_calibration_sets.py`
- `workspace/quantize_nvfp4.py`
- `workspace/build_evaluation_sets.py`
- `workspace/evaluate_nll.py`
- `artifacts/calibration/manifest.json`
- `artifacts/evaluation/manifest.json`
- `results/eval_nll.json`
- `results/results.md`
- `results/scores.json`
- `logs/preflight.json`
- `logs/quantize_general_chat.json`
- `logs/quantize_code.json`
- `logs/quantize_math_reasoning.json`
- `logs/eval_nll_base.json`
- `logs/eval_nll_nvfp4_general_chat.json`
- `logs/eval_nll_nvfp4_code.json`
- `logs/eval_nll_nvfp4_math_reasoning.json`

## Blocking Issues

None.

## Warnings For Interpretation

- Calibration and evaluation datasets are tiny synthetic pilot sets.
- The evaluation metric is NLL/perplexity only, not task accuracy or generation quality.
- The evaluation sets contain reference answers written for this pilot and are not public benchmark splits.
- Matched calibration did not win in this pilot, so claims about matched-domain benefits are unsupported.

## Notes

`results/scores.json` and `results/eval_nll.json` agree on the model/domain NLL matrix. The run should be interpreted as an end-to-end pipeline validation plus weak pilot evidence, not as final scientific evidence.
