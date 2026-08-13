# Artifact Audit

## Verdict

PASS WITH WARNINGS。最終v2の入力、11ページの実行ログ、生成出力、評価JSON、比較値が追跡可能である。

## Checked Artifacts

- `workspace/input/documents.json` に4資料の出所、SHA-256、ページ数がある。
- `logs/hybrid-run-v2.json` に11件すべて`success`、model、backend、wall time、出力pathがある。
- `workspace/outputs-hybrid/` に11ページの最終Markdownが存在する（生成物のためgitignore）。
- `results/page_metrics.json` に11ページすべての評価値がある。
- `results/scores.json` と `results/results.md` の最終平均値が一致する。
- 初版失敗のログ `logs/hybrid-run.json` と、修正確認の2つのsmoke logを保存した。

## Blocking Issues

なし。

## Warnings For Interpretation

- PDF text layerをreferenceにしたproxyであり、グラフの位置関係や図の忠実性を直接測定していない。
- `max_new_tokens=1024`のため、長い表・本文の完全性は評価値より低い可能性がある。
- 表評価はMarkdown行幅のみで、セル値・結合セルのgold評価ではない。
- v1の生成出力はv2で上書きされたため、v1は実行ログとその時点で記録した集計値で追跡する。

## Notes

v1は決算説明会資料8ページの点線装飾を反復して失敗した。v2は装飾図形を出力しない規則を追加した最終promptである。
