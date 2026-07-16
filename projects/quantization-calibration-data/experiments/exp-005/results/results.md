# Results

## Summary

`exp-005` re-ran the Japanese-vs-English NVFP4 W4A4 calibration-language NLL comparison using `llm-jp/llm-jp-instructions` for Japanese calibration/evaluation data.

Completed stages:

1. Built English, LLM-jp Japanese, and bilingual mixed calibration JSONL files.
2. Quantized three NVFP4 W4A4 variants using 64 calibration samples per condition.
3. Evaluated base and all three quantized variants with held-out NLL on 100 English and 100 Japanese instruction texts.

Main result: all quantized variants have higher NLL than the base model on both English and Japanese evaluation text. Within quantized variants, bilingual mixed calibration is slightly best on English evaluation, while LLM-jp Japanese calibration is best on Japanese evaluation.

This is an accuracy experiment, not a speed benchmark. vLLM was not used because the NLL evaluation completed through the Transformers/compressed-tensors path.

## Setup

- Base model: `Qwen/Qwen3-4B-Instruct-2507`.
- Quantization: LLM Compressor `oneshot` with `QuantizationModifier(targets="Linear", scheme="NVFP4", ignore=["lm_head"])`.
- Calibration samples: 64 per condition.
- Evaluation samples: 100 per language.
- Evaluation max length: 768.
- Metric: mean next-token negative log likelihood (NLL), lower is better.

## Datasets

| language condition | dataset / construction | split | calibration samples | evaluation samples |
| --- | --- | --- | ---: | ---: |
| `english_instruction` | `databricks/databricks-dolly-15k` | `train` | 64 | 100 |
| `japanese_instruction` | `llm-jp/llm-jp-instructions`, config `v1.0`, parquet converted shard | `train` | 64 | 100 |
| `bilingual_mixed` | first 32 English + first 32 LLM-jp Japanese calibration rows | n/a | 64 | 0 |

Japanese rows are loaded from the converted parquet shard because the normal `datasets.load_dataset("llm-jp/llm-jp-instructions", data_dir="v1.0")` path exposed a split-name mismatch in this environment. The artifact manifest records the exact parquet URL.

## Metrics

NLL is token-weighted mean next-token negative log likelihood over held-out instruction texts. Perplexity is `exp(NLL)`. Delta NLL is measured against the base model on the same evaluation language.

## Main Results

NLL / perplexity / delta NLL vs base:

| model | English eval | Japanese eval |
| --- | ---: | ---: |
| `base` | 2.2731 / 9.7093 / 0.0000 | 2.3389 / 10.3697 / 0.0000 |
| `nvfp4_lang_english_instruction` | 2.3390 / 10.3712 / 0.0659 | 2.3740 / 10.7408 / 0.0352 |
| `nvfp4_lang_japanese_instruction` | 2.3511 / 10.4968 / 0.0780 | 2.3624 / 10.6167 / 0.0235 |
| `nvfp4_lang_bilingual_mixed` | 2.3367 / 10.3476 / 0.0637 | 2.3719 / 10.7176 / 0.0330 |

Best quantized variant by evaluation language:

| evaluation_language | best_quantized_model | mean_nll | delta_nll_vs_base | note |
| --- | --- | ---: | ---: | --- |
| `english_instruction` | `nvfp4_lang_bilingual_mixed` | 2.3367 | 0.0637 | bilingual mixed is slightly best |
| `japanese_instruction` | `nvfp4_lang_japanese_instruction` | 2.3624 | 0.0235 | matched LLM-jp Japanese calibration wins |

## Interpretation

- All NVFP4 W4A4 variants degrade relative to base on both languages.
- On LLM-jp Japanese evaluation text, Japanese calibration is best among quantized variants: delta NLL is 0.0235, compared with 0.0352 for English calibration and 0.0330 for bilingual mixed calibration.
- On English evaluation text, bilingual mixed is slightly best: delta NLL is 0.0637, compared with 0.0659 for English calibration. The gap is small.
- Compared with `exp-004`, replacing the Japanese dataset with LLM-jp data changes the Japanese-language conclusion from mixed-best to matched-Japanese-best.

## Figures

No figures were generated.

## Failures And Negative Results

- No quantized variant beat the base model on either language.
- English matched-language calibration was not the best English quantized variant in this run, although the gap to bilingual mixed was only 0.0023 NLL.
- This is still an NLL-only evaluation; generation-based downstream task accuracy was not run.

## Reproduction

```bash
uv run python projects/quantization-calibration-data/experiments/exp-005/workspace/build_language_datasets.py --num-calibration-samples 64 --num-eval-samples 100
uv run python projects/quantization-calibration-data/experiments/exp-005/workspace/quantize_nvfp4.py --language english_instruction
uv run python projects/quantization-calibration-data/experiments/exp-005/workspace/quantize_nvfp4.py --language japanese_instruction
uv run python projects/quantization-calibration-data/experiments/exp-005/workspace/quantize_nvfp4.py --language bilingual_mixed
uv run python projects/quantization-calibration-data/experiments/exp-005/workspace/evaluate_nll.py --max-samples 100 --max-length 768
```

## Notes For Reviewer

This experiment changes the Japanese data source relative to `exp-004` and increases held-out evaluation samples to 100 per language. It supports only NLL degradation claims, not broad generation-quality or downstream-task accuracy claims.
