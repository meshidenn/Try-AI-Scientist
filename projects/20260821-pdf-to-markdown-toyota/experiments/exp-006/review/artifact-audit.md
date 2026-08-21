# Artifact Audit

## Verdict

PASS

## Checked Artifacts

- `spec.yaml`、`README.md`、`inputs/`、`logs/evaluate-ensemble-confidence.json`が存在する。
- `results/ensemble_confidence.json`、`results/scores.json`、`results/claims.json`、`manifest.json`はJSONとして構文妥当である。
- `outputs/confidence-review/hybrid/` に4ページ分のHTML review artifactが存在する。
- `find`によりexp-006配下の`.py`、`.sh`、notebook、`.pyc`が0件であることを確認した。共有実装は`workspace/evaluate_ensemble_confidence.py`にある。
- 共有workspaceのunittest 14件がすべて成功した。

## Blocking Issues

なし。

## Warnings For Interpretation

- primary metricの`mean_coverage_adjusted_confidence`は、校正済みの正答確率ではない。PDF text layerの数値token被覆率を掛けたevidence scoreである。
- 数値token集合の評価なので、表セル位置・列対応、数値の重複、単位対応、画像化グラフの値は評価しない。
- Gemma出力はexp-003、Qwen/GLM出力はexp-004の既存artifactであり、実行器・promptの完全な同一性は保証されない。

## Notes

- 実験は既存出力の再評価のみであり、新規モデル推論は実行していない。
