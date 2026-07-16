# Survey

## Current Starting Point

The official Hugging Face model page for `google/gemma-4-26B-A4B-it-assistant`
describes it as a Multi-Token Prediction drafter for Gemma 4. The page states
that Gemma 4 MTP uses a smaller draft model in a speculative decoding pipeline,
where draft tokens are verified by the target model in parallel. The usage
example pairs:

- Target: `google/gemma-4-26B-A4B-it`
- Assistant drafter: `google/gemma-4-26B-A4B-it-assistant`

For this project, the FP8 comparison target is
`RedHatAI/gemma-4-26B-A4B-it-FP8-Dynamic`.

## Baseline Need

Before mitigation, measure:

- Original Gemma 4 26B A4B + official assistant drafter.
- FP8 Gemma 4 26B A4B + the same official assistant drafter.

The key metrics are output throughput, total throughput, mean TPOT, mean E2E
latency, and speculative acceptance statistics if exposed by the serving stack.

## Sources

- https://huggingface.co/google/gemma-4-26B-A4B-it-assistant
