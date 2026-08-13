# exp-009: Page-level character n-gram match rate

PDFのtext layerをページ単位の正解として、既存の3モデルのhybrid Markdown出力を文字n-gramで比較する。各n-gramは正規化後のユニーク集合とし、n=1〜10を測定する。

主指標は、出力Markdown側のn-gramのうち同じPDFページ内に存在する割合である。併せて、PDF側n-gramの出力による回収率とF1を保存する。これはPDFの文字layerを正解とした文字列一致の評価であり、表のセル位置、読み順、画像中文字、意味的な正しさは評価しない。

実装は共有の `workspace/evaluate_page_ngrams.py` に置き、結果は `results/page_ngrams.json`、`results/results.md`、`results/scores.json` に保存する。入力PDFはexp-001のsnapshotを参照する。
