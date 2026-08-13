# Results

## Summary

有価証券報告書 p135をPDF text block座標の縦空白で2表に分割し、Gemma 4を各chunkへ4096 token上限で適用した。ページ一括方式で起きた第2表途中の切断を解消し、表本体の83個の数値tokenに対するrecallとprecisionはともに1.000000だった。

最初の起動失敗と判断した事象は誤判定だった。過去の成功ログと同様、Gemmaの重みロードには約6分を要する。通常精度で起動を待機したところ、353.65秒でweight loadingが完了し、推論へ到達した。FP8 Dynamicの再試行は不要であり、FP8結果としては扱わない。

## Setup

- 対象: 有価証券報告書 p135（連結持分変動計算書）
- モデル: `google/gemma-4-26B-A4B-it`、local vLLM 0.19.1 dev
- 分割: 20pt以上の縦空白で前年度表と当年度表を別chunk化
- chunk 1 bbox: `[50.73, 48.84, 548.03, 361.81]`
- chunk 2 bbox: `[50.73, 370.24, 547.83, 711.21]`
- 生成: 各chunk `max_new_tokens=4096`、temperature 0
- baseline: exp-003の同ページ一括hybrid、`max_new_tokens=1024`
- 比較対象の数値集合: 表本体の83数値token。ページフッタの`132`は除外した。

## Metrics

| 指標 | 定義 | 高い方がよいか |
| --- | --- | --- |
| Numeric recall | 参照数値tokenのうち出力に含まれる割合 | はい |
| Numeric precision | 出力数値tokenのうち参照に含まれる割合 | はい |
| Finish reason | APIがgenerationを終了した理由 | `stop`が途中切れなしの補助根拠 |

## Main Results

| 方式 | 数値token recall | 数値token precision | matched / reference | finish reason |
| --- | ---: | ---: | ---: | --- |
| 一括hybrid baseline（1024 token） | 0.590361 | 1.000000 | 49 / 83 | 出力末尾が第2表途中 |
| 座標chunk hybrid（4096 token） | **1.000000** | **1.000000** | **83 / 83** | chunk 1: stop, chunk 2: stop |

| Chunk | 領域 | 出力文字数 | 数値recall | finish reason | 実行時間 |
| --- | --- | ---: | ---: | --- | ---: |
| 1 | 前年度表 | 1,295 | 1.000000 | stop | 43.74秒 |
| 2 | 当年度表 | 1,466 | 1.000000 | stop | 45.63秒 |

## Figures

- `outputs/securities_report/page-0135/chunk-01/region.png`
- `outputs/securities_report/page-0135/chunk-02/region.png`

## Failures And Negative Results

- chunk 1/2ともMarkdown表の行幅は一貫しない。数値集合が完全一致しても、セル列の対応が正しいことは保証しない。
- 当年度表に`[判読不能]`のセルが1件ある。数値token評価では検知できない構造・欠損である。
- 初回に5分程度でロード停止と判断したが、過去の成功ログでは最初のshardが5分超かかっていた。今回の通常精度ロードは353.65秒で完了したため、ロード時間だけを失敗根拠にしてはならない。

## Reproduction

```bash
uv run python projects/pdf-to-markdown-toyota/workspace/run_chunked_hybrid.py \
  --root projects/pdf-to-markdown-toyota/experiments/exp-007 \
  --document securities_report --page 135 \
  --base-url http://127.0.0.1:18028/v1 \
  --model gemma4-26b-moe --max-new-tokens 4096
```

## Notes For Reviewer

この結果は有報p135の1ページ・2表でのpilotである。座標chunk化が全資料・グラフ・統合報告書の図に一般化することは示していない。
