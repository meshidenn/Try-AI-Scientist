# Results

## Summary

Status: completed.

Compared ordinary stratified CV with group-aware CV using PassengerId groups.

## Setup

- Experiment: `exp-007`
- Data: official Kaggle CSV files in `/Users/hiroki-iida/works/Try-AI-Scientist/projects/kaggle-spaceship-titanic/data/spaceship-titanic`
- Model: HistGradientBoostingClassifier with exp-006 feature bundle
- Splitters: StratifiedKFold and StratifiedGroupKFold

## Metrics

| Splitter | CV Accuracy Mean | CV Accuracy Std |
| --- | ---: | ---: |
| StratifiedKFold | 0.808810 | 0.007786 |
| StratifiedGroupKFold | 0.805015 | 0.005506 |

Gap, stratified minus group-aware: 0.003796

## Main Results

The group-aware score is 0.805015.
The gap is 0.003796.

## Figures

No figures were generated.

## Failures And Negative Results

- This is a diagnostic run; no submission file was produced.
- Group-aware CV is not necessarily the leaderboard split, but it is useful for leakage checks.

## Reproduction

```bash
uv run python group_cv_diagnostic.py --data-dir /Users/hiroki-iida/works/Try-AI-Scientist/projects/kaggle-spaceship-titanic/data/spaceship-titanic
```

## Notes For Reviewer

Use this result to calibrate confidence in StratifiedKFold scores from exp-005
and exp-006.
