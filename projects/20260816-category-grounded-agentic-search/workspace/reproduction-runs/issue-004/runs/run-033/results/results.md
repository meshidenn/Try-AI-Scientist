# Results

## Summary

UltraDomainの全61 unique contextに対するQwen JSONトリプル抽出は完了した。全61文書が`processed`であり、non-stop終了・失敗文書はいずれも0件だった。正本triplet artifactを61行でexportした。

## Setup

- Dataset: UltraDomain unique contexts（revision `aa8a51d523f8fc3c5a0ab90dd16b7f6b9dbb5d0d`）
- Extractor: `Qwen/Qwen3.6-35B-A3B-FP8`（served model `llm`）
- Format: LightRAG JSON extraction
- Extract maximum: 32,768 tokens
- Repetition penalty: 1.05
- Chunking: 512 tokens、overlap 64 tokens
- Gleaning: 0

## Metrics

- Documents: 61 / 61 processed
- Chunks: 1,375
- LLM calls: 1,567
- Prompt tokens: 3,526,429
- Completion tokens: 3,219,285
- Total tokens: 6,745,714
- Aggregated entities: 22,114
- Aggregated relations: 24,032
- Non-stop finish reasons: 0
- Failed documents: 0
- Repetition warning events: 782

## Main Results

`data/derived/triplets/UltraDomain--aa8a51d523f8fc3c5a0ab90dd16b7f6b9dbb5d0d/Qwen--Qwen3.6-35B-A3B-FP8/triplets.jsonl`を全量tripletの正本として確定した。SHA-256は`6a5f7eaab019fe8a0c68ed0c89f80c27d5caba8418c11e665a6abd1a11b7d059`である。

## Figures

図は作成していない。

## Failures And Negative Results

失敗文書とnon-stop終了はなかった。反復検出は782件あったが、すべて`finish_reason=stop`かつ非空出力であり、事前に定めた判断に従って抽出を継続した。これは出力の意味的重複がないことを保証する指標ではない。

## Reproduction

`README.md`のコマンドでLightRAG storeを作り、`interfaces.derived_artifacts`で`triplets.jsonl`をexportする。入力manifest、実行ログ、store snapshotはこの実験ディレクトリに保存されている。

## Notes For Reviewer

entity/relationの30/50上限は各抽出応答に対する制約であり、上記のentity/relation集計は文書内チャンクを統合した合計である。そのため、文書単位の値は上限を超えうる。
