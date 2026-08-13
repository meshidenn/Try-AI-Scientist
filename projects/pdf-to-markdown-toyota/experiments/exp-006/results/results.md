# Results

## Summary

Gemma 4 26B MoE、Qwen 3.6 27B、GLM-4.6V-Flashの既存 `hybrid` 出力を、追加推論なしで再評価した。数値token候補に、モデル支持率（0.45）、PDF text layer存在（0.40）、支持モデルが出したMarkdown表の列数一貫性（0.15）を加えたevidence scoreを付与した。

4ページのPDF数値token被覆率は平均0.704411、候補平均confidenceは0.889264、被覆率を掛けたページ集約値は0.643828だった。

## Setup

- 対象: 有価証券報告書 p135、決算説明会資料 p8、統合報告書 p11、中期方針資料 p2
- 入力: exp-003のGemma hybrid出力、exp-004のQwen/GLM hybrid出力、exp-001のPDF snapshot
- 追加推論: なし。既存local vLLM outputだけを再利用
- 候補単位: 正規化した数値token（カンマを除去）
- confidence: `0.45 * モデル支持率 + 0.40 * PDF text layer存在 + 0.15 * 表構造妥当性`
- label: High >= 0.85、Medium >= 0.65、Low < 0.65

## Metrics

| 指標 | 定義 | 高い方がよいか |
| --- | --- | --- |
| PDF numeric coverage | PDF text layerの数値tokenのうち、少なくとも1モデルが出力した割合 | はい |
| Mean candidate confidence | 出力された数値候補のevidence score平均 | 参考値 |
| Coverage-adjusted confidence | Mean candidate confidence × PDF numeric coverage | はい。ただし確率ではない |

## Main Results

| 資料 / ページ | PDF数値token数 | 被覆率 | 候補平均confidence | 被覆率調整confidence | High / Medium / Low |
| --- | ---: | ---: | ---: | ---: | ---: |
| 有価証券報告書 p135 | 84 | 0.583333 | 0.900000 | 0.525000 | 49 / 0 / 0 |
| 決算説明会資料 p8 | 55 | 0.963636 | 0.890984 | 0.858584 | 46 / 7 / 8 |
| 統合報告書 p11 | 133 | 0.270677 | 0.787500 | 0.213158 | 18 / 18 / 0 |
| 中期方針資料 p2 | 7 | 1.000000 | 0.978571 | 0.978571 | 7 / 0 / 0 |
| **4ページ平均** | — | **0.704411** | **0.889264** | **0.643828** | **120 / 25 / 8** |

## Figures

各ページの数値候補、支持モデル、PDF根拠、confidenceをHTML review artifactに出力した。

- `outputs/confidence-review/hybrid/<document>/page-<page>.html`

## Failures And Negative Results

- 有価証券報告書 p135は候補49件がすべてHighでも、PDF数値被覆率は0.583333に留まった。High候補だけを見ると欠落を見逃すため、被覆率を必ず併記する必要がある。
- この評価は数値集合を扱うため、同じ数値が異なる表セルや列に置かれていても検知できない。表の列ずれをconfidenceの根拠にしてはならない。
- 決算説明会資料 p8では、`6.6%` と `6.6`、`2025.3` と `-2025.3` のような表記・token化差がLow/Mediumを生んだ。数値と単位、日付を分離する正規化が次段階で必要である。
- PDF text layerに存在しない画像化グラフ値は、モデルが一致してもPDF根拠0となる。図表値には画像・座標に基づく別検証が必要である。

## Reproduction

```bash
uv run python projects/pdf-to-markdown-toyota/workspace/evaluate_ensemble_confidence.py \
  --root projects/pdf-to-markdown-toyota/experiments/exp-006 \
  --model-log gemma4-26b-moe=projects/pdf-to-markdown-toyota/experiments/exp-003/logs/hybrid-run-v2.json \
  --model-log qwen3.6-27b=projects/pdf-to-markdown-toyota/experiments/exp-004/logs/qwen3.6-27b-hybrid-pilot.json \
  --model-log glm-4.6v-flash=projects/pdf-to-markdown-toyota/experiments/exp-004/logs/glm-4.6v-flash-pilot.json
```

## Notes For Reviewer

このconfidenceは未校正のevidence scoreであり、正答確率ではない。人手検証ラベルを作り、High/Medium/Lowごとの実測正答率を計測して初めて確率的なconfidenceへ校正できる。
