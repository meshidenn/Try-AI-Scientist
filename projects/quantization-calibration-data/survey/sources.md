# Sources

## Red Hat / LLM Compressor Sources

- RedHatAI. 2026. `RedHatAI/gemma-4-26B-A4B-it-FP8-Dynamic`. Hugging Face model card. URL: https://huggingface.co/RedHatAI/gemma-4-26B-A4B-it-FP8-Dynamic. Accessed: 2026-07-04.
  - Relation: states that the model is quantized to FP8 using dynamic per-token activation quantization and static per-channel FP8 weight scaling; creation uses `model_free_ptq(..., scheme="FP8_DYNAMIC", ...)`.
- RedHatAI. 2026. `RedHatAI/gemma-4-31B-it-FP8-dynamic`. Hugging Face model card. URL: https://huggingface.co/RedHatAI/gemma-4-31B-it-FP8-dynamic. Accessed: 2026-07-04.
  - Relation: same Red Hat Gemma 4 dynamic FP8 pattern; model card says data-free FP8 dynamic quantization with LLM Compressor.
- RedHatAI. 2026. `RedHatAI/gemma-4-31B-it-FP8-block`. Hugging Face model card. URL: https://huggingface.co/RedHatAI/gemma-4-31B-it-FP8-block. Accessed: 2026-07-04.
  - Relation: states FP8 block quantization with 128 by 128 weight blocks and dynamic per-group activation quantization; creation uses `scheme="FP8_BLOCK"`.
- vLLM Project. 2026. LLM Compressor docs, `fp8 Weight and Activation Quantization`. URL: https://docs.vllm.ai/projects/llm-compressor/en/latest/examples/quantization_w8a8_fp8/. Accessed: 2026-07-04.
  - Relation: documents that `FP8_DYNAMIC` uses static per-channel weight quantization and dynamic per-token activation quantization, and does not need calibration data.
- vLLM Project. 2026. LLM Compressor docs, Gemma 4 FP8 Block Example. URL: https://docs.vllm.ai/projects/llm-compressor/en/latest/key-models/gemma4/fp8-block-example/. Accessed: 2026-07-04.
  - Relation: states Gemma 4 FP8 block quantization uses `model_free_ptq` and does not require a calibration dataset.
- vLLM Project. 2026. LLM Compressor docs, AWQ Quantization. URL: https://docs.vllm.ai/projects/llm-compressor/en/latest/examples/awq/. Accessed: 2026-07-04.
  - Relation: documents AWQ as using a small calibration dataset to derive scaling factors.

- RedHatAI. 2025. `RedHatAI/Qwen3-32B-NVFP4`. Hugging Face model card. URL: https://huggingface.co/RedHatAI/Qwen3-32B-NVFP4. Accessed: 2026-07-04.
  - Relation: documents NVFP4 quantization with LLM Compressor using 512 UltraChat calibration samples and `oneshot`.
- RedHatAI. 2025. `RedHatAI/Qwen3-30B-A3B-NVFP4`. Hugging Face model card. URL: https://huggingface.co/RedHatAI/Qwen3-30B-A3B-NVFP4. Accessed: 2026-07-04.
  - Relation: documents NVFP4 quantization with LLM Compressor using 512 UltraChat calibration samples and a recipe with FP4 weights and FP4 input activations.
- NVIDIA. 2025. `nvidia/Qwen3-32B-NVFP4`. Hugging Face model card. URL: https://huggingface.co/nvidia/Qwen3-32B-NVFP4. Accessed: 2026-07-04.
  - Relation: documents TensorRT Model Optimizer FP4 quantization and lists `cnn_dailymail` as the calibration dataset.
- NVIDIA. 2025. `nvidia/Qwen3-30B-A3B-NVFP4`. Hugging Face model card. URL: https://huggingface.co/nvidia/Qwen3-30B-A3B-NVFP4. Accessed: 2026-07-04.
  - Relation: documents TensorRT Model Optimizer FP4 quantization and lists `cnn_dailymail` as the calibration dataset.
- vLLM Project. 2026. LLM Compressor docs, `model_free_ptq`. URL: https://docs.vllm.ai/projects/llm-compressor/en/latest/guides/entrypoints/model-free-ptq/. Accessed: 2026-07-04.
  - Relation: documents data-free `model_free_ptq`, including `FP8_DYNAMIC`, `FP8_BLOCK`, `NVFP4A16`, and `MXFP4/MXFP8`, and separates them from calibration-dependent GPTQ/AWQ/SmoothQuant/static activation quantization.
- vLLM Project. 2026. LLM Compressor docs, `fp4 Quantization with NVFP4`. URL: https://docs.vllm.ai/projects/llm-compressor/en/latest/examples/quantization_w4a4_fp4/. Accessed: 2026-07-04.
  - Relation: documents W4A4 NVFP4 calibration requirements, including global activation scale calibration.

- vLLM Project. 2026. LLM Compressor docs, `model_free_ptq`. URL: https://docs.vllm.ai/projects/llm-compressor/en/latest/guides/entrypoints/model-free-ptq/. Accessed: 2026-07-04.
  - Relation: documents `FP8_DYNAMIC`, `FP8_BLOCK`, `NVFP4A16`, and `MXFP4/MXFP8` as common data-free model-free PTQ presets and describes `model_free_ptq` as supporting data-free weight quantization schemes.
- NVIDIA. 2026. PTX ISA documentation. URL: https://docs.nvidia.com/cuda/parallel-thread-execution/index.html. Accessed: 2026-07-04.
  - Relation: reference for NVIDIA low-level instruction support and architecture-specific tensor core formats.

## Prior Work

- Lin et al. 2023. AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration. URL: https://arxiv.org/abs/2306.00978.
  - Relation: calibration activation distributions are central to AWQ scaling.
- Frantar et al. 2022. GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers. URL: https://arxiv.org/abs/2210.17323.
  - Relation: representative calibration samples are used for one-shot weight quantization.
- Williams and Aletras. 2023. On the Impact of Calibration Data in Post-training Quantization and Pruning. URL: https://arxiv.org/abs/2311.09755.
  - Relation: directly studies how calibration data affects compressed LLM performance.

## Local Experiment Sources

- The initial `exp-001` toy experiment uses local package documentation and the built-in `sklearn.datasets.load_digits` dataset. It is not the main LLM evidence for this project.
