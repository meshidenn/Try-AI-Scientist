# Results

## Summary

Unlimited-OCR を、外部APIを使わず公式 `vllm/vllm-openai:unlimited-ocr` イメージで4代表ページに実行した。4/4ページが生成成功し、今回の生出力評価では3モデル中で最高の文字量proxy (0.594082) と数値F1 (0.209897) を得た。

ただし出力はMarkdownそのものではなく、bbox付きの `title` / `text` / `table` / `chart` レコードである。表はHTML断片、グラフは `chart [bbox]` に留まるため、最終的なMarkdown比較には座標付き中間表現をMarkdown/HTMLへレンダリングする後処理が必要である。

## Setup

- 入力: 4種のToyota資料から各1ページ（`inputs/pilot-pages.json`）
- 推論: ローカルGPU、外部推論APIなし
- Unlimited-OCR: `baidu/Unlimited-OCR` revision `07dea832e22aefee32ad281d4b80551282e1c168`
- runtime: `vllm/vllm-openai:unlimited-ocr`、native prompt `document parsing.`

## Metrics

| Model | 文字量proxy | 数値recall | 数値precision | 数値F1 | 秒/頁 |
|---|---:|---:|---:|---:|---:|
| PaddleOCR-VL-1.6 | 0.474997 | 0.434632 | 0.290182 | 0.164853 | 21.143747 |
| DeepSeek-OCR-2 | 0.539732 | 0.309994 | 0.161796 | 0.192047 | 10.144335 |
| Unlimited-OCR | **0.594082** | 0.368580 | 0.180162 | **0.209897** | 10.562507 |

数値指標はPDFテキスト層との数値トークン集合の比較であり、表のセル対応やグラフの意味を測るものではない。

## Main Results

- 有報の表では、Unlimited-OCRは`<table>`内に数値を多く保持したが、行・列のHTML構造は崩れている。
- 決算説明会の棒グラフでは、`chart [bbox]`として位置を保持する一方、棒・系列値は構造化されなかった。
- 統合報告書では、本文と画像bboxを分けられたが、系統図は画像領域として残り、ノード・エッジに展開されなかった。
- 中期経営計画書の通常本文はbbox付きテキストとしてほぼ連続して読めた。

## Failures And Negative Results

- PaddleOCR-VL-1.6のvLLM直結出力には`<|LOC...|>`が残った。公式PaddleOCR pipelineはこのARM/CUDA 13環境で`PP-DocLayoutV3`初期化時にSIGSEGVした。
- MinerU2.5-Proは公式ユーティリティとvLLM 0.21でもレイアウト出力が不正な反復文字列となり、有効なMarkdownを得られなかった。
- Unlimited-OCRの初回起動はDeepSeek-OCR-2がGPUを占有していたためOOMとなった。DeepSeekコンテナ停止後は正常起動した。

## Reproduction

`projects/pdf-to-markdown-toyota/workspace/start_vllm.sh` をUnlimited-OCR公式イメージ・ポート18027で起動し、`projects/pdf-to-markdown-toyota/workspace/run_general_vlm.py --root projects/pdf-to-markdown-toyota/experiments/exp-005 --modes native_ocr --native-instruction 'document parsing.'` を実行する。

## Notes For Reviewer

Unlimited-OCRは「位置を失わずに抽出する中間表現」として有望である。一方、現在の評価器はbboxやHTML断片をMarkdownと同列にスコアリングするため、次回は(1)座標付きIRの保持率、(2)HTML table gridの整合性、(3)図表領域の手動意味評価を分離する。
