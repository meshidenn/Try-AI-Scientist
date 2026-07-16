# exp-004

## Purpose

Compare whether NVFP4 W4A4 calibration language changes quantization degradation for Japanese and English instruction text.

This experiment is an accuracy experiment. vLLM is not a speed metric target here; it is only a possible execution backend if generation-based accuracy evaluation becomes impractically slow through Transformers/compressed-tensors.

## Scope

- Model: `Qwen/Qwen3-4B-Instruct-2507`
- Quantization: LLM Compressor `oneshot` with `QuantizationModifier(targets="Linear", scheme="NVFP4", ignore=["lm_head"])`
- Calibration languages: `english_instruction`, `japanese_instruction`, `bilingual_mixed`
- Calibration samples: 64 per language condition
- NLL evaluation samples: 24 per evaluation language
- Evaluation languages: English instruction text and Japanese instruction text

## Commands

```bash
uv run python projects/quantization-calibration-data/experiments/exp-004/workspace/build_language_datasets.py --num-calibration-samples 64 --num-eval-samples 24
uv run python projects/quantization-calibration-data/experiments/exp-004/workspace/quantize_nvfp4.py --language english_instruction
uv run python projects/quantization-calibration-data/experiments/exp-004/workspace/quantize_nvfp4.py --language japanese_instruction
uv run python projects/quantization-calibration-data/experiments/exp-004/workspace/quantize_nvfp4.py --language bilingual_mixed
uv run python projects/quantization-calibration-data/experiments/exp-004/workspace/evaluate_nll.py --max-samples 24 --max-length 768
```

## Notes

Dataset resolution is logged because Japanese instruction dataset availability can vary. If the primary Japanese Dolly-style dataset is unavailable, the builder tries the configured fallback candidates and records all load errors.
