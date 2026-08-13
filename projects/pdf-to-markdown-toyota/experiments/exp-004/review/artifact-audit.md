# Artifact Audit

## Verdict

WARN

## Checked Artifacts

- `spec.yaml`: `partial_completed`。実行済みの汎用VLM候補と、未実行の専用文書パーサ候補を確認した。
- `inputs/source-manifest.json` / `inputs/pilot-pages.json`: 4資料・各1ページの入力指定を確認した。
- Qwen logs 2本: image-first / hybrid各4 recordsが`success`で、出力Markdownが非空であることを確認した。
- InternVL log: 8 recordsがHTTP上`success`だが、出力実体が反復・断片であることを確認し、`invalid_model_summaries`へ分類した。
- GLM log: 8 recordsが`success`で、出力Markdownが非空。生出力を`outputs/glm-4.6v-flash/raw/`へ保存し、box control tokenだけを正規化したことを確認した。
- `results/page_metrics.json`: 24 records、3モデル×2 methodの自動集計を確認した。
- `results/results.md`、`results/scores.json`、`results/claims.json`: GLM制御token除去後の再評価値（image-first 0.713285 / hybrid 0.717053）を反映し、metric名・方向・モデル妥当性分類・artifact参照の一致を確認した。

## Blocking Issues

なし。Qwen・GLMの4ページpilotについて、成功出力と自動評価の対応は追跡できる。InternVLは比較対象から除外する分類がartifactに明記されている。

## Warnings For Interpretation

- experiment全体は未完了であり、PaddleOCR-VL、MinerU、DeepSeek-OCR-2、dotsなど専用文書パーサは未実行である。
- `numeric_token_*` とtext proxyはPDF text layerを擬似正解とする自動指標で、位置・接続関係・表の意味的正確性は測定しない。
- Qwenの統合報告書p.11は、初回32,768-token超過とvLLM multimodal cache HTTP 500を経て、payloadを18,000文字に制限しコンテナ再起動後に成功した。全hybridページが厳密に同一payload制約ではない。
- max_new_tokens=1,024はspec通常条件4,096と異なる。停止理由を保存していないため、上限で打ち切られた出力があるかは判定できない。
- table_row_width_consistencyは有効モデルで0/4。表についての肯定的主張は不可。
- targeted manual reviewは未実施。
- GLMのraw outputから制御tokenを除去した後処理は、文字内容を追加・削除していないが、モデル生出力そのものと最終Markdownを分けて扱う必要がある。

## Notes

共有実行器はlocalhost以外のendpointを拒否し、各run logのbackendは`local_vllm_openai`である。外部推論APIの使用を示すartifactは確認されなかった。
