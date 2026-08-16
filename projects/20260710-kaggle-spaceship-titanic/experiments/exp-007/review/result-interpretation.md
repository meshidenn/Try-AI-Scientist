# Result Interpretation

## Summary

exp-007 compared ordinary StratifiedKFold with StratifiedGroupKFold using
PassengerId group IDs for the exp-006 selected HistGradientBoosting setup.

## Supported Findings

- Ordinary stratified CV accuracy was 0.808810.
- Group-aware CV accuracy was 0.805015.
- The gap was 0.003796.

## Limitations

- Group-aware CV does not reproduce the hidden Kaggle split.
- No leaderboard score is recorded.

## Interpretation

The small gap suggests that the exp-006 local CV score is not heavily inflated
by splitting passenger groups across folds. This increases confidence in the
local CV improvement, while still not proving leaderboard performance.
