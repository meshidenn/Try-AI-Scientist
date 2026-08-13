# Results

## Summary

同一のGemma 4、Qwen 3.6、GLM-4.6Vの既存hybrid出力について、数値tokenとテキスト候補を別々にアンサンブル評価した。テキスト候補は本文行、見出し、Markdown表内の非数値セルである。追加推論は行っていない。

数値はPDF数値token被覆率0.704411、被覆率調整confidence 0.643828だった。テキストはPDF text-unit被覆率proxy 0.710165、被覆率調整confidence 0.502155だった。テキストの方がモデル間の表現・構造の揺れが大きい。

## Setup

- 対象: 有価証券報告書 p135、決算説明会資料 p8、統合報告書 p11、中期方針資料 p2
- モデル: Gemma 4 26B MoE、Qwen 3.6 27B、GLM-4.6V-Flash
- 入力: exp-003のGemma hybrid出力、exp-004のQwen/GLM hybrid出力
- 追加推論: なし。exp-007のGemma chunk出力は条件不一致のため使わない
- 数値confidence: `0.45 * モデル支持率 + 0.40 * PDF数値token存在 + 0.15 * 支持モデルの表列数一貫性`
- テキストconfidence: `0.55 * モデル支持率 + 0.45 * PDF text layerへの正規化文字列包含`

## Metrics

| 指標 | 定義 | 注意 |
| --- | --- | --- |
| Numeric PDF coverage | PDF数値tokenのうち、少なくとも1モデルが出力した割合 | 位置・列は見ない |
| Numeric coverage-adjusted confidence | 数値候補平均confidence × Numeric PDF coverage | 確率ではない |
| Text PDF unit coverage proxy | PDF text block相当の本文unitに、出力候補が文字列類似で対応した割合 | 意味的類似ではない |
| Text coverage-adjusted confidence | テキスト候補平均confidence × Text coverage proxy | 確率ではない |

## Main Results

| 資料 / ページ | 数値被覆率 | 数値調整confidence | テキスト被覆率proxy | テキスト調整confidence | テキスト High / Medium / Low |
| --- | ---: | ---: | ---: | ---: | ---: |
| 有価証券報告書 p135 | 0.583333 | 0.525000 | 0.500000 | 0.451190 | 21 / 4 / 3 |
| 決算説明会資料 p8 | 0.963636 | 0.858584 | 1.000000 | 0.374285 | 2 / 1 / 32 |
| 統合報告書 p11 | 0.270677 | 0.213158 | 0.340659 | 0.183145 | 8 / 4 / 58 |
| 中期方針資料 p2 | 1.000000 | 0.978571 | 1.000000 | 1.000000 | 6 / 0 / 0 |
| **4ページ平均** | **0.704411** | **0.643828** | **0.710165** | **0.502155** | **37 / 9 / 93** |

## Figures

- `outputs/confidence-review/hybrid/<document>/page-<page>.html`: 数値候補のreview
- `outputs/text-confidence-review/hybrid/<document>/page-<page>.html`: テキスト候補のreview
- `outputs/colorized-model-output/<model>/hybrid/<document>/page-<page>.html`: 各モデルの**実際のMarkdown出力**をHTML表示し、High（緑）/ Medium（黄）/ Low（赤）のevidence scoreを重ねたもの。4資料×3モデルの計12件。
- `results/colorized_html_manifest.json`: 上記12件の元MarkdownとHTMLの対応表。

## Failures And Negative Results

- テキストconfidenceは文字列根拠だけであり、言い換え、分割・結合、図中文字、系統図の関係を正解として統合できない。
- 決算説明会資料p8はtext coverage proxy 1.0でもLow候補32件である。グラフ説明をモデルごとに異なる粒度へ構造化するため、coverageだけでは合意度を表せない。
- 統合報告書p11はtext coverage proxy 0.340659、Low候補58件である。複合レイアウト・図の内容はこの文字列方式では不十分である。
- 有報p135の数値/テキスト評価は旧来の1024 token一括出力に基づく。exp-007の座標chunk Gemma結果を混在させていない。
- 数値tokenが一致しても表セル・列対応は保証しない。

## Reproduction

```bash
uv run python projects/pdf-to-markdown-toyota/workspace/evaluate_ensemble_confidence.py --root projects/pdf-to-markdown-toyota/experiments/exp-008 --model-log gemma4-26b-moe=projects/pdf-to-markdown-toyota/experiments/exp-003/logs/hybrid-run-v2.json --model-log qwen3.6-27b=projects/pdf-to-markdown-toyota/experiments/exp-004/logs/qwen3.6-27b-hybrid-pilot.json --model-log glm-4.6v-flash=projects/pdf-to-markdown-toyota/experiments/exp-004/logs/glm-4.6v-flash-pilot.json

PYTHONPATH=projects/pdf-to-markdown-toyota/workspace uv run python projects/pdf-to-markdown-toyota/workspace/evaluate_ensemble_text_confidence.py --root projects/pdf-to-markdown-toyota/experiments/exp-008 --model-log gemma4-26b-moe=projects/pdf-to-markdown-toyota/experiments/exp-003/logs/hybrid-run-v2.json --model-log qwen3.6-27b=projects/pdf-to-markdown-toyota/experiments/exp-004/logs/qwen3.6-27b-hybrid-pilot.json --model-log glm-4.6v-flash=projects/pdf-to-markdown-toyota/experiments/exp-004/logs/glm-4.6v-flash-pilot.json

PYTHONPATH=projects/pdf-to-markdown-toyota/workspace uv run python projects/pdf-to-markdown-toyota/workspace/render_confidence_colored_html.py --root projects/pdf-to-markdown-toyota/experiments/exp-008
```

## Notes For Reviewer

数値・テキストのconfidenceは未校正のevidence scoreである。High/Medium/Lowを正答確率にするには、同じ候補単位で人手正解ラベルを付与し、実測正答率へ校正する必要がある。
