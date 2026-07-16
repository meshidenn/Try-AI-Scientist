# exp-003

## Purpose

Run a real-corpus LLM NVFP4 W4A4 calibration-domain sensitivity pilot. This experiment follows `exp-002`, replacing synthetic calibration/evaluation text with real datasets where available.

## Scope

- Model: `Qwen/Qwen3-4B-Instruct-2507`
- Quantization: LLM Compressor `oneshot` with `QuantizationModifier(targets="Linear", scheme="NVFP4", ignore=["lm_head"])`
- Calibration domains: `general_chat`, `code`, `math_reasoning`
- Calibration samples: 64 per domain
- NLL evaluation samples: 12 per domain
- Task pilot samples: 4 GSM8K and 4 MBPP samples per model
- Max quantization sequence length: 2048

## Datasets

| domain | calibration source | evaluation source |
| --- | --- | --- |
| `general_chat` | `HuggingFaceH4/ultrachat_200k` | held-out UltraChat rows |
| `code` | MBPP candidate datasets | held-out MBPP rows |
| `math_reasoning` | `openai/gsm8k`, `main`, train | `openai/gsm8k`, `main`, test |

## Commands

```bash
uv run python projects/quantization-calibration-data/experiments/exp-003/workspace/build_real_datasets.py --num-calibration-samples 64 --num-eval-samples 12
uv run python projects/quantization-calibration-data/experiments/exp-003/workspace/quantize_nvfp4.py --domain general_chat
uv run python projects/quantization-calibration-data/experiments/exp-003/workspace/quantize_nvfp4.py --domain code
uv run python projects/quantization-calibration-data/experiments/exp-003/workspace/quantize_nvfp4.py --domain math_reasoning
uv run python projects/quantization-calibration-data/experiments/exp-003/workspace/evaluate_nll.py --max-samples 12 --max-length 768
uv run python projects/quantization-calibration-data/experiments/exp-003/workspace/evaluate_tasks.py --max-samples 4 --gsm8k-max-new-tokens 64 --mbpp-max-new-tokens 96 --code-timeout-s 2
```

## Notes

Generated model checkpoints live under `artifacts/models/` and are ignored by git. The task pilot is intentionally small; the first 8-sample task attempt was manually interrupted because Transformers/compressed-tensors NVFP4 A4 generation made the accuracy evaluation impractically slow.
