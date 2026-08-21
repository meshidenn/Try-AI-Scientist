# Results

## Summary

Toyotaの4資料から各1ページ、計4ページをMarkdownへ変換するローカルvLLM pilotを実行した。対象はQwen3.6-27B、InternVL3.5-8B、GLM-4.6V-Flashで、各モデルに`image_first`（ページ画像のみ）と`hybrid`（画像+PDF parser抽出payload）を適用した。

QwenとGLMは8/8リクエストで利用可能なMarkdownを出力した。数値token F1はQwen hybridが最高（0.721653）、text-length proxyはGLM hybridが最高（0.717053）、平均ページ時間はGLM hybridが最短（61.746694秒）だった。InternVLは8/8がHTTP上は成功したが、数値を含まない断片・反復出力で意味的に無効と判定し、優劣比較から除外する。

本結果は4ページのpilotに限定される。PDF text layerを擬似正解にする自動指標であり、図・表・レイアウトの忠実性を直接には測らない。

## Setup

- Backend: ローカル vLLM OpenAI-compatible server (`vllm/vllm-openai:v0.24.0`)、localhostのみ
- Model revisions: Qwen `Qwen/Qwen3.6-27B`（revision未記録）、InternVL `741a7d03020411e666c6109218ab71e08151ef86`、GLM `411bb4d77144a3f03accbf4b780f5acb8b7cde4e`
- Pages: securities report p.135 / earnings presentation p.8 / integrated report p.11 / midterm policy p.2
- Rendering: 300 dpi page image
- Decoding: temperature 0, top_p 1, max_new_tokens 1,024。Qwen / GLMはthinkingを無効化。
- Input: `image_first`はページ画像のみ、`hybrid`はページ画像+PDF parserの抽出payload。
- hybrid payload: 最大18,000文字。Qwenの統合報告書 p.11 は初回32,768-token上限超過後、この制約とコンテナ再起動を用いて成功した。
- GLM postprocess: raw出力を`outputs/glm-4.6v-flash/raw/`に保存し、`<|begin_of_box|>` / `<|end_of_box|>`だけを最終Markdownから除去した。

## Metrics

- `text_normalized_similarity_proxy`: PDF text layerと出力の正規化文字数の近さ。内容一致率ではない。
- `numeric_token_recall` / `precision` / `f1`: PDF text layerと出力に出現する数値token集合の比較。値の位置、列、重複、単位の対応は見ない。
- `table_row_width_consistency`: 検出したMarkdown tableで列数が揃うか。意味的な表の正しさは測らない。
- `wall_time_seconds`: 1ページのリクエスト処理時間（秒）。

## Main Results

| Model | Method | Semantic validity | Success | Text proxy | Numeric recall | Numeric precision | Numeric F1 | Mean wall time (s) | Consistent-table pages |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.6-27B | image_first | valid | 4/4 | 0.688820 | 0.616988 | 0.949213 | 0.658382 | 164.567408 | 0 |
| Qwen3.6-27B | hybrid | valid | 4/4 | 0.710277 | 0.650037 | 0.962963 | **0.721653** | 195.066573 | 0 |
| GLM-4.6V-Flash | image_first | valid | 4/4 | 0.713285 | 0.572970 | 0.948540 | 0.629333 | 64.388575 | 0 |
| GLM-4.6V-Flash | hybrid | valid | 4/4 | **0.717053** | 0.606667 | **0.995370** | 0.669129 | **61.746694** | 0 |
| InternVL3.5-8B | image_first | invalid | 4/4 | 0.408135 | 0.000000 | — | 0.000000 | 80.517054 | 0 |
| InternVL3.5-8B | hybrid | invalid | 4/4 | 0.526842 | 0.000000 | — | 0.000000 | 79.760018 | 0 |

有効モデル内では、両モデルともhybridがimage-firstより数値recallを上げた。Qwenは`+0.033049`、GLMは`+0.033697`である。Qwen hybridはGLM hybridよりnumeric F1が`+0.052524`高い一方、GLM hybridは平均時間が約3.16倍短い。

