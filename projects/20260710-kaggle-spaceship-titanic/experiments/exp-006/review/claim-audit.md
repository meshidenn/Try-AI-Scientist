# Claim Audit

## Verdict

PASS WITH LIMITATION

## Checked Claims

- Local CV improvement over exp-005: supported by `results/scores.json`.
- HistGradientBoosting selected: supported by candidate scores.
- Public leaderboard score: supported by Kaggle submission metadata in `results/scores.json`.
- Private leaderboard score: unsupported because it is not available.

## Notes

The local improvement claim is valid for 5-fold StratifiedKFold CV. The public
leaderboard score is directly recorded, but there is no exp-005 public score for
a public-leaderboard delta claim.
