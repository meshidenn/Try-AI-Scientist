# Claim Audit

## Verdict

PASS with scope limitations

## Checked Claims

- 数値集計値は`results/ensemble_confidence.json`と`results/scores.json`に一致する。
- 「High候補だけでは欠落を隠す」は、有価証券報告書 p135のHigh 49件とcoverage 0.583333で直接支持される。
- 正答確率・表セル正確性・グラフ系列正確性の主張はしていない。

## Unsupported Claim Prevented

High/Medium/Lowを校正済み確率とみなす根拠はない。人手正解ラベルによる校正前はevidence scoreとしてのみ扱う。
