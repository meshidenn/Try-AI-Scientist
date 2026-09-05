# Artifact Audit

## Verdict

PASS

## Checked Artifacts

- `spec.yaml`で比較条件と変更要因を確認した。
- `inputs/manifest.json`でexp-002から継続する入力snapshotを確認した。
- `outputs/lightrag-store/kv_store_doc_status.json`で1 documentが`processed`、chunk数が6であることを確認した。
- `outputs/run_summary.json`のextract 6 callがすべて`stop`、queryの非`stop` finishが0であることを確認した。
- `outputs/lightrag-store/kv_store_full_entities.json`と`kv_store_full_relations.json`で101 entity・99 relationを確認した。
- `results/results.md`と`results/scores.json`でtotal token 42,817、LLM latency 246.893 s、extract `stop` 6/6をrun summaryと照合した。

## Blocking Issues

ない。

## Warnings For Interpretation

- `logs/run.log`には、成功run前に実行セッションが途切れたpartial attemptの1 extract callも含まれる。成功runの定量値は`outputs/run_summary.json`を正本とし、partial outputは別directoryに退避済みである。
- 1 documentのsmoke pilotであり、relation数やquery完走をretrieval recall・relation品質・比較性能と解釈してはいけない。
- hash embeddingは接続確認用である。

## Notes

`status=completed`は、specに定義したextract 6/6 `stop`、index完走、4 query完走を満たすことを表す。
