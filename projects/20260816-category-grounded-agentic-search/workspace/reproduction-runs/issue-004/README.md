# Issue #4: LightRAG再現実装のrun記録

ここはIssue #4の**再現実装に伴う試行錯誤**を残す領域であり、正式な研究experimentではない。設定、結果要約、判断はGitで追跡する。一方で、再生成できるraw completion、context snapshot、embedding、index、LightRAG storeはローカルに保持し、manifestで再現可能にする。

正式な精度評価は、独立した仮説・比較・評価指標・成功判定を定義してから`experiments/exp-xxx/`に作成する。UltraDomain Mix全125問の再現性評価はIssue #12で別experimentとして実施する。

## Runの流れ

| 段階 | Run | 内容 |
| --- | --- | --- |
| 小規模疎通 | `run-007`〜`run-016` | Qwen endpoint、token上限、query生成、judge経路の実装確認。 |
| 反復・length対策 | `run-017`〜`run-032` | extract出力長、JSON抽出、重複禁止、反復検出、repetition penaltyを検証。 |
| 全量triplet抽出 | `run-033` | UltraDomain Mixの61 unique contextをQwenで処理し、triplet artifactを確定。 |
| BGE-M3 index | `run-034` | 全量tripletからBGE-M3 embeddingとLightRAG indexを作成。 |
| 評価経路の疎通 | `run-035` | 固定5問でhybrid/naiveとjudge経路を実装確認。精度の主張には使わない。 |

## 移行対応

以下のrunは過去に`experiments/exp-xxx/`へ誤って配置されていた。Gitから除外せず、履歴を保つrenameとして移した。各run内部の`experiment_id: exp-xxx`は当時の記録を改変しないためのlegacy識別子である。

| 旧path | 新path |
| --- | --- |
| `experiments/exp-007`〜`experiments/exp-035` | `workspace/reproduction-runs/issue-004/runs/run-007`〜`run-035` |

共有triplet/indexの正本は`data/derived/`のmanifestであり、同manifestのLightRAG store参照は`run-033`へ更新済みである。
