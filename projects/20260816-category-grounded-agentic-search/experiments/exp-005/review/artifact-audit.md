# Artifact Audit

## Verdict

WARN

## Checked Artifacts

- `spec.yaml`で比較条件と変更要因を確認した。
- `inputs/manifest.json`の入力snapshotを確認した。
- `outputs/lightrag-store/kv_store_doc_status.json`で1 documentが`processed`、chunk数が6であることを確認した。
- `outputs/query_results.json`に4問のcontext付きresponseがあり、query finish reasonが全`stop`であることを確認した。
- `outputs/run_summary.json`、`logs/run.log`、`results/scores.json`でtotal token 41,629、LLM latency 194.321 s、extract `stop` 2/6・`length` 4/6、116 entity・80 relationを照合した。

## Blocking Issues

smoke pilotの完走を妨げる欠損はない。

## Warnings For Interpretation

- extractの4/6 callが`length`のため、保存relationは完全な抽出結果ではない。
- relation数の増加はrelationの正確性やretrieval品質を示さない。
- 1 documentのsmoke pilotであり、query完走をretrieval recallや比較性能と解釈してはいけない。
- hash embeddingは接続確認用である。
