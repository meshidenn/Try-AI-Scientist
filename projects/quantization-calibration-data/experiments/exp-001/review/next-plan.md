# Next Plan

## Priority 1: Repeat Calibration Sampling

Run 20 to 50 random draws for `representative_200`, `small_20`, and smaller sizes such as 5, 10, 50, 100, 500. Report mean, standard deviation, min, and max accuracy for 4-bit and 8-bit.

Expected observation: 4-bit accuracy variance should increase as calibration size decreases.

Metric: mean test accuracy and standard deviation across calibration draws.

## Priority 2: Add Distribution Shift Conditions

Create calibration sets that preserve valid input ranges but shift class distribution or pixel intensity more systematically, such as single-class calibration for each digit and brightness-scaled calibration.

Expected observation: valid but biased calibration should produce smaller degradation than blank calibration, but may become visible at 4-bit.

Metric: test accuracy and input/hidden clip rates.

## Priority 3: Use A Real Quantization Backend

Repeat the same question with a framework quantization path, such as PyTorch static quantization or ONNX Runtime quantization, after adding the dependency through `uv add` if needed.

Expected observation: production quantization details may change the magnitude of calibration sensitivity.

Metric: test accuracy, model size, and inference latency.
