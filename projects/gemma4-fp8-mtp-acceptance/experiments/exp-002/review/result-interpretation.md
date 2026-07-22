# Result Interpretation

agent trace風workloadでは、FP8 slowdownを`spec_tokens=16, concurrency=1`で再現した。FP8 throughputはBF16比0.762xで、acceptance rateは85.24%から47.99%へ低下した。

ただし、この結果は「FP8はMTPで一般に遅い」ことを意味しない。同じFP8 targetでもs8は全concurrencyで最速で、s16もconcurrency 2/4ではBF16より速かった。したがって問題はFP8単体ではなく、target/drafter mismatch、draft depth、低concurrencyを組み合わせた過剰投機と解釈するのが妥当である。

実運用の第一候補はFP8で`spec_tokens=8`、または短いstructured outputではs4以下へ動的に落とすpolicyである。実traceで再検証するまでは固定s16を推奨しない。
