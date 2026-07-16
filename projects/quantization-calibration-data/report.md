# Quantization Calibration Data Report

## 概要

このprojectの目的は、LLMのpost-training quantization (PTQ) において、calibration data の選び方が量子化後の精度劣化にどの程度影響するかを調べることである。ここでいう「量子化するデータ」はfine-tuning dataではなく、GPTQ/AWQ/SmoothQuant/NVFP4 W4A4のようなcalibration-dependent PTQで、activation scaleや近似再構成に使われるcalibration dataを指す。

今回の主実験は `Qwen/Qwen3-4B-Instruct-2507` を対象に、LLM Compressor の NVFP4 W4A4 `oneshot` quantization を使った。評価は主に held-out next-token NLL で行った。NLLは生成回答の正誤ではなく、評価テキストの次tokenをどれだけ高い確率で予測できるかを測る指標であり、低いほど良い。

## 背景整理

Red Hat Gemma 4 の FP8 Dynamic / FP8 Block 系は、公開情報上は LLM Compressor の `model_free_ptq` による data-free quantization として扱われる。これらはcalibration datasetを使わないため、calibration dataのドメイン差を調べる本projectの中心実験には直接向かない。一方、Red Hat Qwen3 NVFP4 系のmodel cardでは、UltraChatのcalibration samplesを使う `oneshot` NVFP4 quantization が示されており、calibration data依存性を見るにはこちらの方が近い。

したがって、このprojectでは以下を分けて扱う。

| 種類 | calibration data | 役割 |
| --- | --- | --- |
| data-free PTQ | 使わない | 強いdeployment baseline。dataset選定リスクが低いが、target workloadへの適応は弱い。 |
| calibration-dependent PTQ | 使う | calibration dataの分布がactivation scaleや量子化誤差に影響しうる。今回の中心対象。 |

## 実験一覧

| exp | 目的 | 主な設定 | 結果の位置づけ |
| --- | --- | --- | --- |
| `exp-001` | toy pipeline確認 | sklearn digits | LLMのclaimには使わない |
| `exp-002` | synthetic calibration smoke | synthetic general/code/math/mixed | pipeline確認寄り |
| `exp-003` | 実データdomain比較 | UltraChat / MBPP / GSM8K | domain calibrationの小規模pilot |
| `exp-004` | 言語比較pilot | English Dolly / Japanese Dolly variant / mixed | 日本語データ出典が弱めのpilot |
| `exp-005` | LLM-jp日本語データで再評価 | English Dolly / `llm-jp/llm-jp-instructions` / mixed | 現時点の主な言語比較結果 |

## exp-003: domain calibration pilot

`exp-003` では、同じbase modelとNVFP4 W4A4 recipeで、calibration domainだけを変えた。

| domain | calibration/eval dataset | calibration samples | eval samples |
| --- | --- | ---: | ---: |
| general_chat | `HuggingFaceH4/ultrachat_200k` | 64 | 12 |
| code | `google-research-datasets/mbpp` | 64 | 12 |
| math_reasoning | `openai/gsm8k` | 64 | 12 |

NLL結果は以下である。値は `NLL / perplexity / ΔNLL vs base`。

| model | general_chat | code | math_reasoning |
| --- | ---: | ---: | ---: |
| base | 1.9803 / 7.24 / +0.0000 | 1.4604 / 4.31 / +0.0000 | 1.2192 / 3.38 / +0.0000 |
| general_chat calib | 2.0403 / 7.69 / +0.0600 | 1.5615 / 4.77 / +0.1011 | 1.3065 / 3.69 / +0.0873 |
| code calib | 2.0470 / 7.74 / +0.0667 | 1.5780 / 4.85 / +0.1175 | 1.2848 / 3.61 / +0.0656 |
| math calib | 2.0302 / 7.62 / +0.0499 | 1.5647 / 4.78 / +0.1043 | 1.2979 / 3.66 / +0.0787 |

観察として、全てのquantized variantはbaseよりNLLが悪化した。また、この小規模pilotではmatched-domain calibrationはどのdomainでも最良にならなかった。これは「calibration dataを評価domainに合わせれば必ず勝つ」という単純な仮説を支持しない。

ただし、評価は12 samples/domainと小さい。加えて、MBPP/GSM8Kのgeneration smoke testは4 samples/taskに留まるため、下流task accuracyの結論としては扱わない。

## exp-004: Japanese/English pilot

`exp-004` では、calibration dataの言語を変えた。日本語には `kunishou/databricks-dolly-15k-ja` を使ったが、後で出典面を考慮し、`exp-005` でLLM-jp公式データへ置き換えた。

| model | English eval | Japanese eval |
| --- | ---: | ---: |
| base | 2.1340 / 8.4490 / 0.0000 | 2.2321 / 9.3197 / 0.0000 |
| English calib | 2.1893 / 8.9291 / +0.0553 | 2.2649 / 9.6304 / +0.0328 |
| Japanese calib | 2.1943 / 8.9735 / +0.0602 | 2.2596 / 9.5792 / +0.0275 |
| bilingual mixed | 2.2045 / 9.0659 / +0.0705 | 2.2542 / 9.5274 / +0.0220 |

