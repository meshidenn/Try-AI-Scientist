# Result Interpretation

## Summary

exp-003 validates that the workflow can repeat a completed run at a larger local
fixture size and preserve comparable artifacts.

## Supported Findings

- Local 5-fold CV accuracy was 0.644800.
- Majority-class baseline accuracy was 0.538600.
- The local model exceeded the majority baseline by 0.106200 accuracy.
- exp-003 CV accuracy was 0.021867 lower than exp-002.
- `workspace/submission.csv` has the expected two-column submission format and
  1200 rows.

## Limitations

- The data is synthetic, so this does not validate Kaggle leaderboard
  performance.
- The comparison with exp-002 is not controlled for seed or exact data
  distribution.
- The generator warning should be fixed before fixture runs are used as a
  regression test.

## Workflow Finding

The artifact workflow supports repeated runs and cross-run comparison, but the
comparison would be easier if `scores.json` had a stricter shared schema for
dataset provenance and run configuration.
