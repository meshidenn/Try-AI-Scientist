# Artifact Audit

## Verdict

PASS with interpretation warnings

## Checked Artifacts

- `spec.yaml`、`README.md`、入力manifest、実行log、数値・テキストの結果JSONが存在する。
- `ensemble_confidence.json`、`ensemble_text_confidence.json`、`scores.json`、`claims.json`、`manifest.json`はJSONとして妥当である。
- 数値review HTMLとテキストreview HTMLが各4ページ、計8件存在する。
- 実出力を着色したHTMLがGemma / Qwen / GLMの各4ページ、計12件存在する。各HTMLは元Markdownのescaped sourceを`details`内に保持し、High / Medium / Lowの3色CSSを定義する。
- exp-008配下に`.py`、`.sh`、notebook、`.pyc`は存在しない。共有実装はworkspaceにある。
- 共有workspaceの全unittest 20件が成功した。

## Blocking Issues

なし。

## Warnings For Interpretation

- 数値とテキストは候補単位・重みが異なる。0.643828と0.502155を絶対的な品質差や正答確率として比較してはならない。
- text coverage proxyはPDF text block相当の文字列被覆であり、意味的言い換え、図中文字、表セル位置を評価しない。
- 入力は既存の1024 token hybrid出力である。p135のGemma chunk出力を3モデル比較へ混在させていない。

## Notes

追加推論は行わず、既存local vLLM artifactの再評価と表示用HTML生成だけを実行した。
