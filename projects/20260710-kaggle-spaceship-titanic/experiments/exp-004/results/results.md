# Results

## Summary

Status: completed.

Compared two sklearn model candidates on the same local fixture configuration as
exp-002.

## Setup

- Experiment: `exp-004`
- Data: synthetic fixture, 1200 train rows, 400 test rows, seed 42
- Evaluation: 5-fold stratified cross-validation

## Metrics

| Candidate | CV Accuracy Mean | CV Accuracy Std |
| --- | ---: | ---: |
| logistic_regression | 0.643333 | 0.019650 |
| random_forest | 0.666667 | 0.020242 |

Majority baseline accuracy: 0.533333

## Main Results

Selected candidate: `random_forest`.

Best CV accuracy: 0.666667.

## Figures

No figures were generated.

## Failures And Negative Results

- Official Kaggle leaderboard score is unavailable.
- Candidate comparison is local to a synthetic fixture.

## Reproduction

```bash
uv run python make_fixture_data.py --out-dir data --train-rows 1200 --test-rows 400 --seed 42
uv run python compare_models.py --data-dir data --folds 5
```

## Notes For Reviewer

This experiment validates candidate comparison artifacts, not real Kaggle
generalization.
