# N-gram Match HTML

既存の `results/page_ngrams.json` とPDF text layerから、モデル・資料・ページごとのHTMLを12件生成した。

## 表示内容

- n=1〜10をプルダウンで切り替え
- モデル出力の正規化後テキスト: PDFページ内に存在するn-gramを緑、不一致の出力n-gramを赤で表示
- PDF text layer: 出力に存在しないn-gramが対応する位置を赤で表示
- PDF側にあり出力側にないn-gramの文字列一覧
- nごとの `out`、`cov`、F1、n-gram件数
- ページ単位の元Markdown出力

## 出力先

```text
outputs/ngram-match-html/<model>/<document>/page-<page>.html
```

全HTMLの対応表は `results/ngram_html_manifest.json` にある。HTMLは追加推論なしで生成した。

## 解釈上の注意

色付け対象は比較用にNFKC、空白除去、Markdown構文除去を行ったテキストである。n-gramはユニーク集合として判定するため、同一文字列の出現回数や表セル位置は評価しない。
