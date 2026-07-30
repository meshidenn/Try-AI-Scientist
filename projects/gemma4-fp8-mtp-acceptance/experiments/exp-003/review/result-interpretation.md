# Result Interpretation

## Conclusion

今回のlong-IO random factorialでは、FP8 slowdownは安定して再現しなかった。36対応cell中、FP8がBF16より遅かったのは`input=1024, output=2048, concurrency=2, spec=8`の1件だけで、差は-0.8%だった。全体の幾何平均ではFP8がBF16比1.447xだった。

## Concurrency Versus Spec Tokens

絶対output throughputへの影響はconcurrencyが明確に大きい。marginal max/min rangeはBF16でconcurrency 2.713xに対してspec tokens 1.439x、FP8で2.699xに対して1.323xだった。両precisionとも平均的にはspec=4が最速で、concurrency=8が最速だった。

FP8/BF16比を変える要因としても、concurrencyのmarginal range 1.148xがspec tokensの1.088xを上回った。ただしconcurrency効果は単調ではなく、c1/c8でFP8優位が大きく、c2/c4で小さい。さらに二要因のadditive modelから最大1.402xのinteraction residualがあり、どちらか一方だけでは個別cellを説明できない。

## Acceptance

唯一のFP8低速cellではacceptanceがBF16 48.5%からFP8 28.7%へ低下しており、低acceptanceが局所的なslowdownに寄与した可能性はある。しかし、acceptanceが低い別cellでもFP8のkernel・memory利得が上回っている。したがって「FP8ではacceptanceが下がるため一般に遅い」は支持されない。

## Relation To Earlier Results

旧random high-spec測定は主に2 promptで、今回の16 prompt測定と値が大きく異なる。今回の方がworkload平均としては強いが、1 runのみなので小さい差を安定効果とは扱わない。agentic syntheticではs16/c1の-23.8% slowdownが残っており、random token長だけでなくprompt構造、出力分布、低concurrency時のtarget/drafter mismatchが候補である。

## Operational Implication

このrandom workloadだけならFP8 + spec=4がthroughputの保守的な選択である。ただし職場agentのslowdownを解消する設定は、実traceかtool-callを含む再現workloadで選ぶ必要がある。固定s16はacceptance低下時の罰が大きいため、現時点ではdefaultにしない。
