# Claim Audit

## Verdict

PASS WITH SCOPE LIMITS

## Checked Claims

- C1は各experimentの`results/scores.json`にあるrelation数0、6、24、80と一致する。
- C2はexp-005の`outputs/run_summary.json`にあるextract非`stop` 4件と一致する。
- C3は`not_evaluated`であり、results本文もretrieval品質改善を主張していない。

## Scope Limits

- C1とC2は固定した1-document smoke pilot条件にのみ適用する。
- relation数はquality metricではない。
