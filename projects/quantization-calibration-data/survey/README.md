# Survey

## Research Question

このprojectの主目的は、LLMのpost-training quantization (PTQ) で使う calibration data のドメインが、量子化後の得手不得手と劣化量をどう変えるかを調べることである。

具体的には、一般会話、コード、数学・推論、長文文書、多言語のcalibration dataを用意し、同一base LLMを同一量子化方式で量子化したうえで、各評価ドメインにおける非量子化baselineからの性能低下を比較する。

## Working Hypothesis

- calibration data が評価ドメインの入力分布を代表しているほど、そのドメインでの量子化劣化が小さくなる可能性がある。
- ただしcalibration dataはfine-tuning dataではないため、「得意になる」というより「その分布で量子化誤差が小さくなる」と解釈する。
- AWQやGPTQのようにcalibration sampleからactivation統計や近似Hessianを使う方式では、calibration dataのドメイン差が出やすい。
- Red Hat Gemma 4 FP8 Dynamic/Blockのようなdata-free FP8 quantizationでは、calibration dataのドメイン差は原理的に出ない。比較するときは「calibration-sensitive方式」と「data-free方式」の違いとして扱う。

## Calibration Domains

| Calibration data | Expected lower degradation | Possible higher degradation |
| --- | --- | --- |
| General chat | Chat, short QA | Code, math, long reasoning |
| Code | Programming completion and code QA | Natural conversation, translation, casual writing |
| Math/reasoning | Step-by-step reasoning, math QA | Naturalness of daily conversation |
| Long documents | RAG, long-context QA, summarization | Short response naturalness or latency may not improve |
| Multilingual | Translation, Japanese/English mixed prompts | Narrow domain tasks |
| Mixed balanced | Robust average performance | May not be best on any single specialized domain |

## Language Calibration Axis

日本語 vs 英語の比較では、ドメインをinstruction textに寄せたまま、calibration dataの言語だけを変える。これは「多言語」ドメインをさらに分解し、英語calibration、日本語calibration、日英混合calibrationが、それぞれ英語評価・日本語評価の量子化劣化にどう影響するかを見るためである。

重要なのは、この比較もfine-tuningではなくPTQ calibrationの比較である点である。日本語calibrationで日本語能力が学習されるわけではなく、日本語入力分布に対するactivation scaleや量子化誤差がどれだけ合うかを見る。

最初の実験は`exp-004`として、生成速度に依存しにくいNLL/perplexityを主指標にする。生成ベースのaccuracy評価は、Transformers/compressed-tensors経路のdecodeが精度評価の完走を妨げる場合のみ、vLLMを実行backendとして検討する。速度そのものはこの実験の評価対象ではない。

## Method Comparison

| Method family | Uses calibration data? | Why it matters here |
| --- | --- | --- |
| AWQ | Yes | Uses calibration data to derive activation-aware scaling factors before low-bit weight quantization. Good candidate for measuring domain-dependent calibration effects. |
| GPTQ | Yes | Uses calibration examples to approximate layerwise reconstruction behavior. Good candidate for measuring calibration-domain sensitivity. |
| SmoothQuant / INT8 W8A8 | Usually yes | Calibration affects activation scaling and outlier handling. Useful secondary comparison. |
| FP8 Dynamic, Red Hat Gemma 4 style | No for published Red Hat Gemma 4 FP8 Dynamic cards | Activations are scaled dynamically per token at inference time; weights use static FP8 scaling. Calibration-domain effects should not appear because no calibration dataset is used. |
| FP8 Block, Red Hat Gemma 4 style | No for published Red Hat Gemma 4 FP8 Block cards | Uses model-free FP8 block quantization. Good data-free baseline, not a direct test of calibration data choice. |
| NVFP4 W4A4, Red Hat Qwen3 style | Yes for published Red Hat Qwen3 NVFP4 cards | Red Hat Qwen3 NVFP4 model cards use LLM Compressor `oneshot` with UltraChat calibration samples. This is directly relevant for calibration-domain sensitivity experiments. |
| NVFP4A16 / MXFP4 / MXFP8 model-free PTQ | No in LLM Compressor `model_free_ptq` | Weight-only or microscale data-free baselines. Useful comparison, but less direct for calibration-domain sensitivity than W4A4 NVFP4, AWQ, GPTQ, or SmoothQuant. |

## Red Hat Gemma 4 Quantization Notes

Red Hat publishes Gemma 4 FP8 Dynamic and FP8 Block variants on Hugging Face. The public model cards describe them as LLM Compressor quantizations for vLLM.

- `RedHatAI/gemma-4-26B-A4B-it-FP8-Dynamic`: weights and activations are FP8; weights use static per-channel FP8 scaling, activations use dynamic per-token scaling at inference time. The creation snippet uses `model_free_ptq(..., scheme="FP8_DYNAMIC", ...)`, described as data-free.
- `RedHatAI/gemma-4-31B-it-FP8-dynamic`: same dynamic FP8 pattern for Gemma 4 31B. The model card states data-free FP8 dynamic quantization with LLM Compressor.
- `RedHatAI/gemma-4-31B-it-FP8-block`: weights use block-wise FP8 scaling with 128 by 128 blocks, activations are dynamically quantized per group with `group_size=128`. The model card and LLM Compressor Gemma 4 example state that this FP8 block path does not require calibration data.

Implication: Red Hat Gemma 4 FP8 models are valuable as strong deployment baselines, but they do not answer the central project question by themselves. To test calibration data domain effects, exp-002 should use AWQ/GPTQ or another calibration-dependent PTQ method on the same base model or a smaller locally feasible LLM.

