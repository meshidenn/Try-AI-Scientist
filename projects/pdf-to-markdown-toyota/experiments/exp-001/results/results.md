# Results

## Summary

vLLMを用いた選定ページ比較を実行済み。4資料から最大3ページずつを、`parse_first`と`image_first`の2方式で処理し、22件すべてが成功した。

## Setup

- logical model: `gemma4-26b-moe`
- model ID: `google/gemma-4-26B-A4B-it`
- backend: `vllm_openai` (`vllm/vllm-openai:gemma4-cu130`)
- methods: `parse_first`, `image_first`
- documents: Toyota公式4資料
- server: `http://127.0.0.1:18021/v1`
- pages: 有価証券報告書・決算説明会資料・統合報告書は各3ページ、中期方針資料は全2ページ

## Metrics

ページ単位の測定値は `results/page_metrics.json` に保存した。成功ページ平均は、parse-firstが本文長近似0.830、数値token再現率0.733、image-firstが本文長近似0.722、数値token再現率0.642だった。Markdown表を出力したページはparse-first 6件、image-first 5件で、行幅が一貫した表はparse-first 3件、image-first 1件だった。

## Main Results

parse-firstは本文長近似・数値token再現率・表行幅一貫性でimage-firstを上回った。統合報告書11ページのparse-firstは16K contextでも失敗したが、32K contextでは入力を切り詰めずに成功した。したがって、座標付きparse payloadにはページ内容に応じたcontext長またはchunkingが必要である。

## Figures

なし。

## Failures And Negative Results

- GitHub issue作成はgh認証不足でHTTP 401になった。
- Transformers直接推論は初回ページで非常に遅く、方式比較の実行系からは外した。
- vLLMサーバーはGemma重みロードに約5分、初期化・CUDA graph準備を含めて約7分を要した。
- 画像方式はスライドの視覚構造を利用できる一方、決算説明会資料29ページで1020列の不正なMarkdown tableが生成され、表の後処理またはcropが必要と分かった。
- 32K contextの再試行は1ページあたり57.8秒を要した。長いparse payloadは品質と推論コストのトレードオフになる。

## Reproduction

```bash
WORKSPACE_DIR="/projects/pdf-to-markdown-toyota/experiments/exp-001/workspace" LOG_DIR="/projects/pdf-to-markdown-toyota/experiments/exp-001/logs" ./projects/pdf-to-markdown-toyota/workspace/start_vllm.sh
uv run python projects/pdf-to-markdown-toyota/workspace/run_vllm_experiment.py --root projects/pdf-to-markdown-toyota/experiments/exp-001 --max-pages 3 --max-new-tokens 1024
uv run python projects/pdf-to-markdown-toyota/workspace/evaluate_outputs.py --root projects/pdf-to-markdown-toyota/experiments/exp-001 --log projects/pdf-to-markdown-toyota/experiments/exp-001/logs/vllm-run.json --log projects/pdf-to-markdown-toyota/experiments/exp-001/logs/vllm-retry-integrated-p11-32k.json
```

## Notes For Reviewer

前処理だけで実験成功とは扱わない。
