# Artifact Audit

## Verdict

PASS

## Checked Artifacts

- `spec.yaml`: present and consistent with a larger local fixture run.
- `workspace/make_fixture_data.py`: present.
- `workspace/train_baseline.py`: present.
- `workspace/data/train.csv`: present.
- `workspace/data/test.csv`: present.
- `workspace/data/sample_submission.csv`: present.
- `workspace/submission.csv`: present, 1200 rows, columns `PassengerId` and `Transported`.
- `results/results.md`: present and records setup, metrics, limitations, comparison, and reproduction commands.
- `results/scores.json`: present with status `completed` and primary metric.
- `logs/run.log`: present.

## Blocking Issues

None.

## Warnings For Interpretation

- The dataset is synthetic and should not be interpreted as Kaggle leaderboard evidence.
- exp-002 and exp-003 use different fixture seeds and sizes, so their comparison is a workflow smoke test, not a controlled modeling study.
- Fixture generation emitted pandas FutureWarnings for missing bool-like values.
- No public leaderboard score is available.

## Notes

The artifact set is sufficient for result interpretation.
