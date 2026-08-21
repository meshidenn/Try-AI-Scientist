# Artifact Audit

## Verdict

PASS

## Checked Artifacts

- `results/page_ngrams.json` は3モデル共通4ページ、12 records、n=1〜10を含む。
- `definition` にPDF text line境界、出力unit境界、数値token除外が記録されている。
- 決算説明会資料p8の「日本」「北米」「欧州」は別lineとして抽出される。
- `results/scores.json` のoverall値・model別値は実測summaryと一致する。
- `results/ngram_html_manifest.json` は12個のHTMLを指し、全ファイルが存在する。

## Blocking Issues

なし。

## Warnings For Interpretation

- PDF text lineはPyMuPDFのtext layerを正解とするproxyで、人手goldではない。
- 数字tokenは一致していても評価対象外である。
- 出力側はMarkdownの行・表セルをunitとするため、モデルの改行がPDF lineと異なる場合の構造までは評価しない。

## Notes

line-aware評価、HTML生成、関連テストとartifact整合性検証が完了した。追加推論は行っていない。
