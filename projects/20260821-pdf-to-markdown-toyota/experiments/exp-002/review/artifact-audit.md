# Artifact Audit

## Verdict

WARN

## Checked Artifacts

- 4資料のURL、SHA-256、ページ数を `workspace/input/documents.json` に保存
- `parse_first` / `image_first` の選定11ページ、計22 HTML fragmentを保存
- `logs/vllm-html-run.json` の22レコードすべてがsuccess
- `results/page_metrics.json` の22レコードと出力ファイルの存在を確認
- HTML tableの`colspan`を考慮して行幅を集計

## Blocking Issues

なし。22件の出力と評価artifactは存在する。

## Warnings For Interpretation

- 許可外タグの`hr`、`span`、`strong`が1ファイルに計5回出現したため、HTML contractは完全には守られていない。
- table形状は`colspan`を考慮するが、`rowspan`とセル意味の正しさは評価していない。
- 本文量近似と数値token再現率はPDF text layerを参照するproxyであり、人手goldの正解率ではない。

## Notes

vLLMコンテナは検証後に停止する。
