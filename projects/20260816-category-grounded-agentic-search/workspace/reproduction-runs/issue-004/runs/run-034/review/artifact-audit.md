# Artifact Audit

## Verdict

PASS

## Checked Artifacts

- `spec.yaml`はcompletedで、入力triplet hash、BGE-M3、CUDA、1,024次元の設定を記録している。
- `results/results.md`と`results/scores.json`は61文書および45,525 vectorの実測値を記録している。
- index manifestはsource LightRAG store、input triplets path/hash、BGE-M3、各vector store件数を記録している。
- chunk/entity/relationship vector storeはすべて1,024次元で、source storeとそれぞれ1,375 / 20,281 / 23,869件が一致する。
- graph、status、full docs/entities/relations、text chunksがsource storeとbyte単位で一致する。
- destination document statusは61件すべて`processed`である。

## Blocking Issues

なし。

## Warnings For Interpretation

- 初回の標準出力転送はログディレクトリが未作成だったため保存できなかった。実行結果はindex manifest、vector storeの内容、監査時の件数照合で確認しており、以後の重要値は`logs/index.log`に固定している。
- この監査はindex artifactの整合性を対象とする。検索・回答精度は未評価である。

## Notes

source storeのQwen抽出結果は変更していない。BGE-M3 embedding/indexは`data/derived/indexes/`に分離して保存している。
