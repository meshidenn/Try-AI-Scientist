# Artifact Audit

## Verdict

PASS

## Checked Artifacts

- `results/page_ngrams.json` はJSONとして読み込め、n=1〜10の10条件を含む。
- 3モデル共通の4ページが記録され、model-page recordは12件（各モデル4件）である。
- `results/results.md` と `results/scores.json` の主指標値は `page_ngrams.json` のoverall集計と一致する。
- `logs/evaluate-page-ngrams.json` に入力ログ、対象ページ数、追加推論なし、結果pathが記録されている。
- 実装・テストは `workspace/` にあり、exp-009配下にPython sourceは置いていない。

## Blocking Issues

なし。

## Warnings For Interpretation

- 正解はPDF text layerであり、人手goldではない。
- n=1は頻出文字の一致で高くなりやすい。
- n-gramはユニーク集合で数えるため、出現回数、表セル位置、読み順、画像中文字は評価しない。
- Gemmaログの追加ページはモデル間の共通範囲に含めず、4ページ比較から除外した。

## Notes

単体テスト3件は成功した。評価実行は12件すべて成功し、ページ境界をまたぐ参照は行っていない。
