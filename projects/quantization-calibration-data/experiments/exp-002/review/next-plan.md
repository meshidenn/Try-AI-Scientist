# Next Plan

## Priority 1: Replace Synthetic Data With Real Corpora

Move from synthetic pilot samples to real calibration/evaluation corpora:

- `HuggingFaceH4/ultrachat_200k` for general chat calibration, matching the Red Hat Qwen3 NVFP4 reference style.
- MBPP/HumanEval-style prompts or a permissive code instruction corpus for code.
- GSM8K train or similar for math reasoning.

Keep sample count, max sequence length, base model, and quantization recipe fixed across calibration domains.

## Priority 2: Add Task Metrics

NLL is useful as a deterministic smoke-test metric, but it does not directly answer whether the model solves tasks. Add domain-specific metrics:

- chat: small held-out instruction following rubric or pairwise generation review
- code: HumanEval/MBPP pass@1 where feasible
- math: GSM8K exact match with answer extraction

## Priority 3: Add Data-Free Controls

Add data-free baselines available through LLM Compressor, such as FP8 dynamic/block or NVFP4A16 where supported, so the project can compare calibration-sensitive W4A4 against data-free approaches.

## Priority 4: Expand Domains

After the real-corpus three-domain run works, add long-document and multilingual calibration/evaluation domains.
