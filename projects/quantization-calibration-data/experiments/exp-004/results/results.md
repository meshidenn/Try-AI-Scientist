# Results

## Summary

`exp-004` ran a Japanese-vs-English NVFP4 W4A4 calibration-language pilot for `Qwen/Qwen3-4B-Instruct-2507`.

Completed stages:

1. Built English, Japanese, and bilingual mixed calibration JSONL files.
2. Quantized three NVFP4 W4A4 variants using 64 calibration samples per condition.
3. Evaluated base and all three quantized variants with held-out NLL on English and Japanese instruction text.

Main result: all quantized variants have higher NLL than the base model on both English and Japanese evaluation text. Within the quantized variants, English calibration is best for English evaluation, while bilingual mixed calibration is best for Japanese evaluation in this small pilot.

This is an accuracy experiment, not a speed benchmark. vLLM was not used; the completed metric is NLL through the Transformers/compressed-tensors path.

## Setup

- Base model: `Qwen/Qwen3-4B-Instruct-2507`.
- Quantization: LLM Compressor `oneshot` with `QuantizationModifier(targets="Linear", scheme="NVFP4", ignore=["lm_head"])`.
- Calibration samples: 64 per condition.
- Evaluation samples: 24 per language.
- Evaluation max length: 768.
- Metric: mean next-token negative log likelihood (NLL), lower is better.

## Datasets

| language condition | dataset / construction | split | calibration samples | evaluation samples |
| --- | --- | --- | ---: | ---: |
| `english_instruction` | `databricks/databricks-dolly-15k` | `train` | 64 | 24 |
| `japanese_instruction` | `kunishou/databricks-dolly-15k-ja` | `train` | 64 | 24 |
| `bilingual_mixed` | first 32 English + first 32 Japanese calibration rows | n/a | 64 | 0 |

Evaluation uses held-out rows from the resolved English and Japanese instruction datasets. Bilingual mixed is calibration-only.

## Main Results

NLL / perplexity / delta NLL vs base:

| model | English eval | Japanese eval |
| --- | ---: | ---: |
| `base` | 2.1340 / 8.4490 / 0.0000 | 2.2321 / 9.3197 / 0.0000 |
| `nvfp4_lang_english_instruction` | 2.1893 / 8.9291 / 0.0553 | 2.2649 / 9.6304 / 0.0328 |
| `nvfp4_lang_japanese_instruction` | 2.1943 / 8.9735 / 0.0602 | 2.2596 / 9.5792 / 0.0275 |
| `nvfp4_lang_bilingual_mixed` | 2.2045 / 9.0659 / 0.0705 | 2.2542 / 9.5274 / 0.0220 |

Best quantized variant by evaluation language:

| evaluation_language | best_quantized_model | mean_nll | delta_nll_vs_base | matched_language_won |
| --- | --- | ---: | ---: | --- |
| `english_instruction` | `nvfp4_lang_english_instruction` | 2.1893 | 0.0553 | yes |
| `japanese_instruction` | `nvfp4_lang_bilingual_mixed` | 2.2542 | 0.0220 | no, mixed won |

## Interpretation

- English matched-language calibration gives the lowest quantized NLL on English evaluation text.
- Japanese matched-language calibration improves Japanese evaluation relative to English calibration, but bilingual mixed calibration is slightly better than Japanese-only calibration.
- The mixed-vs-Japanese difference on Japanese evaluation is small: delta NLL is 0.0220 for mixed and 0.0275 for Japanese-only.
- All quantized variants degrade relative to base, so the result is about relative degradation among quantized variants, not absolute improvement.

## Failures And Negative Results

- No quantized variant beat the base model on either language.
- Matched-language calibration was not the best quantized variant for Japanese evaluation.
- The pilot is small: 64 calibration samples per condition and 24 evaluation samples per language.
- Generation-based accuracy metrics were not run.

## Reproduction

```bash
uv run python projects/quantization-calibration-data/experiments/exp-004/workspace/build_language_datasets.py --num-calibration-samples 64 --num-eval-samples 24
uv run python projects/quantization-calibration-data/experiments/exp-004/workspace/quantize_nvfp4.py --language english_instruction
uv run python projects/quantization-calibration-data/experiments/exp-004/workspace/quantize_nvfp4.py --language japanese_instruction
uv run python projects/quantization-calibration-data/experiments/exp-004/workspace/quantize_nvfp4.py --language bilingual_mixed
uv run python projects/quantization-calibration-data/experiments/exp-004/workspace/evaluate_nll.py --max-samples 24 --max-length 768
```

## Notes For Reviewer

This experiment changes calibration language while keeping base model, quantization recipe, sample count, max sequence length, and evaluation sets fixed. It supports only a small NLL pilot claim; it does not support broad Japanese/English generation-quality claims.
