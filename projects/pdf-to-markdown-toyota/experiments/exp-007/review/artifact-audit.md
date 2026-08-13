# Artifact Audit

## Verdict

PASS with interpretation warnings

## Checked Artifacts

- `spec.yaml`、`README.md`、`inputs/source-manifest.json`、実行log、結果Markdown/JSONが存在する。
- `chunk_metrics.json`、`scores.json`、`claims.json`、`manifest.json`はJSON構文として妥当である。
- 2 chunkのinput JSON、crop PNG、Markdown outputが存在する。
- `chunk_metrics.json`では2 chunkとも`status=success`、`finish_reason=stop`、page numeric recall=1.0である。
- exp-007配下に`.py`、`.sh`、notebook、`.pyc`は存在しない。実装は共有workspaceにある。
- 実験コンテナは停止済みである。

## Blocking Issues

なし。

## Warnings For Interpretation

- 数値評価は表本体の数値token集合であり、位置・重複・列・セル対応を測らない。
- 両Markdown表は行幅一貫性を満たさず、当年度表には`[判読不能]`セルが残る。
- baselineとの比較は、ページフッタを除いた83 token参照集合で再計算した値を使う。

## Notes

- 初回のruntime_blocked判断は、Gemmaの重みロードに約6分必要という過去ログを見落としたため更新した。今回のrunでは353.65秒で重みロードが完了した。