統合報告書 p.11 の数値recallは、Qwenがimage-first `0.030075`→hybrid `0.180451`、GLMが`0.015038`→`0.022556`だった。系譜図・レイアウトの接続関係が正しいことは、この値からは判断できない。

## Model-to-Model Agreement

同一4ページのモデル出力を直接比較した。文字列一致はNFKC正規化・空白除去後の`SequenceMatcher.ratio`、数値一致は数値token集合のJaccardであり、各ページを等重み平均した。

| Method | Pair | Character sequence agreement | Numeric-token Jaccard |
|---|---|---:|---:|
| image-first | Gemma4 × Qwen3.6 | 0.608464 | 0.581195 |
| image-first | Gemma4 × GLM-Flash | 0.637314 | 0.491016 |
| image-first | Qwen3.6 × GLM-Flash | **0.835061** | **0.834740** |
| hybrid | Gemma4 × Qwen3.6 | **0.751062** | **0.865741** |
| hybrid | Gemma4 × GLM-Flash | 0.681562 | 0.680952 |
| hybrid | Qwen3.6 × GLM-Flash | 0.701370 | 0.688159 |

詳細なページ別値と定義は`results/model_agreement.json`を参照。Gemmaはexp-001 / exp-003の既存出力を使うため、厳密な同一推論条件の比較ではない。

## Figures

図は未作成。ページ画像・生出力・正規化Markdownは`outputs/`に保存した。

## Failures And Negative Results

- Qwen hybridの統合報告書 p.11は、初回入力が36,201 tokenで32,768-token上限を超過した。payloadを18,000文字に制限した最初のrecoveryは、vLLM multimodal cache assertionによるHTTP 500で失敗した。Qwenコンテナ再起動後に成功した。
- InternVL3.5-8BはvLLM起動・8/8 HTTP応答には成功したが、出力が`。`や中国語断片などの反復で、全methodのnumeric recallが0だった。今回のvLLM/OpenAI content形式では意味的変換失敗として扱う。
- 全有効モデルでtable_row_width_consistencyは0。表の品質についての肯定的結論は出せない。
- max_new_tokens=1,024はspecの通常条件4,096と異なるpilot制約である。各出力が上限到達で終了したかはログから判定できない。
- PaddleOCR-VL、MinerU、DeepSeek-OCR-2、dotsは未実行である。

## Reproduction

共有実行器は`projects/pdf-to-markdown-toyota/workspace/run_general_vlm.py`。結果保存先を明示する。

```bash
uv run python projects/pdf-to-markdown-toyota/workspace/run_general_vlm.py \
  --root projects/pdf-to-markdown-toyota/experiments/exp-004 \
  --logical-name glm-4.6v-flash --model-id zai-org/GLM-4.6V-Flash \
  --served-model glm-4.6v-flash --base-url http://127.0.0.1:18024/v1 \
  --pilot --modes image_first hybrid --max-payload-chars 18000 \
  --disable-thinking --max-new-tokens 1024
```

評価:

```bash
uv run python projects/pdf-to-markdown-toyota/workspace/evaluate_model_comparison.py \
  --root projects/pdf-to-markdown-toyota/experiments/exp-004 \
  --log projects/pdf-to-markdown-toyota/experiments/exp-004/logs/qwen3.6-27b-image-first-pilot.json \
  --log projects/pdf-to-markdown-toyota/experiments/exp-004/logs/qwen3.6-27b-hybrid-pilot.json \
  --log projects/pdf-to-markdown-toyota/experiments/exp-004/logs/internvl3.5-8b-pilot.json \
  --log projects/pdf-to-markdown-toyota/experiments/exp-004/logs/glm-4.6v-flash-pilot.json
```

## Notes For Reviewer

自動評価はOCR/VLMの数値誤読、PDF text layerの欠落、位置・単位・重複を区別しない。表・グラフ・系統図の忠実性を判断するには、specのtargeted manual reviewが必要である。InternVLの結果は自動集計には残すが、意味的にinvalidとして解釈対象から外す。
