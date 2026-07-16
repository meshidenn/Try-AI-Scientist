# Next Plan

1. Run a small downstream generation evaluation for Japanese and English instruction tasks to connect NLL differences to task behavior.
2. Keep `llm-jp/llm-jp-instructions` as the main Japanese instruction source, and optionally compare `llm-jp/magpie-sft-v1.0` as a larger synthetic Japanese calibration source.
3. Increase calibration sample count from 64 to 256 to test whether the matched-language pattern strengthens or weakens.
4. If generation evaluation is too slow through Transformers/compressed-tensors, consider vLLM only as an execution backend fallback, not as a speed benchmark target.
