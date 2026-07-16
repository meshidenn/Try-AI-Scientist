# Sources

- Google. 2026. `google/gemma-4-26B-A4B-it-assistant`. Hugging Face model
  card. URL: https://huggingface.co/google/gemma-4-26B-A4B-it-assistant.
  Accessed: 2026-07-04.
  - Relation: official Gemma 4 26B assistant drafter for MTP/speculative
    decoding; pairs with `google/gemma-4-26B-A4B-it`.
- Red Hat AI. 2026. `RedHatAI/gemma-4-26B-A4B-it-FP8-Dynamic`. Hugging Face
  model card.
  - Relation: FP8 dynamic target model to compare against the original target.

## Related Reports And Literature Added 2026-07-05

- vLLM issue #41789. 2026. `[Bug]: gemma4 31B MTP Avg Draft acceptance rate: 0.2%`.
  URL: https://github.com/vllm-project/vllm/issues/41789. Accessed: 2026-07-05.
  - Relation: closest public report found. It uses a quantized Gemma 4 31B target, Gemma 4 assistant MTP, `num_speculative_tokens=4`, and `kv_cache_dtype=fp8`; the reported average draft acceptance rate is 0.2%.
  - Difference from this project: reported target is AWQ 4-bit / Gemma 4 31B, not RedHatAI Gemma 4 26B FP8 Dynamic.
- vLLM issue #46088. 2026. `[Bug]: MTP speculative decoding with --kv-cache-dtype auto produces cross-sequence garbage under batching (Gemma-4 W4A16; fp8 KV unaffected)`.
  URL: https://github.com/vllm-project/vllm/issues/46088. Accessed: 2026-07-05.
  - Relation: Gemma 4 quantized target plus MTP under batching. The issue points to KV-cache/spec-decode interactions and mixed sequence lengths; fp8 KV cache is reported as a workaround for their corruption case.
- vLLM issue #42005. 2026. `[Doc]: Gemma 4 assistant speculative decoding docs do not match actual behavior on vLLM 0.20.1`.
  URL: https://github.com/vllm-project/vllm/issues/42005. Accessed: 2026-07-05.
  - Relation: explains why older vLLM versions treated Gemma 4 assistant as `draft_model` and failed; supports using a newer container with explicit `method: mtp`.
- vLLM issue #43456. 2026. `[deepseek_v4] DeepSeekV4MTP loader silently skips top-level head.weight + embed.weight -> 0% MTP draft acceptance with no error`.
  URL: https://github.com/vllm-project/vllm/issues/43456. Accessed: 2026-07-05.
  - Relation: not Gemma 4, but documents an MTP quantization/artifact loader failure mode that causes near-zero acceptance with no runtime error.
- vLLM issue #43457. 2026. `[deepseek_v4 / DeepGEMM] paged_mqa_logits kernel asserts on next_n=3 -> num_speculative_tokens capped at 1 on Hopper`.
  URL: https://github.com/vllm-project/vllm/issues/43457. Accessed: 2026-07-05.
  - Relation: not Gemma 4, but shows FP8/MTP kernel constraints can make `num_speculative_tokens > 1` invalid or suboptimal for some hardware/model paths.
- vLLM issue #47297. 2026. `[Bug]: ~7x MTP (K=3) decode-throughput regression on Qwen3.6-35B-A3B (GB10 / sm_121) in recent nightlies`.
  URL: https://github.com/vllm-project/vllm/issues/47297. Accessed: 2026-07-05.
  - Relation: not Gemma 4, but directly reports an MTP decode throughput regression on GB10/sm_121, relevant to this project's hardware-risk dimension.
- vLLM docs. 2026. `MTP (Multi-Token Prediction)`.
  URL: https://docs.vllm.ai/en/latest/features/speculative_decoding/mtp/. Accessed: 2026-07-05.
  - Relation: official docs state Gemma 4 assistant checkpoints should use `method: mtp`, are not generic draft models, and that a small `num_speculative_tokens` such as 1 is a good starting default.
- Shukla, Shikhar. 2026. `SpecKV: Adaptive Speculative Decoding with Compression-Aware Gamma Selection`. arXiv:2605.02888.
  URL: https://arxiv.org/abs/2605.02888. Accessed: 2026-07-05.
  - Relation: paper argues optimal speculation length changes with compression level and reports profiling across compression regimes. Supports sweeping `num_speculative_tokens` instead of assuming fixed 4 is optimal.
- Liu, Xiaoxuan; Yu, Jiaxiang; Park, Jongseok; Stoica, Ion; Cheung, Alvin. 2026. `Speculative Decoding: Performance or Illusion?`. arXiv:2601.11580.
  URL: https://arxiv.org/abs/2601.11580. Accessed: 2026-07-05.
  - Relation: vLLM-focused speculative decoding study covering MTP; emphasizes that acceptance length varies by positions, requests, datasets, and batch sizes, and that measured speedups can lag theoretical bounds.

