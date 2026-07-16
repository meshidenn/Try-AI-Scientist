# Related Reports Search - 2026-07-05

## Question

Are there public reports of Gemma 4 FP8/quantized targets with MTP speculative decoding showing low acceptance rate or throughput regressions?

## Search Scope

- vLLM GitHub issues for `Gemma4 MTP`, `Gemma4 FP8 MTP`, `FP8 MTP acceptance`, and related terms.
- vLLM MTP documentation.
- Recent speculative decoding literature mentioning compression/quantization and MTP performance.

## Findings

### Closest Match

- vLLM #41789 reports Gemma 4 31B MTP with a quantized target, Gemma 4 assistant, `num_speculative_tokens=4`, and `kv_cache_dtype=fp8`, with Avg Draft acceptance rate reported as 0.2%.
- This is not the same target as this project: it uses a Gemma 4 31B AWQ 4-bit model, not RedHatAI Gemma 4 26B FP8 Dynamic.
- Still, it is a strong signal that Gemma 4 assistant MTP can collapse on quantized targets under some configurations.

### Related vLLM Issues

- vLLM #46088 reports Gemma 4 W4A16 + MTP correctness problems under batching with mixed long/short sequences. It is a KV-cache/spec-decode interaction report, not a throughput-only report.
- vLLM #42005 documents that older vLLM versions treated Gemma 4 assistant as generic `draft_model`; newer MTP support is required.
- vLLM #43456 reports a non-Gemma MTP loader failure causing 0% acceptance after quantization artifacts omit expected MTP head/embed keys.
- vLLM #43457 reports FP8/MTP kernel constraints around `num_speculative_tokens` on Hopper.
- vLLM #47297 reports an MTP decode-throughput regression on GB10/sm_121 in recent nightlies for Qwen3.6, which is hardware-path relevant even though it is not Gemma 4.

### Literature Signal

- SpecKV (Shukla 2026) argues that optimal speculation length depends on compression level; this supports sweeping `num_speculative_tokens` for BF16 and FP8 separately.
- Speculative Decoding: Performance or Illusion? (Liu et al. 2026) studies SD variants in vLLM, including MTP, and emphasizes that acceptance length varies across positions, requests, datasets, and batch sizes.

## Interpretation For This Project

I did not find a public report exactly matching `RedHatAI/gemma-4-26B-A4B-it-FP8-Dynamic` + `google/gemma-4-26B-A4B-it-assistant` + vLLM MTP slowdown. However, public reports do support the broader failure pattern:

1. Gemma 4 quantized targets can show extremely low MTP acceptance.
2. MTP behavior can depend strongly on `num_speculative_tokens`, KV dtype, batch composition, and hardware/kernel path.
3. Fixed `num_speculative_tokens=4` is not a safe universal default for compressed targets.

## URLs

- https://github.com/vllm-project/vllm/issues/41789
- https://github.com/vllm-project/vllm/issues/46088
- https://github.com/vllm-project/vllm/issues/42005
- https://github.com/vllm-project/vllm/issues/43456
- https://github.com/vllm-project/vllm/issues/43457
- https://github.com/vllm-project/vllm/issues/47297
- https://docs.vllm.ai/en/latest/features/speculative_decoding/mtp/
- https://arxiv.org/abs/2605.02888
- https://arxiv.org/abs/2601.11580