## Red Hat Qwen3 NVFP4 Quantization Notes

Red Hat's published Qwen3 NVFP4 model cards are not data-free. They use LLM Compressor with calibration samples from `HuggingFaceH4/ultrachat_200k`.

- `RedHatAI/Qwen3-32B-NVFP4`: the creation snippet uses `oneshot(..., dataset=ds, recipe=QuantizationModifier(..., scheme="NVFP4"), num_calibration_samples=512, ...)` after preprocessing UltraChat chat-template text.
- `RedHatAI/Qwen3-30B-A3B-NVFP4`: the creation snippet also uses UltraChat, 512 calibration samples, and an explicit recipe with FP4 weights and FP4 input activations. The card comments that weights are quantized to FP4 with per-group 16 via PTQ and that a global activation scale is calibrated.

Implication: Red Hat Qwen3 NVFP4 is closer to this project's central question than Red Hat Gemma 4 FP8 Dynamic/Block. It is a useful reference recipe for exp-002, but to test domain effects we should replace UltraChat with code, math, long-document, multilingual, and mixed calibration sets while keeping model, sample count, sequence length, and quantization recipe fixed.

## LLM Compressor Data-Free Methods

LLM Compressor documents `model_free_ptq` as the entrypoint for data-free schemes. It operates directly on safetensors rather than loading a full Transformers model and computes scales from weight tensors. The docs list examples such as `FP8_DYNAMIC`, `FP8_BLOCK`, `NVFP4A16`, and `MXFP4/MXFP8`.

The same docs explicitly separate these from calibration-dependent methods: GPTQ, AWQ, SmoothQuant, and static activation quantization should use `oneshot` because they require calibration data.

## Blackwell FP4 Tensor Core And Activation Precision

For Blackwell FP4 Tensor Core acceleration, the matrix multiplication operands need to reach the FP4 compute path. In LLM serving terms, this usually means W4A4: FP4 weights and FP4 activations. Weight-only FP4 variants such as `NVFP4A16` or `MXFP4A16` reduce weight memory bandwidth, but they do not fully exercise FP4 activation quantization and should not be treated as equivalent to W4A4 FP4 Tensor Core inference.

LLM Compressor's NVFP4 example makes this distinction explicit: on machines below SM100, vLLM will not run activation quantization and will only run weight-only quantization. For NVFP4 W4A4, weights use per-tensor global scales and per-group local scales, while activations use calibrated per-tensor global scales plus dynamic per-group local scales during inference.

| Scheme | Weight precision | Activation precision | Data-free? | Calibration data? | Notes |
| --- | --- | --- | --- | --- | --- |
| `FP8_DYNAMIC` | FP8, static per-channel | FP8, dynamic per-token | Yes | No | Data-free W8A8-style FP8. |
| `FP8_BLOCK` | FP8 block-wise scaling | FP8 activation path in supported serving kernels | Yes | No in model-free examples | Data-free FP8 block baseline, Blackwell-oriented. |
| `NVFP4` | FP4 weights | FP4 activations | No | Yes | W4A4 path; needs calibration for global activation scale. |
| `NVFP4A16` | NVFP4 weights | A16 activations | Yes | No in model-free PTQ | Weight-only FP4; not the same as W4A4 FP4 Tensor Core inference. |
| `MXFP4/MXFP8` via `model_free_ptq` | MXFP4 or MXFP8 weights | Usually unchanged/A16 unless a W4A4 recipe is used | Yes | No in model-free PTQ | Docs list this under data-free weight quantization schemes. |

## Data-Free Versus Calibration-Dependent Quantization

Data-free quantization is attractive because it is simple, reproducible, and avoids dataset licensing or privacy issues. It can be the right default when the goal is a fast deployment baseline and the chosen numeric format supports dynamic activation scaling or weight-only quantization.

However, data-free quantization has an important limitation: it cannot adapt its scales, smoothing, reconstruction objective, or outlier handling to the activation distribution of the target workload. That means it may be less optimal when the deployment workload is skewed toward code, math, Japanese, long-context retrieval, or another domain whose activations differ from generic text.

| Axis | Data-free methods | Calibration-dependent methods |
| --- | --- | --- |
| Setup cost | Low. No dataset pipeline is needed. | Higher. Requires dataset selection, preprocessing, and calibration runs. |
| Reproducibility | High, because fewer external inputs exist. | Lower unless calibration data and sampling are fixed carefully. |
| Privacy/licensing | Easier, because no calibration corpus is needed. | Must manage data rights and possible sensitive examples. |
| Workload adaptation | Weak. Scales are derived from weights or dynamic local statistics, not target examples. | Stronger. Activation statistics or reconstruction can match the target distribution. |
| Risk of calibration overfit | None from calibration data. | Possible if calibration is too narrow or unrepresentative. |
| Best use | General deployment baseline, very large models, missing model definitions, data-free FP8/weight-only schemes. | Low-bit W4A4, AWQ/GPTQ/SmoothQuant, static activation quantization, domain-specific serving. |

The project should therefore compare both: data-free methods answer "how good is the easiest robust deployment path?", while calibration-dependent methods answer "can target-domain calibration preserve more task-specific quality?".

## Current Survey Status

The project now treats LLM calibration-domain sensitivity as the central question. `exp-001` is retained only as a toy pipeline check. The next real experiment should be `exp-002`, using an LLM and calibration-dependent quantization.
