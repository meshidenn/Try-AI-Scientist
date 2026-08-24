# Next Plan

## 次に検証する変更

extract promptに、entity/relation数の上限、簡潔なrelation description、終端delimiterの明示を追加し、`max_tokens=1536`で6/6 callが`stop`となるかを確認する。

## 成功判定

- 同一6 chunkでextract `stop`が6/6である。
- indexと4件のhybrid queryが完走する。
- relation数だけでなく、抽出relationを少数サンプルで人手確認できるartifactを保存する。

## 保留事項

上限を2048以上へ増やす試行は、上記の出力制約後にも`length`が残る場合に限定する。上限増加だけでは1536で解消していないためである。
