# 2026-07-04 Update: Red Hat Gemma 4 FP8 Quantization

## Question

How are Red Hat's Gemma 4 FP8 models quantized, and are they comparable to AWQ/GPTQ for studying calibration data effects?

## Findings

Red Hat's published Gemma 4 FP8 Dynamic and FP8 Block model cards describe data-free quantization flows using LLM Compressor. They are therefore different from AWQ/GPTQ experiments where the calibration dataset is an explicit input.

### FP8 Dynamic

For `RedHatAI/gemma-4-26B-A4B-it-FP8-Dynamic` and `RedHatAI/gemma-4-31B-it-FP8-dynamic`, the cards describe:

- FP8 weight quantization.
- FP8 activation quantization.
- Static per-channel FP8 scaling for weights.
- Dynamic per-token scaling for activations at inference time.
- LLM Compressor `model_free_ptq` with `scheme="FP8_DYNAMIC"`.
- No calibration dataset.

### FP8 Block

For `RedHatAI/gemma-4-31B-it-FP8-block`, the card describes:

- FP8 weight and activation quantization.
- Block-wise FP8 weight scaling with 128 by 128 blocks.
- Dynamic per-group activation quantization with `group_size=128`.
- LLM Compressor `model_free_ptq` with `scheme="FP8_BLOCK"`.
- No calibration dataset.

## Comparison Against Calibration-Dependent Methods

| Method | Calibration data influence | Expected usefulness for this project |
| --- | --- | --- |
| Red Hat FP8 Dynamic | None in the published flow | Strong data-free deployment baseline; not a direct calibration-domain experiment |
| Red Hat FP8 Block | None in the published flow | Strong data-free deployment baseline; useful for comparison |
| AWQ | High | Main candidate for testing whether code/math/chat calibration changes downstream degradation |
| GPTQ | High | Main candidate for testing calibration-domain sensitivity |
| SmoothQuant / INT8 W8A8 | Medium to high | Secondary candidate if activation scaling behavior is the focus |

## Implication For exp-002

`exp-002` should not use Red Hat FP8 Dynamic/Block alone to answer the calibration data question. Instead, it should:

1. Use AWQ or GPTQ on a feasible base LLM.
2. Vary only the calibration domain.
3. Evaluate all quantized variants on general chat, code, math/reasoning, long document, and multilingual tasks.
4. Include Red Hat-style data-free FP8 as a baseline if the hardware and model support it.

## Sources

- https://huggingface.co/RedHatAI/gemma-4-26B-A4B-it-FP8-Dynamic
- https://huggingface.co/RedHatAI/gemma-4-31B-it-FP8-dynamic
- https://huggingface.co/RedHatAI/gemma-4-31B-it-FP8-block
- https://docs.vllm.ai/projects/llm-compressor/en/latest/examples/quantization_w8a8_fp8/
- https://docs.vllm.ai/projects/llm-compressor/en/latest/key-models/gemma4/fp8-block-example/
- https://docs.vllm.ai/projects/llm-compressor/en/latest/examples/awq/
