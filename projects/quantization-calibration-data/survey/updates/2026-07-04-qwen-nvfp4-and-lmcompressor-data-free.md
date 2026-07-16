# 2026-07-04 Update: Qwen NVFP4 And LLM Compressor Data-Free Schemes

## Question

Are Red Hat's Qwen NVFP4 models data-free, and which LLM Compressor methods are data-free?

## Findings

Red Hat's Qwen3 NVFP4 model cards are not data-free. They use calibration samples from `HuggingFaceH4/ultrachat_200k`.

`RedHatAI/Qwen3-32B-NVFP4` uses `oneshot` with `QuantizationModifier(..., scheme="NVFP4")`, `dataset=ds`, `num_calibration_samples=512`, and `max_seq_length=2048`.

`RedHatAI/Qwen3-30B-A3B-NVFP4` also uses UltraChat with 512 calibration samples. Its recipe explicitly defines FP4 weights and FP4 input activations. The comments state that the process calibrates a global activation scale used to quantize activations on the fly.

NVIDIA's Qwen3 NVFP4 model cards are also not data-free. They list `cnn_dailymail` as the calibration dataset and say the models are quantized with TensorRT Model Optimizer.

## LLM Compressor Data-Free Methods

LLM Compressor's `model_free_ptq` is the main documented data-free entrypoint. The docs say it is for data-free schemes and operates directly on safetensors checkpoint files without a Transformers model definition.

Common documented data-free presets include:

- `FP8_DYNAMIC`
- `FP8_BLOCK`
- `NVFP4A16`
- `MXFP4/MXFP8`

The docs explicitly say that calibration-dependent methods such as GPTQ, AWQ, SmoothQuant, and static activation quantization should use `oneshot` instead.

## Implication For exp-002

For this project, Red Hat Qwen3 NVFP4 is more relevant than Red Hat Gemma 4 FP8 Dynamic/Block because it already uses calibration samples. A strong exp-002 design is to reproduce the Red Hat Qwen3 NVFP4 recipe but replace UltraChat with domain-specific calibration sets.

## Sources

- https://huggingface.co/RedHatAI/Qwen3-32B-NVFP4
- https://huggingface.co/RedHatAI/Qwen3-30B-A3B-NVFP4
- https://huggingface.co/nvidia/Qwen3-32B-NVFP4
- https://huggingface.co/nvidia/Qwen3-30B-A3B-NVFP4
- https://docs.vllm.ai/projects/llm-compressor/en/latest/guides/entrypoints/model-free-ptq/
- https://docs.vllm.ai/projects/llm-compressor/en/latest/examples/quantization_w4a4_fp4/
