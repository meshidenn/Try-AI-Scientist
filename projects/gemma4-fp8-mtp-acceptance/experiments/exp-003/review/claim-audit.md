# Claim Audit

## Verdict

PASS with scope limitation.

72 successful runs、36対応比較、FP8 slowdownが1件だけだったこと、marginal factor rangeはraw benchmark JSONと集約JSONで直接確認した。

「絶対throughputではconcurrencyの影響がspec-tokenより大きい」は今回の3 workload、4 concurrency、3 spec depthに限定して支持される。run反復がないため統計的有意差は主張しない。

この実験だけから職場agent slowdownの原因を特定するclaimは支持されない。実trace、tool-call、arrival timing、prefix reuseが含まれていないためである。
