# Results

## Summary

Status: completed.

Ran official-data feature bundle and model comparison.
Submitted the selected model to Kaggle and recorded the public leaderboard score.

## Setup

- Experiment: `exp-006`
- Data: official Kaggle CSV files in `/Users/hiroki-iida/works/Try-AI-Scientist/projects/kaggle-spaceship-titanic/data/spaceship-titanic`
- Feature bundle: group, cabin, spending, missingness, and categorical combinations
- CV: 5-fold StratifiedKFold, random_state=42

## Metrics

| Candidate | CV Accuracy Mean | CV Accuracy Std |
| --- | ---: | ---: |
| random_forest | 0.740020 | 0.005579 |
| extra_trees | 0.756814 | 0.008809 |
| hist_gradient_boosting | 0.808810 | 0.007786 |

Selected model: `hist_gradient_boosting`

exp-005 baseline accuracy: 0.744276

Delta versus exp-005: 0.064535

Kaggle public leaderboard score: 0.803830

## Main Results

Best official-data CV accuracy in this run is 0.808810.
The selected model wrote a valid submission with 4277 rows.
Kaggle accepted the submission as ref `54281125` with public score 0.803830.

## Figures

No figures were generated.

## Failures And Negative Results

- Private leaderboard score is not available.
- HistGradientBoosting uses ordinal-encoded categoricals here, not native categorical dtypes.

## Reproduction

```bash
uv run python compare_official_models.py --data-dir /Users/hiroki-iida/works/Try-AI-Scientist/projects/kaggle-spaceship-titanic/data/spaceship-titanic
uv run kaggle competitions submit -c spaceship-titanic -f workspace/submission.csv -m "exp-006 hist_gradient_boosting feature bundle cv=0.808810"
```

## Notes For Reviewer

Compare claims against `results/scores.json`; do not infer leaderboard accuracy.
