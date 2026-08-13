# exp-011: Line-aware and numeric-excluded n-gram evaluation

exp-010で判明した、同一PDF block内の別line・別列を連結する問題を修正した再評価である。

- PDFの`get_text("dict")`からtext lineを抽出し、各line内だけでn-gramを生成する
- 出力側もMarkdownの行・表セル単位を跨がない
- NFKC後の数字tokenと数字tokenを跨ぐn-gramを評価から除外する

特に決算説明会資料p8の「日本」「北米」「欧州」のように、同一block内でも画像上の列が異なる文字列を連接しない。既存hybrid出力を再利用し、追加推論は行わない。
