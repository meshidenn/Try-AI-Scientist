# Survey Changelog

## 2026-06-30

- Created initial benchmark choice.
- Selected Spaceship Titanic as the first validation target because it is small,
  scorable, and suitable for an end-to-end artifact workflow test.
- Expanded the survey from benchmark selection to official-data modeling
  strategy.
- Added feature engineering, missing-value, validation, model comparison, and
  next-experiment recommendations.
- Added sources for scikit-learn HistGradientBoosting, LightGBM, CatBoost docs,
  and CatBoost paper.

## 2026-07-03

- Added post-exp-008 survey update focused on how to improve beyond public score
  0.803830.
- Added Kaggle notebook/discussion sources for CryoSleep imputation, LightGBM,
  CatBoost/LightGBM/XGBoost stacking, threshold tuning, and reproducibility
  concerns.
- Updated experiment implications: next steps should prioritize domain
  imputation, richer spending features, GBDT diversity, OOF ensembling, and
  threshold calibration rather than another small single-model tune.
