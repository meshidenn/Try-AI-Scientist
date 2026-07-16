# Result Interpretation

## Summary

`exp-005` completed the LLM-jp Japanese-data NLL comparison for NVFP4 W4A4 calibration language. The Japanese data source was changed to `llm-jp/llm-jp-instructions` and evaluation was increased to 100 samples per language.

## Main Findings

- All quantized variants degraded relative to base on both English and Japanese evaluation text.
- Japanese evaluation: matched LLM-jp Japanese calibration was best among quantized variants with mean NLL 2.3624 and delta NLL 0.0235.
- English evaluation: bilingual mixed calibration was slightly best among quantized variants with mean NLL 2.3367 and delta NLL 0.0637.
- The English gap between bilingual mixed and English-only calibration is small: 0.0023 NLL.

## Comparison To exp-004

`exp-004` used a previous Japanese dataset and found bilingual mixed best on Japanese NLL in a 24-sample pilot. `exp-005` uses LLM-jp Japanese data and 100 samples, and the Japanese result changes to matched-Japanese-best. This suggests the Japanese dataset choice matters for calibration-data conclusions.

## Limits

This result does not directly measure instruction-following correctness, translation quality, code accuracy, or math reasoning. It measures token-level likelihood degradation on held-out instruction text.
