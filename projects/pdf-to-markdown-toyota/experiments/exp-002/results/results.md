# Results

## Summary

HTML fragmentとして22/22件の生成に成功した。Markdown版と同じ選定11ページ・Gemma 4・vLLM 32K contextを使用した。

## Setup

- model: `gemma4-26b-moe` (`google/gemma-4-26B-A4B-it`)
- backend: `vllm_openai` (`vllm/vllm-openai:gemma4-cu130`)
- context: 32,768 tokens
- methods: `parse_first`, `image_first`
- format: CSSなしのHTML fragment

## Metrics

成功ページ平均は、parse-firstが本文量近似0.703、数値token再現率0.692、image-firstが本文量近似0.660、数値token再現率0.686だった。HTML tableを出力したページはparse-first 2件、image-first 3件で、行幅一貫表はそれぞれ0件、2件だった（`colspan`考慮、`rowspan`未考慮）。

## Main Results

HTML出力でもparse-firstが本文量近似・数値token再現率でimage-firstを上回った。一方、exp-001のMarkdown版より本文量近似はparse-firstで0.830→0.703、image-firstで0.722→0.660に低下した。HTMLはタグ表現の利点があるが、今回のプロンプトだけでは構造忠実度の改善を示せない。

## Figures

なし。

## Failures And Negative Results

- 推論失敗は0件。
- HTML contractの許可外タグ`hr`、`span`、`strong`が1ファイルに計5回出現した。
- tableの`rowspan`とセル内容の正しさは自動評価していない。

## Reproduction

`README.md` のvLLM起動・実行コマンドを使う。評価は次で再現できる。

```bash
uv run python projects/pdf-to-markdown-toyota/workspace/evaluate_outputs.py --root projects/pdf-to-markdown-toyota/experiments/exp-002 --pdf-dir projects/pdf-to-markdown-toyota/experiments/exp-001/workspace/input/pdfs --log projects/pdf-to-markdown-toyota/experiments/exp-002/logs/vllm-html-run.json
```

## Notes For Reviewer

HTML要素の存在だけを正確さと扱わず、数値と表構造を個別に確認する。
