# Result Interpretation

## Summary

exp-006 added the survey-recommended feature bundle and compared three
scikit-learn models on official Kaggle data.

## Supported Findings

- exp-005 baseline CV accuracy was 0.744276.
- RandomForest with the expanded feature bundle scored 0.740020.
- ExtraTrees scored 0.756814.
- HistGradientBoosting scored 0.808810 and was selected.
- The best local CV improvement over exp-005 was 0.064535.
- The selected model produced a valid local submission file.
- Kaggle accepted submission ref `54281125` with public score 0.803830.

## Limitations

- Private leaderboard score is not available.
- The HistGradientBoosting categorical treatment is ordinal encoding, so a future native-categorical or CatBoost/LightGBM run may differ.

## Interpretation

The feature/model change materially improved local CV accuracy. The largest gain
came from moving to HistGradientBoosting, not from RandomForest with the added
feature bundle. The public score of 0.803830 is close to the 0.808810 local CV
score, so the local validation estimate appears reasonably calibrated for this
submission.
