# Next Plan

## Priority 1: Increase Evaluation Size

Scale English and Japanese evaluation from 24 examples to at least 100 examples while reusing the existing checkpoints.

## Priority 2: Make Language Evaluation More Parallel

Use paired English/Japanese translation or instruction data if available, so language is isolated more cleanly from content differences.

## Priority 3: Increase Calibration Samples

Repeat quantization with 128 or 256 calibration samples per language condition.

## Priority 4: Add Generation Accuracy Carefully

Add Japanese and English generation metrics only after NLL is stable. If Transformers/compressed-tensors generation becomes impractically slow, use vLLM as an accuracy-evaluation backend.
