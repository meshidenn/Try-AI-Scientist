# 2026-07-04 Update: Blackwell FP4 And Activation Precision

## Question

Does using Blackwell FP4 Tensor Cores require A4 activations, and what activation precision do `FP8_DYNAMIC`, `FP8_BLOCK`, and `MXFP4` use?

## Findings

For practical LLM inference, fully using Blackwell FP4 Tensor Core compute means the GEMM operands need to be in FP4 form. That usually corresponds to W4A4: FP4 weights and FP4 activations. Weight-only FP4, such as `NVFP4A16` or `MXFP4A16`, can reduce weight storage and memory bandwidth but should not be treated as equivalent to W4A4 FP4 Tensor Core inference.

LLM Compressor's NVFP4 example says that on machines below SM100, vLLM will not run activation quantization and will only run weight-only quantization. The same page states that NVFP4 uses per-tensor global scales and per-group local scales for weights, plus per-tensor global activation scales and dynamic per-group local activation scales during inference.

## Activation Precision Table

| Scheme | Activation precision | Data-free? | Calibration data? | Notes |
| --- | --- | --- | --- | --- |
| `FP8_DYNAMIC` | FP8, dynamic per-token | Yes | No | Weights are static per-channel FP8. |
| `FP8_BLOCK` | FP8 activation path in supported kernels | Yes | No in model-free examples | Data-free FP8 block baseline. |
| `NVFP4` | FP4 activations | No | Yes | W4A4. Needs calibration samples for global activation scales. |
| `NVFP4A16` | A16 activations | Yes | No in model-free PTQ | Weight-only FP4. Does not fully test FP4 activation behavior. |
| `MXFP4/MXFP8` via `model_free_ptq` | Usually unchanged/A16 unless a W4A4 recipe is used | Yes | No in model-free PTQ | LLM Compressor lists this under data-free weight quantization schemes. |

## Implication For exp-002

If the goal is to measure Blackwell FP4 Tensor Core W4A4 behavior, exp-002 should use `NVFP4`, not `NVFP4A16` or generic model-free `MXFP4` weight-only quantization. If the goal is a data-free baseline, `FP8_DYNAMIC`, `FP8_BLOCK`, or `NVFP4A16` are appropriate baselines, but they answer a different question.

## Sources

- https://docs.vllm.ai/projects/llm-compressor/en/latest/examples/quantization_w4a4_fp4/
- https://docs.vllm.ai/projects/llm-compressor/en/latest/guides/entrypoints/model-free-ptq/
- https://docs.vllm.ai/projects/llm-compressor/en/latest/examples/quantization_w8a8_fp8/
- https://docs.vllm.ai/projects/llm-compressor/en/latest/key-models/gemma4/fp8-block-example/
