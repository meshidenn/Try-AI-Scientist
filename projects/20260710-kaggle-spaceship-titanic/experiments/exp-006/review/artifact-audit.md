# Artifact Audit

## Verdict

PASS

## Checked Artifacts

- `spec.yaml`: present.
- `workspace/compare_official_models.py`: present.
- `workspace/submission.csv`: present, 4277 rows plus header.
- `results/results.md`: present.
- `results/scores.json`: present with completed status, candidate fold scores, selected model, exp-005 comparison, and Kaggle submission metadata.
- `logs/run.log`: present.

## Blocking Issues

None.

## Warnings For Interpretation

- Private leaderboard score is not available.
- HistGradientBoosting uses ordinal-encoded categorical features in this script, not native categorical dtypes.

## Notes

The artifact set is sufficient for local CV comparison claims and public leaderboard score reporting.
