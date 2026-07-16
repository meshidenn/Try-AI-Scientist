# Result Interpretation

## What Was Learned

`exp-003` successfully moved the calibration-domain experiment from synthetic pilot data to real corpora:

- `general_chat`: UltraChat (`HuggingFaceH4/ultrachat_200k`, `train_sft`)
- `code`: MBPP (`google-research-datasets/mbpp`, `full`, `train`)
- `math_reasoning`: GSM8K (`openai/gsm8k`, `main`)

All three real-calibrated NVFP4 W4A4 variants were produced and evaluated against the same held-out real evaluation files.

The NLL result is negative for the matched-domain hypothesis. Matched calibration did not produce the best quantized variant for any evaluated domain:

| evaluation_domain | best_quantized_model | delta_nll_vs_base |
| --- | --- | ---: |
| `general_chat` | `nvfp4_real_math_reasoning` | +0.0499 |
| `code` | `nvfp4_real_general_chat` | +0.1011 |
| `math_reasoning` | `nvfp4_real_code` | +0.0656 |

All quantized variants were worse than base on all evaluated domains, with delta NLL ranging from 0.0499 to 0.1175.

A small generation task pilot was also completed with 4 samples per task:

| model | GSM8K exact match | MBPP pass@1 |
| --- | ---: | ---: |
| `base` | 1/4 = 0.25 | 4/4 = 1.00 |
| `nvfp4_real_general_chat` | 1/4 = 0.25 | 4/4 = 1.00 |
| `nvfp4_real_code` | 0/4 = 0.00 | 3/4 = 0.75 |
| `nvfp4_real_math_reasoning` | 1/4 = 0.25 | 2/4 = 0.50 |

The task pilot also does not support a matched-domain advantage, but the sample count is too small for a stable task-quality conclusion.

## What Was Not Learned

The task pilot is a smoke check, not a reliable benchmark. It uses only 4 GSM8K and 4 MBPP samples per model, with short generation limits chosen to make Transformers/compressed-tensors NVFP4 A4 accuracy evaluation finish.

Chat quality, translation, long-context behavior, and larger task accuracy were not evaluated.

## Hypothesis Status

Weakly tested and not supported by this real-corpus NLL plus small task-pilot run.

## Research Judgment

The strongest result remains the NLL matrix: all real-calibrated NVFP4 variants degrade relative to base, and matched-domain calibration does not win. The task pilot is useful mainly because it shows that NLL and task outcomes can diverge: `nvfp4_real_code` was best quantized on math NLL but scored 0/4 on GSM8K, while `nvfp4_real_general_chat` tied base on the tiny MBPP pilot.

Next work should scale task evaluation before making task-specific claims.
