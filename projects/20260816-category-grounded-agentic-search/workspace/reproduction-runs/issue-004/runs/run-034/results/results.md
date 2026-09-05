# Results

## Summary

exp-033で確定した全61文書のLightRAG graph/chunk/tripletを入力に、Qwen抽出を再実行せず、home-serverのRTX 3090でBGE-M3 vector indexを構築した。3種すべてのvector storeを1,024次元で作成し、入力storeとの件数一致を検証した。

## Setup

- Input triplets: exp-033の`triplets.jsonl`（SHA-256 `6a5f7eaab019fe8a0c68ed0c89f80c27d5caba8418c11e665a6abd1a11b7d059`）
- Source graph/chunk store: `workspace/reproduction-runs/issue-004/runs/run-033/outputs/lightrag-store`
- Embedding model: `BAAI/bge-m3`
- Device: NVIDIA GeForce RTX 3090（CUDA）
- Vector dimension: 1,024
- Batch size: 32
- Vector storage: LightRAG NanoVectorDB

## Metrics

- Processed documents: 61
- Chunk vectors: 1,375
- Entity vectors: 20,281
- Relationship vectors: 23,869
- Total vectors: 45,525
- Embedding failures: 0

## Main Results

正本indexは`data/derived/indexes/UltraDomain--aa8a51d523f8fc3c5a0ab90dd16b7f6b9dbb5d0d/Qwen--Qwen3.6-35B-A3B-FP8__BAAI--bge-m3/lightrag-store/`に保存した。graph、document status、full docs/entities/relations、text chunksはsource storeとbyte単位で一致する。vector storeだけをBGE-M3で置換している。

## Figures

図は作成していない。

## Failures And Negative Results

embedding失敗はなかった。初回の標準出力保存はログディレクトリ未作成のため失敗したが、構築プロセスは継続して完了し、重要な設定・件数・入力hashは`logs/index.log`、index manifest、vector storeに記録した。

## Reproduction

`uv run python -m category_grounded_agentic_search.interfaces.bge_m3_index --help`を参照し、source store、triplet JSONL、derived rootを指定して実行する。

## Notes For Reviewer

本stageは抽出済みのgraph/chunk/entity/relationをcopyし、vector storeのみ再構築する。Qwen endpointには接続していない。
