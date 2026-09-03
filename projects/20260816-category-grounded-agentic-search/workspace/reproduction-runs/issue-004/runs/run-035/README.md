# exp-035: BGE-M3全量indexのQwen再評価pilot

exp-033の全量tripletとexp-034のBGE-M3 indexを再利用する。Qwen抽出は再実行せず、固定済みの5問に対してLightRAG hybrid/naiveの回答生成とPrometheus-2およびgpt-oss-20bによるpairwise judgeを行う。

このpilotは、全量indexのquery疎通と相対的な回答品質比較を対象とする。UltraDomain入力に独立したgold evidenceがないため、検索Recallや正解率は報告しない。

## 結果

5問すべてでhybrid/naiveの回答生成と両judgeの判定を完了した。Prometheus-2、gpt-oss-20bともに相対勝率はhybrid 60%（3/5）、naive 40%（2/5）で、全5問の勝者が一致した。
