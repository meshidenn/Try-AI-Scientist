# Artifact Audit

## Verdict

PASS

## Checked Artifacts

- `spec.yaml`はcompletedであり、対象61文書と設定を記録している。
- `inputs/manifest.json`と`inputs/contexts.jsonl`が存在する。
- `outputs/index_summary.json`はcompletedで、61文書すべてが`processed`、non-stop終了が0件である。
- LightRAG storeにdocument status、chunk、entity、relation、graphの各artifactが存在する。
- `results/results.md`と`results/scores.json`は実測値とtriplet artifactのhashを記録している。
- `triplets.jsonl`は61行で、manifestのprocessed_document_count=61およびSHA-256と一致する。
- 実行ログと反復警告ログが存在する。

## Blocking Issues

なし。

## Warnings For Interpretation

- 782件の反復警告は、行単位の一意率による診断である。全件が`stop`終了であり抽出失敗ではないが、意味的な重複除去の品質指標ではない。
- entity/relation数はチャンク統合後の文書単位集計であり、各抽出応答の30/50上限と直接比較してはならない。
- このrunの内部vector storeはhash embeddingであり、BGE-M3 embedding/indexは本実験後の別stageで作成する。

## Notes

再利用可能なtriplet artifactの正本は`data/derived/triplets/`に確定した。embedding/index stageはmanifest上で未開始として分離されている。
