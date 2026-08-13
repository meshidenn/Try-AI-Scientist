# Results

## Summary

exp-010のblock-aware評価をさらに修正し、PDFの`get_text("dict")`から抽出した座標付きtext line内だけでn-gramを生成した。これにより、同じPDF blockに含まれていても別line・別列にある文字列の連接を評価対象外にした。数字tokenと数字を跨ぐn-gramも除外している。

対象は3モデル共通の4ページ、計12件。全体の出力側一致率は n=1 の **0.962921** から n=10 の **0.641699**、PDF側回収率は n=1 の **0.900721** から n=10 の **0.778472** となった。

## Setup

- 対象: 有価証券報告書 p135、決算説明会資料 p8、統合報告書 p11、中期方針資料 p2
- モデル: Gemma 4 26B MoE、Qwen 3.6 27B、GLM-4.6V-Flash
- 出力: 既存の`hybrid` Markdown。追加推論なし
- PDF単位: PyMuPDF `get_text("dict")` の各text line
- 出力単位: Markdownの行・表セル
- 数値: NFKC後の数値tokenと、数値tokenを跨ぐn-gramを除外
- n-gram: 各line/unit内のユニーク文字n-gram集合。line/unit間・ページ間を跨がない

## Metrics

| 指標 | 定義 |
| --- | --- |
| `out` | 出力unitの非数値n-gramのうち、同じPDFページのいずれかのtext line内に存在する割合 |
| `cov` | PDF text line内の非数値n-gramのうち、出力unitにも存在する割合 |
| `F1` | `out`と`cov`の調和平均 |

## Main Results

| n | 出力側一致率 | PDF側回収率 | F1 |
|---:|---:|---:|---:|
| 1 | 0.962921 | 0.900721 | 0.919815 |
| 2 | 0.923920 | 0.869226 | 0.874599 |
| 3 | 0.898052 | 0.841523 | 0.839440 |
| 4 | 0.874829 | 0.829466 | 0.819589 |
| 5 | 0.846271 | 0.822127 | 0.800876 |
| 6 | 0.810739 | 0.815414 | 0.778123 |
| 7 | 0.771117 | 0.806095 | 0.752139 |
| 8 | 0.729157 | 0.797030 | 0.724821 |
| 9 | 0.679235 | 0.783529 | 0.687427 |
| 10 | 0.641699 | 0.778472 | 0.659571 |

## Model Results

| Model | n=1 out | n=10 out | n=1 cov | n=10 cov | n=10 F1 |
|---|---:|---:|---:|---:|---:|
| Gemma 4 | 0.913129 | 0.617143 | 0.907869 | 0.761979 | 0.644796 |
| Qwen 3.6 | 0.984615 | 0.649604 | 0.929334 | 0.793924 | 0.691042 |
| GLM-4.6V | 0.991017 | 0.658350 | 0.864959 | 0.779514 | 0.642874 |

全nのモデル別値は `results/page_ngrams.json` の `summary.by_model` に保存している。

## Column-boundary Check

決算説明会資料 p8では、PyMuPDFのblock 13に「日本」「北米」「欧州」などが含まれるが、`get_text("dict")`では以下の別lineとして抽出される。

```text
日本
北米
欧州
```

したがって、「日本北米」「北米欧州」のような列間連接n-gramは評価対象にならない。

## HTML Review

`outputs/ngram-match-html/<model>/<document>/page-<page>.html` に12件のHTMLを生成した。n=1〜10を切り替え、text line内で一致した出力を緑、不一致を赤、PDF側の漏れを赤、数字を灰色（評価対象外）で表示する。

## Reproduction

```bash
PYTHONPATH=projects/pdf-to-markdown-toyota/workspace uv run python projects/pdf-to-markdown-toyota/workspace/evaluate_line_aware_page_ngrams.py \
  --root projects/pdf-to-markdown-toyota/experiments/exp-011 \
  --model-log gemma4-26b-moe=projects/pdf-to-markdown-toyota/experiments/exp-003/logs/hybrid-run-v2.json \
  --model-log qwen3.6-27b=projects/pdf-to-markdown-toyota/experiments/exp-004/logs/qwen3.6-27b-hybrid-pilot.json \
  --model-log glm-4.6v-flash=projects/pdf-to-markdown-toyota/experiments/exp-004/logs/glm-4.6v-flash-pilot.json

PYTHONPATH=projects/pdf-to-markdown-toyota/workspace uv run python projects/pdf-to-markdown-toyota/workspace/render_line_aware_ngram_html.py --root projects/pdf-to-markdown-toyota/experiments/exp-011
```

## Notes For Reviewer

exp-009とexp-010は旧定義の結果として保持し、本exp-011をline-aware・numeric-excludedの採用結果とする。
