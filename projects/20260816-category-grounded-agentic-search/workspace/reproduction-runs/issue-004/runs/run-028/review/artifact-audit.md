# Artifact Audit

## Verdict

PASS

## Checked Artifacts

- `spec.yaml`、`README.md`、`inputs/manifest.json`、`inputs/contexts.jsonl`
- `outputs/index_summary.json`、`outputs/lightrag-store/kv_store_doc_status.json`
- `outputs/lightrag-store/graph_chunk_entity_relation.graphml`
- `logs/repetition_warnings.jsonl`、`results/results.md`、`results/scores.json`

## Blocking Issues

なし。対象documentは `processed`、全抽出completionは `stop` であり、KG artifactが存在する。

## Warnings For Interpretation

- 反復警告は全11抽出completionで発生している。これは診断値であり、抽出完了性の失敗ではない。
- embeddingはhashであり、正式なBGE-M3 indexや検索精度を示さない。

## Notes

入力snapshotのchecksum、LLM completion統計、KGのentity/relation件数を確認した。
