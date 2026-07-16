# Next Plan

## Priority 1: Scale Task Metrics

Increase task evaluation on the existing base and three real-calibrated NVFP4 variants:

- GSM8K exact match from 4 samples to at least 50 samples.
- MBPP pass@1 from 4 samples to at least 50 samples, while keeping restricted execution and timeouts.
- Keep generation lengths short enough to finish, or evaluate only one task per run to avoid long NVFP4 A4 decode time.

## Priority 2: Increase NLL Evaluation Size

Increase held-out NLL evaluation from 12 examples per domain to at least 100 examples per domain. Keep the same quantized checkpoints first, so this isolates evaluation variance from quantization variance.

## Priority 3: Increase Calibration Samples

After task metrics are larger, repeat quantization with 128 or 256 calibration samples per domain. Keep all other settings fixed.

## Priority 4: Add Data-Free Controls

Add data-free LLM Compressor baselines such as FP8 dynamic/block or NVFP4A16 where supported, so the project can compare calibration-sensitive W4A4 against data-free quantization.
