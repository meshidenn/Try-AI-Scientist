# Results

## Summary

Status: completed.

Ran a small HistGradientBoosting hyperparameter search on official Kaggle data.
Submitted the selected candidate to Kaggle.

## Setup

- Experiment: `exp-008`
- Data: official Kaggle CSV files in `/Users/hiroki-iida/works/Try-AI-Scientist/projects/kaggle-spaceship-titanic/data/spaceship-titanic`
- Feature bundle: same as exp-006
- CV: 5-fold StratifiedKFold, random_state=42
- Candidate count: 36

## Metrics

exp-006 CV baseline: 0.808810

Best exp-008 CV accuracy: 0.812261

Delta versus exp-006 CV: 0.003451

exp-006 public leaderboard baseline: 0.803830

exp-008 public leaderboard score: 0.802430

Delta versus exp-006 public score: -0.001400

| Rank | Candidate | CV Accuracy Mean | CV Accuracy Std | Params |
| ---: | --- | ---: | ---: | --- |
| 1 | hgb_004 | 0.812261 | 0.012176 | {"l2_regularization": 0.0, "learning_rate": 0.04, "max_iter": 200, "max_leaf_nodes": 31, "min_samples_leaf": 20} |
| 2 | hgb_006 | 0.811342 | 0.007427 | {"l2_regularization": 0.05, "learning_rate": 0.04, "max_iter": 200, "max_leaf_nodes": 31, "min_samples_leaf": 20} |
| 3 | hgb_003 | 0.811226 | 0.007697 | {"l2_regularization": 0.05, "learning_rate": 0.04, "max_iter": 200, "max_leaf_nodes": 15, "min_samples_leaf": 20} |
| 4 | hgb_033 | 0.811112 | 0.004827 | {"l2_regularization": 0.05, "learning_rate": 0.06, "max_iter": 300, "max_leaf_nodes": 15, "min_samples_leaf": 20} |
| 5 | hgb_010 | 0.810996 | 0.010681 | {"l2_regularization": 0.0, "learning_rate": 0.04, "max_iter": 300, "max_leaf_nodes": 31, "min_samples_leaf": 20} |
| 6 | hgb_025 | 0.809732 | 0.005635 | {"l2_regularization": 0.0, "learning_rate": 0.06, "max_iter": 200, "max_leaf_nodes": 15, "min_samples_leaf": 20} |
| 7 | hgb_002 | 0.809731 | 0.005893 | {"l2_regularization": 0.01, "learning_rate": 0.04, "max_iter": 200, "max_leaf_nodes": 15, "min_samples_leaf": 20} |
| 8 | hgb_009 | 0.809731 | 0.006253 | {"l2_regularization": 0.05, "learning_rate": 0.04, "max_iter": 300, "max_leaf_nodes": 15, "min_samples_leaf": 20} |
| 9 | hgb_015 | 0.809501 | 0.005908 | {"l2_regularization": 0.05, "learning_rate": 0.05, "max_iter": 200, "max_leaf_nodes": 15, "min_samples_leaf": 20} |
| 10 | hgb_027 | 0.809501 | 0.005703 | {"l2_regularization": 0.05, "learning_rate": 0.06, "max_iter": 200, "max_leaf_nodes": 15, "min_samples_leaf": 20} |

## Main Results

Selected candidate `hgb_004` with CV accuracy 0.812261.
The selected model wrote `workspace/submission.csv` with 4277 rows.
Kaggle accepted submission ref `54296477` with public score 0.802430.

The tuned candidate improved local CV but did not improve public leaderboard
score versus exp-006.

## Figures

No figures were generated.

## Failures And Negative Results

- Public leaderboard score decreased from exp-006 by 0.001400.
- Private leaderboard score is not available.
- This search only tunes HistGradientBoosting hyperparameters.

## Reproduction

```bash
uv run python tune_hist_gradient_boosting.py --data-dir /Users/hiroki-iida/works/Try-AI-Scientist/projects/kaggle-spaceship-titanic/data/spaceship-titanic
uv run kaggle competitions submit -c spaceship-titanic -f workspace/submission.csv -m "exp-008 hgb tuning hgb_004 cv=0.812261"
```

## Notes For Reviewer

Use `results/scores.json` for exact fold scores and all candidate parameters.
