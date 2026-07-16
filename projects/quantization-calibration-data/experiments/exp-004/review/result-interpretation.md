# Result Interpretation

## What Was Learned

`exp-004` completed a real Japanese-vs-English calibration-language pilot for NVFP4 W4A4.

| evaluation_language | best_quantized_model | delta_nll_vs_base |
| --- | --- | ---: |
| `english_instruction` | `nvfp4_lang_english_instruction` | +0.0553 |
| `japanese_instruction` | `nvfp4_lang_bilingual_mixed` | +0.0220 |

All quantized variants were worse than base on both languages. Within quantized variants, English matched-language calibration won on English evaluation. Japanese-only calibration was better than English calibration on Japanese evaluation, but bilingual mixed calibration was slightly better still.

## Hypothesis Status

Partially supported for English, not fully supported for Japanese. The Japanese result suggests mixed calibration may be more robust than narrow Japanese-only calibration in this small setup.

## What Was Not Learned

This experiment does not measure generation quality, translation accuracy, chat preference, or Japanese task correctness. It only measures held-out instruction-text NLL.

## Research Judgment

The language axis appears worth studying further. The signal is small but coherent enough to scale: matched English helps English; Japanese evaluation benefits from Japanese-containing calibration, with mixed slightly ahead of Japanese-only.
