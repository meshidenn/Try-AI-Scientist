# Results

## Summary

Status: completed.

Ran the RandomForest baseline on official Kaggle Spaceship Titanic data.

## Setup

- Experiment: `exp-005`
- Data: official Kaggle CSV files in `/Users/hiroki-iida/works/Try-AI-Scientist/projects/kaggle-spaceship-titanic/data/spaceship-titanic`
- Model: RandomForestClassifier
- Evaluation: 5-fold StratifiedKFold, random_state=42

## Metrics

| Metric | Value |
| --- | ---: |
| Majority baseline accuracy | 0.503624 |
| CV accuracy mean | 0.744276 |
| CV accuracy std | 0.006141 |
| Improvement over majority | 0.240652 |
| Train accuracy | 0.748303 |

Fold scores: [0.7538815411155837, 0.7429557216791259, 0.7481311098332375, 0.7399309551208285, 0.7364787111622555]

## Main Results

The official-data baseline CV accuracy is 0.744276.
The model produced a valid submission file with 4277 rows.

## Figures

No figures were generated.

## Failures And Negative Results

- Public leaderboard score is not recorded yet.
- This run uses a single model family.

## Reproduction

```bash
uv run python train_official_baseline.py --data-dir /Users/hiroki-iida/works/Try-AI-Scientist/projects/kaggle-spaceship-titanic/data/spaceship-titanic
```

## Notes For Reviewer

This is the first official-data local CV baseline and should be the comparison
anchor for follow-up experiments.
