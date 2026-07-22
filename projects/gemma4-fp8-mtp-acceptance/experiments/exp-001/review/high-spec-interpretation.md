# High Spec Interpretation

FP8では`spec_tokens=16`が`spec_tokens=8`より10/10 workloadで遅かった。throughput比は0.60x〜0.94xで、s16はacceptance低下と追加verification costを回収できなかった。

BF16でもs16は8/10で遅く、s16問題はFP8固有ではない。ただしagent replayのs16/c1ではFP8 acceptanceがBF16より大きく崩れ、FP8が23.75%遅くなった。したがってFP8はs16過剰投機の影響を受けやすい条件がある。

現時点の実用的defaultはFP8+s8。短いstructured generationではs4以下も候補で、固定s16は避ける。
