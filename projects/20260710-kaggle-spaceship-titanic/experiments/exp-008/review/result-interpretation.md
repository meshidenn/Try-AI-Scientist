# Result Interpretation

## Summary

exp-008 ran a 36-candidate HistGradientBoosting hyperparameter search. The best
candidate improved local CV but did not improve the Kaggle public leaderboard.

## Supported Findings

- exp-006 CV baseline was 0.808810.
- exp-006 public leaderboard baseline was 0.803830.
- exp-008 selected `hgb_004`.
- `hgb_004` CV accuracy was 0.812261.
- exp-008 improved local CV by 0.003451.
- exp-008 public leaderboard score was 0.802430.
- exp-008 public score was 0.001400 lower than exp-006.

## Limitations

- The public leaderboard score is only one external split.
- Private leaderboard score is not available.
- The selected candidate has higher fold variance than several nearby candidates.

## Interpretation

The tuning run shows a small local CV gain that did not transfer to the public
leaderboard. For the current leaderboard baseline, exp-006 remains better. The
next search should either use public-score feedback sparingly or add a more
robust validation criterion, such as favoring candidates with lower fold
variance or checking group-aware CV for tuned candidates.
