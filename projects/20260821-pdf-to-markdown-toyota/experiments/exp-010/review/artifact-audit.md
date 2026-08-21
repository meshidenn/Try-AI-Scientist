# Artifact Audit

## Verdict

PASS

## Checked Artifacts

- `results/page_ngrams.json` は3モデル共通4ページ、12 records、n=1〜10を含む。
- `definition` にPDF text block境界、出力unit境界、数値token除外が記録されている。
- `results/scores.json` のoverall値とmodel別値は実測JSONのsummaryと一致する。
- `results/ngram_html_manifest.json` は12個のHTMLを指し、全ファイルが存在する。
- HTMLに一致、不一致、PDF側の漏れ、数字除外の表示要素が含まれる。
- 実装とテストはworkspaceにあり、exp-010配下にPython sourceはない。

## Blocking Issues

なし。

## Warnings For Interpretation

- PDFのtext blockはPyMuPDFのtext layerを正解とするproxyで、人手goldではない。
- 数字tokenは一致していても評価対象外である。
- 出力側はMarkdownの行・表セルをunitとするため、モデルの改行がPDF blockと異なる場合の構造までは評価しない。

## Notes

単体テスト11件（block-aware評価3件、HTML2件、既存評価6件）は成功した。追加推論は行っていない。
