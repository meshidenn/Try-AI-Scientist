# Result Interpretation

## 実測から言えること

同一条件でextract roleの`max_tokens`を512、768、1024、1536へ増やすと、保存relation数は0、6、24、80件になった。1536では6 extract call中2件が`stop`で終了したため、出力上限はtruncationの程度を下げ、より多いgraph artifactを保存する要因になった。

## 実測から言えないこと

- relation数が増えたことでrelationの正確性、網羅性、またはretrieval品質が改善したこと。
- 1 document・hash embedding・4問のsmoke pilotから一般的な最適token上限を導くこと。

## 判断

1536 tokenを「truncationを許容する接続確認用」の暫定上限として使うことはできる。ただし4/6 callが`length`であるため、これを抽出完了条件や比較評価の最終設定にはしない。次は上限をさらに上げる前に、extract出力を短く完結させる設計を検証する。
