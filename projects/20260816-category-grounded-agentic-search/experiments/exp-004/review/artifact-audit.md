# Artifact Audit

## Verdict

WARN

## Checked Artifacts

- `spec.yaml`で比較条件と変更要因を確認した。
- `inputs/manifest.json`の入力snapshotを確認した。
- `outputs/lightrag-store/kv_store_doc_status.json`で1 documentが`processed`、chunk数が6であることを確認した。
- `outputs/query_results.json`に4問のcontext付きresponseがあり、query finish reasonが全`stop`であることを確認した。
- `outputs/run_summary.json`、`logs/run.log`、`results/scores.json`でtotal token 35,858、LLM latency 145.876 s、extract `length` 6/6、115 entity・24 relationを照合した。

## Blocking Issues

smoke pilotの完走を妨げる欠損はない。

## Warnings For Interpretation

- extractが6/6 callで`length`のため、保存relationは完全な抽出結果ではない。
- 1 documentのsmoke pilotであり、query完走をretrieval recallや比較性能と解釈してはいけない。
- hash embeddingは接続確認用である。
