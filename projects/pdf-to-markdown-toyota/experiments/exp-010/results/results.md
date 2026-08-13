# Results

## Summary

exp-009の評価定義を修正し、PDF text block境界を跨ぐn-gramと数値tokenを評価対象から除外して再計算した。対象は3モデル共通の4ページ、計12件である。

全体の出力側一致率は n=1 の **0.964265** から n=10 の **0.845269**、PDF側回収率は n=1 の **0.902065** から n=10 の **0.695446** となった。

## Setup

- 対象: 有価証券報告書 p135、決算説明会資料 p8、統合報告書 p11、中期方針資料 p2
- モデル: Gemma 4 26B MoE、Qwen 3.6 27B、GLM-4.6V-Flash
- 出力: 既存の`hybrid` Markdown。追加推論なし
- PDF単位: PyMuPDF `get_text("blocks")` の各text block
- 出力単位: Markdownの行・表セル
- 数値: NFKC後の数値tokenと、数値tokenを跨ぐn-gramを除外
- n-gram: 各単位内のユニーク文字n-gram集合。単位間・ページ間を跨がない

## Metrics

| 指標 | 定義 |
| --- | --- |
| `out` | 出力unitの非数値n-gramのうち、同じPDFページのいずれかのtext block内に存在する割合 |
| `cov` | PDF text block内の非数値n-gramのうち、出力unitにも存在する割合 |
| `F1` | `out`と`cov`の調和平均 |

## Main Results

| n | 出力側一致率 | PDF側回収率 | F1 |
|---:|---:|---:|---:|
| 1 | 0.964265 | 0.902065 | 0.921159 |
| 2 | 0.947076 | 0.834980 | 0.869212 |
| 3 | 0.932665 | 0.790996 | 0.830395 |
| 4 | 0.924098 | 0.763818 | 0.808301 |
| 5 | 0.914188 | 0.745371 | 0.790673 |
| 6 | 0.901417 | 0.730622 | 0.774252 |
| 7 | 0.887195 | 0.720787 | 0.760453 |
| 8 | 0.874292 | 0.708980 | 0.745308 |
| 9 | 0.860353 | 0.697758 | 0.729361 |
| 10 | 0.845269 | 0.695446 | 0.719995 |

## Model Results

| Model | n=1 out | n=10 out | n=1 cov | n=10 cov | n=10 F1 |
|---|---:|---:|---:|---:|---:|
| Gemma 4 | 0.913129 | 0.813292 | 0.907869 | 0.668103 | 0.677928 |
| Qwen 3.6 | 0.984615 | 0.889709 | 0.929334 | 0.729590 | 0.779203 |
| GLM-4.6V | 0.995050 | 0.832806 | 0.868991 | 0.688645 | 0.702853 |

n=10のF1ではQwenが最も高く、出力側一致率ではQwenがGLMを上回る。全nのモデル別値は `results/page_ngrams.json` の `summary.by_model` に保存している。

## HTML Review

`outputs/ngram-match-html/<model>/<document>/page-<page>.html` に12件のHTMLを生成した。HTMLではn=1〜10を切り替え、PDF text block内で一致した出力を緑、不一致を赤、PDF側の漏れを赤、数字を灰色（評価対象外）で表示する。漏れn-gramは一覧にも掲載する。

## Reproduction

```bash
PYTHONPATH=projects/pdf-to-markdown-toyota/workspace uv run python projects/pdf-to-markdown-toyota/workspace/evaluate_box_aware_page_ngrams.py \
  --root projects/pdf-to-markdown-toyota/experiments/exp-010 \
  --model-log gemma4-26b-moe=projects/pdf-to-markdown-toyota/experiments/exp-003/logs/hybrid-run-v2.json \
  --model-log qwen3.6-27b=projects/pdf-to-markdown-toyota/experiments/exp-004/logs/qwen3.6-27b-hybrid-pilot.json \
  --model-log glm-4.6v-flash=projects/pdf-to-markdown-toyota/experiments/exp-004/logs/glm-4.6v-flash-pilot.json

PYTHONPATH=projects/pdf-to-markdown-toyota/workspace uv run python projects/pdf-to-markdown-toyota/workspace/render_box_aware_ngram_html.py --root projects/pdf-to-markdown-toyota/experiments/exp-010
```

## Notes For Reviewer

旧exp-009は旧定義の結果として保持し、本結果をblock-aware・numeric-excludedの修正版とする。数字を除外する際は数字tokenを削除して前後の文字を連結せず、数字を境界として扱っている。
