# Experiment exp-003

## Objective

表はparse優先、グラフ・図と配置は画像優先という根拠規則を同一Gemma promptへ与え、hybrid Markdownを生成する。

## Status

`completed`。v2のhybrid promptで4資料・選定11ページをすべて生成・評価済み。

最終方式は、PDFから抽出した文字block・座標と300 DPIのページ画像を同じGemma 4 promptへ入力する。表の値はparse、図・グラフの位置関係は画像、段組み・読順は両者を根拠とする。

## Result

- text normalized similarity proxy: `0.750`
- numeric token recall: `0.748`（parse-first `0.733`を上回る）
- 表を含む出力の行幅整合: `4/5`（parse-first `3/6`、image-first `1/5`）

全体テキスト近似ではparse-firstの`0.830`に届かない。ページ全体を一つのpromptで融合するだけでは、抽出テキストの読み順を十分に回復できないことが分かった。
