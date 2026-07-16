# Claim Audit

## Verdict

PASS

## Checked Claims

- Real calibration/evaluation JSONL files were generated.
- Three real-calibrated NVFP4 W4A4 variants were produced.
- All quantized variants were worse than base on NLL in all evaluated domains.
- Matched-domain calibration did not produce the best quantized NLL in any evaluated domain.
- A 4-sample-per-task GSM8K/MBPP task smoke pilot was run for base and all three NVFP4 variants.
- The small task pilot did not show a matched-domain advantage.

## Unsupported Or Overstated Claims

None found in the updated artifacts.

## Notes

The updated interpretation stays within the measured NLL and small task-pilot evidence. Task results are explicitly labeled as smoke metrics because the task sample count is only 4 per task.