このpilotでは、English evalはEnglish calibrationが最良、日本語evalはbilingual mixedが最良だった。ただし評価は24 samples/languageで、日本語データの出典にも懸念があった。

## exp-005: LLM-jp Japanese data での再評価

`exp-005` では、日本語データを `llm-jp/llm-jp-instructions` に置き換え、評価サンプルを100 samples/languageへ増やした。通常の `datasets.load_dataset("llm-jp/llm-jp-instructions", data_dir="v1.0")` ではsplit名の不整合が出たため、converted parquet shardを明示して読み込んだ。正確なURLは `experiments/exp-005/artifacts/calibration/manifest.json` に記録している。

| language condition | dataset / construction | calibration samples | evaluation samples |
| --- | --- | ---: | ---: |
| English | `databricks/databricks-dolly-15k` | 64 | 100 |
| Japanese | `llm-jp/llm-jp-instructions`, `v1.0/train` | 64 | 100 |
| bilingual mixed | English 32 + LLM-jp Japanese 32 | 64 | 0 |

NLL結果は以下である。

| calibration | English eval NLL | English ΔNLL | Japanese eval NLL | Japanese ΔNLL |
| --- | ---: | ---: | ---: | ---: |
| base | 2.2731 | 0.0000 | 2.3389 | 0.0000 |
| English | 2.3390 | +0.0659 | 2.3740 | +0.0352 |
| LLM-jp Japanese | 2.3511 | +0.0780 | **2.3624** | **+0.0235** |
| bilingual mixed | **2.3367** | **+0.0637** | 2.3719 | +0.0330 |

主な観察は次の通り。

- 全てのNVFP4 W4A4 variantはbaseよりNLLが悪化した。
- 日本語評価では、LLM-jp Japanese calibrationが最良だった。English calibrationのΔNLLは+0.0352、bilingual mixedは+0.0330、Japanese calibrationは+0.0235である。
- English評価では、bilingual mixedがわずかに最良だった。ただしEnglish calibrationとの差は0.0023 NLLで小さい。
- `exp-004` では日本語評価でbilingual mixedが最良だったが、`exp-005` ではmatched Japanese calibrationが最良になった。したがって、日本語データセットの選び方は結論に影響した。

## NLL差の読み方

NLLの差はnats/tokenであり、`ΔNLL = 0.01` はper-token perplexityで約1%の悪化に相当する。ただし、下流task accuracyへ直接変換はできない。コード生成、数学推論、翻訳、雑談では、NLL差が正答率や主観品質へどう現れるかは異なる。

今回の `exp-005` では、日本語評価におけるEnglish calibrationとJapanese calibrationの差は `0.0352 - 0.0235 = 0.0117` NLLである。これは小さいが、100 samplesで同条件比較したうえでの差なので、次に下流taskで確認する価値はある。一方、English評価におけるbilingual mixedとEnglish calibrationの差は0.0023 NLLであり、現時点では微差として扱うのが妥当である。

## 結論

現時点の実測から言えることは以下である。

1. NVFP4 W4A4量子化では、今回の全実験でbase modelよりNLLが悪化した。
2. calibration dataの違いにより、量子化後の劣化幅とvariant順位は変わる。
3. domain比較の `exp-003` ではmatched-domain advantageは確認できなかった。
4. language比較の `exp-005` では、LLM-jp Japanese evaluationに対してmatched Japanese calibrationが最良だった。
5. 日本語データの出典を変えると結論が変わったため、calibration data研究ではdataset choice自体を主要な実験条件として明記する必要がある。

## 限界

- NLLは生成回答の正誤ではない。
- `exp-003` のdomain評価は12 samples/domainと小さい。
- `exp-005` は100 samples/languageだが、instruction textのNLLに限られる。
- calibration sample数は64であり、512 samplesなどRed Hat Qwen3 NVFP4 model cardに近い規模では未検証である。
- vLLMは今回使っていない。Transformers/compressed-tensorsでNLL評価が完走したためである。

## 次の計画

1. `exp-005` の設定で、Japanese/Englishの小規模generation taskを追加する。
   - Japanese QA / summarization / translation
   - English QA / summarization
   - 必要ならjudge-based評価を使う
2. calibration sample数を64から256または512へ増やし、matched Japanese calibrationの優位が安定するか見る。
3. `llm-jp/magpie-sft-v1.0` を使い、manual instruction datasetとsynthetic instruction datasetの差を見る。
4. data-free FP8 / NVFP4A16 / MXFP4 をbaselineとして追加し、calibration-dependent NVFP4 W4A4と比較する。
5. 生成評価がTransformers経路で遅すぎる場合のみ、vLLMを精度評価の実行backendとして検討する。

## 主要artifact

- `experiments/exp-003/results/results.md`
- `experiments/exp-004/results/results.md`
- `experiments/exp-005/results/results.md`
- `experiments/exp-005/results/scores.json`
- `experiments/exp-005/results/claims.json`
- `survey/README.md`
- `survey/sources.md`
