# Results

## Summary

PDF block+bboxとページ画像を同時に入力するhybridは、数値再現率と表の行幅整合では最良だった。一方、テキスト全体近似はparse-firstを下回った。最終v2は11/11ページ成功した。

## Setup

exp-001と同一の11ページを、PDF block+bboxと300 DPIページ画像で同時に入力した。Gemma 4 26B A4B InstructをvLLMでtemperature 0、max model length 32768、max new tokens 1024として実行した。

## Metrics

`text_normalized_similarity_proxy`、`numeric_token_recall`、Markdown表の行幅整合、wall timeを用いた。前二者はPDF text layerをreferenceとするproxyであり、画像上の位置・図形の再現を直接は測らない。

## Main Results

| 方式 | 成功 | text proxy ↑ | numeric recall ↑ | 表を含む出力 | 行幅整合 | 平均wall time (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| parse-first (exp-001) | 11/11 | 0.830 | 0.733 | 6 | 3 | 28.86 |
| image-first (exp-001) | 11/11 | 0.722 | 0.642 | 5 | 1 | 23.89 |
| hybrid v1 | 11/11 | 0.732 | 0.689 | 5 | 2 | 30.58 |
| **hybrid v2** | **11/11** | **0.750** | **0.748** | **5** | **4** | **30.45** |

hybrid v1では、決算説明会資料8ページの点線装飾を反復出力して1024 tokenを使い切った。v2では「装飾線を文字で再現しない」規則を追加し、同ページのnumeric recallを`0.000`から`0.818`へ改善した。

v2は数値recallでparse-firstを`+0.015`、表の行幅整合で`+1`件改善した。text proxyはparse-firstより`-0.080`であり、位置関係を含む評価ではないことにも注意が必要である。

## Figures

生成Markdownは `workspace/outputs-hybrid/`（gitignore対象）にある。評価のページ別数値は `results/page_metrics.json` に保存した。

## Failures And Negative Results

- 初版hybridは決算説明会資料8ページの点線を反復し、numeric recallが`0.000`だった。v2で修正済みだが、初版ログ `logs/hybrid-run.json` をnegative resultとして保存した。
- 統合報告書11ページの長い系譜表は、v2でも1024 output token上限の影響を受け、text proxy `0.301`、numeric recall `0.226`に留まった。
- 表構造の評価はMarkdownの行幅のみであり、cell value・rowspan/colspan・位置関係のgold評価ではない。

## Reproduction

```bash
WORKSPACE_DIR="$PWD/projects/pdf-to-markdown-toyota/experiments/exp-003/workspace" \
LOG_DIR="$PWD/projects/pdf-to-markdown-toyota/experiments/exp-003/logs" \
PORT=18021 ./projects/pdf-to-markdown-toyota/workspace/start_vllm.sh

uv run python projects/pdf-to-markdown-toyota/workspace/run_hybrid_experiment.py --root projects/pdf-to-markdown-toyota/experiments/exp-003 \
  --pdf-dir projects/pdf-to-markdown-toyota/experiments/exp-001/workspace/input/pdfs \
  --max-pages 3 --max-new-tokens 1024 --log-name hybrid-run-v2.json

uv run python projects/pdf-to-markdown-toyota/workspace/evaluate_outputs.py \
  --root projects/pdf-to-markdown-toyota/experiments/exp-003 \
  --pdf-dir projects/pdf-to-markdown-toyota/experiments/exp-001/workspace/input/pdfs \
  --log projects/pdf-to-markdown-toyota/experiments/exp-003/logs/hybrid-run-v2.json
```

## Notes For Reviewer

ページ単位fusionは領域cropを含む完全なhybridではない。次はページ分類後に、表・グラフ・本文をbbox cropして別promptへ送り、構造化mergeするべきである。
