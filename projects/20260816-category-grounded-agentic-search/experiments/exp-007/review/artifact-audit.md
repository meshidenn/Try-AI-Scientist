# Artifact Audit

## Verdict

WARN

## Checked Artifacts

- `inputs/manifest.json`はUltraDomain Mix revision、61文書のhash、質問生成条件を記録している。
- `inputs/generated_queries.json`は125問で、manifestのSHA-256と一致する。
- `outputs/lightrag_hybrid_results.json`と`outputs/lightrag_naive_results.json`は各125回答を持つ。
- `outputs/gpt_4o_mini_judge_results.json`は125組すべてを判定し、勝数はhybrid 50、naive 58、Tie 17である。初回BatchのJSON未完了6件は同じmodel・temperatureで再判定済みであり、最終解析失敗は0件である。
- `outputs/gpt_oss_20b_low_reasoning_2048_judge_results.json`は125組すべてを判定し、勝数はhybrid 60、naive 65である。
- `outputs/prometheus_7b_v2_1024_judge_results.json`は125組すべてを判定し、勝数はhybrid 65、naive 60である。
- `outputs/gpt_oss_120b_low_reasoning_2048_judge_results.json`は125組すべてを判定し、勝数はhybrid 52、naive 73である。
- `results/scores.json`の勝数・勝率はjudge出力と一致する。

## Blocking Issues

なし。GPT-4o-miniを含む125組の集計artifactは完備している。

## Warnings For Interpretation

- GPT-4o-miniの初回Batchは6件がJSON未完了となったため、max tokens 1,024の再試行で回復した。主結果は再試行を含む125組の集計である。
- 三つの代替judgeでhybrid勝率は41.6%から52.0%まで変動しており、主評価のGPT-4o-miniは40.0%である。judge間で頑健な優劣は確認できない。
- 参照回答・gold evidenceは論文プロトコル上用いないため、このwin rateは正解率ではない。
- Qwen回答生成の診断ログには`finish_reason=length`が5回あり、run summaryにも5件のnon-stop finish reasonが記録されている。回答JSONが125件ずつ存在することは確認したが、影響範囲の追加確認が必要である。

## Notes

raw answer、judge応答、checkpoint、indexは再生成可能なためGit管理対象外とし、入力hash・集計値・監査結果を追跡する。
