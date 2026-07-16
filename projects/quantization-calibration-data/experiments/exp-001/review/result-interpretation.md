# Result Interpretation

## What Was Learned

In this toy PTQ setup, calibration data mattered in two different regimes.

For non-pathological calibration datasets, 8-bit quantization was insensitive: all non-blank calibration sets matched the FP32 baseline accuracy of 0.9733. For 4-bit quantization, the non-pathological conditions ranged from 0.9622 to 0.9689 test accuracy, a spread of 0.0067 absolute accuracy.

The pathological `blank_zeros_200` calibration set collapsed both 4-bit and 8-bit accuracy to 0.0978. This is directly explained by its invalid input range: calibration input min and max were both 0.0, and the test input clip rate was 0.5093.

## Hypothesis Status

Partially supported.

The run supports the idea that broken or non-representative calibration ranges can severely damage quantized accuracy. It only weakly supports the idea that realistic calibration data differences matter in this small digits setup, because the non-pathological variants produced small differences and the single representative sample was not the best 4-bit result.

## What Was Not Learned

- Sampling variance across repeated calibration draws was not measured.
- Larger models, real neural-network quantization libraries, and LLM calibration behavior were not tested.
- Weight-only quantization and per-channel quantization were not compared.
- No latency, memory, or model-size metric was measured.

## Research Judgment

The first result is useful as a sanity check and scaffold, but not enough for a strong paper-style claim. The next experiment should estimate variance across calibration samples and include a less toy-like model or task.
