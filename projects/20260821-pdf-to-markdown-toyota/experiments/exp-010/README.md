# exp-010: Block-aware and numeric-excluded n-gram evaluation

exp-009で判明した2つの問題を修正した再評価である。

- PDFのtext blockを単一文字列へ連結せず、各block内だけでn-gramを生成する
- 出力側もMarkdownの行・表セル単位を跨がない
- NFKC後の数字tokenと数字tokenを跨ぐn-gramを評価から除外する

exp-003とexp-004の既存hybrid出力を再利用し、追加推論は行わない。評価結果とモデル別HTMLはこのexperiment配下へ保存する。
