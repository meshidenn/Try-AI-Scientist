# Artifact Audit

## Verdict

WARN

## Checked Artifacts

- `spec.yaml`にはparent issue、固定したLightRAG/UltraDomain revision、LLM endpoint、chunk/retrieval設定、制約を記録した。
- `inputs/manifest.json`のsource revision・全source checksum・pilot snapshot checksumを確認した。
- `outputs/lightrag-store/kv_store_doc_status.json`でdocument statusが`processed`、chunk数が6であることを確認した。
- `outputs/query_results.json`には固定IDの4問すべてがあり、空response・`[no-context]` responseはない。
- `outputs/run_summary.json`と`logs/run.log`のtoken数（30,613）、query数（4）、queryのfinish reason（全`stop`）を照合した。
- `results/results.md`と`results/scores.json`の数値・単位・scopeをrun summaryと照合した。

## Blocking Issues

smoke pilotの完走を妨げる欠損はない。

## Warnings For Interpretation

- extract roleは6/6 callで`finish_reason=length`であり、69 entity・0 relationのgraphになった。relation-aware retrievalの品質を示す結果ではない。
- 4問は同一documentに紐づく。query completion率を複数documentのretrieval recallや比較性能と解釈してはいけない。
- `deterministic-hash-128-v1`は接続確認用であり、実用embedding modelではない。
- 途中で失敗した2試行は保存しているが、最終resultsの数値には含めない。

## Notes

`outputs/run_summary.json`は、run本体が完走後にsummary整形の実装バグで中断したため、保存済みlog・query結果・document statusを検証する`--recover-summary`で復元した。復元処理はquery finish reasonが全`stop`であることと、context付き4 responseを検査する。
