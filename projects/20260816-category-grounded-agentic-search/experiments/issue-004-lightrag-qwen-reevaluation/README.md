# Issue #4: Qwen LightRAG再評価

GitHub Issue #4に属する実験artifactの索引である。`experiments/<exp-id>/`というprojectの標準配置を維持するため、実験本体はこのディレクトリへ移動せず、各experimentの`parent_issue: 4`と本索引で関連を明示する。

## 実験の流れ

| 段階 | 実験 | 内容 |
| --- | --- | --- |
| 小規模疎通 | [exp-007](../exp-007/) ～ [exp-016](../exp-016/) | Qwen endpoint、token上限、query生成、judge経路の実装確認。 |
| 反復・length対策 | [exp-017](../exp-017/) ～ [exp-032](../exp-032/) | extract出力長、JSON抽出、重複禁止、反復検出、repetition penaltyを検証。 |
| 全量triplet抽出 | [exp-033](../exp-033/) | UltraDomain Mixの61 unique contextをQwenで処理し、triplet artifactを確定。 |
| BGE-M3 index | [exp-034](../exp-034/) | 全量tripletからBGE-M3 embeddingとLightRAG indexを作成。 |
| Qwen評価pilot | [exp-035](../exp-035/) | 固定5問でhybrid/naiveを比較し、Prometheus-2とgpt-oss-20bでjudge。 |

## 生成dataの扱い

`contexts.jsonl`、triplet JSONL、embedding、index、LightRAG storeは再生成可能な大型dataである。Gitには投入せず、取得元datasetのrevision・URL・SHA-256、生成設定、artifact hashを各manifestへ記録する。共有のtriplet/indexについては`data/derived/`のmanifestを正本とする。
