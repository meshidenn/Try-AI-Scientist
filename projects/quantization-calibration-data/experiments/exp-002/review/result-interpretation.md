# Result Interpretation

## What Was Learned

The local environment can run an end-to-end LLM calibration-domain pilot for NVFP4 W4A4 on `Qwen/Qwen3-4B-Instruct-2507`:

- build synthetic calibration sets
- quantize three NVFP4 variants with LLM Compressor
- build separate held-out synthetic evaluation sets
- evaluate base and quantized variants with deterministic NLL/perplexity

The evaluation result is mixed. On the current synthetic held-out set, all three NVFP4 variants improved NLL on `general_chat` relative to base, but all three worsened NLL on `code` and `math_reasoning` relative to base.

Among quantized variants, the best model per evaluation domain was:

| evaluation_domain | best_quantized_model | delta_nll_vs_base |
| --- | --- | ---: |
| `general_chat` | `nvfp4_code` | -0.2070 |
| `code` | `nvfp4_general_chat` | +0.1674 |
| `math_reasoning` | `nvfp4_general_chat` | +0.1823 |

## What Was Not Learned

This pilot does not establish real-world calibration-domain behavior. The calibration and evaluation sets are tiny synthetic prompt/answer texts, and the metric is NLL only. No exact-match, pass@1, long-document, multilingual, RAG, or human preference evaluation has been run.

The results also do not explain why quantized variants outperform base on `general_chat`; this can happen with small NLL sets due to tokenization, reference wording, numerical noise, or regularization-like quantization effects.

## Hypothesis Status

Weakly tested and not supported by this pilot. Matched calibration did not produce the best quantized NLL for any of the three synthetic evaluation domains.

## Research Judgment

The pipeline is now ready for a more meaningful experiment. The next scientifically useful step is to replace both calibration and evaluation data with real corpora while keeping the model, sample count, max sequence length, and quantization recipe fixed.
