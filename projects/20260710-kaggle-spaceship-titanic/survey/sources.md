# Sources

| Source | URL | Notes |
| --- | --- | --- |
| Kaggle Spaceship Titanic | https://www.kaggle.com/competitions/spaceship-titanic | Primary benchmark. Page metadata describes the task as predicting transported passengers. Accessed 2026-06-30. |
| Kaggle Spaceship Titanic Data | https://www.kaggle.com/competitions/spaceship-titanic/data | Official data page for train/test/submission files. Accessed 2026-06-30. |
| Kaggle Spaceship Titanic Evaluation | https://www.kaggle.com/competitions/spaceship-titanic/overview/evaluation | Official evaluation page. Accessed 2026-06-30. |
| Kaggle Titanic | https://www.kaggle.com/competitions/titanic | Simpler alternative considered. Accessed 2026-06-30. |
| Kaggle House Prices | https://www.kaggle.com/competitions/house-prices-advanced-regression-techniques | Regression alternative considered. Accessed 2026-06-30. |
| scikit-learn HistGradientBoostingClassifier docs | https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingClassifier.html | Documents native missing-value handling and categorical feature support. Accessed 2026-06-30. |
| LightGBM Features docs | https://lightgbm.readthedocs.io/en/stable/Features.html | Documents leaf-wise tree growth and categorical split handling. Accessed 2026-06-30. |
| CatBoost categorical feature docs | https://catboost.ai/docs/en/concepts/algorithm-main-stages_cat-to-numberic | Documents categorical feature transformation strategy. Accessed 2026-06-30. |
| CatBoost paper | https://arxiv.org/abs/1706.09516 | Describes ordered boosting and categorical handling; relevant if adding CatBoost as a candidate model. Accessed 2026-06-30. |
| Kaggle notebook: Spaceship Titanic Feature Engineering LGBM | https://www.kaggle.com/code/krishnaharish1/spaceship-titanic-feature-engineering-lgbm | Read via Kaggle API. Emphasizes CryoSleep/zero-spend imputation, group/cabin/spending features, LightGBM with CV. Accessed 2026-07-03. |
| Kaggle discussion: CryoSleep / zero-spend rule | https://www.kaggle.com/competitions/spaceship-titanic/discussion/716052 | Read via Kaggle API. States CryoSleep passengers have zero amenity spend in train and suggests bidirectional imputation. Accessed 2026-07-03. |
| Kaggle notebook: Agents Grading Agents Spaceship Titanic MLE-bench | https://www.kaggle.com/code/georgymamarin/agents-grading-agents-spaceship-titanic-mle-bench | Read via Kaggle API. Uses engineered features, CatBoost/LightGBM/XGBoost, 10-fold OOF, weighted averaging/stacking, and leakage diagnostics. Accessed 2026-07-03. |
| Kaggle discussion: autonomous agent score variance | https://www.kaggle.com/competitions/spaceship-titanic/discussion/712563 | Read via Kaggle API. Reports same agent setup varying from 0.80230 to 0.82069 and highlights provenance/reproducibility risk. Accessed 2026-07-03. |
| Kaggle notebook: LGBM 0.8066 Score Top 7% Solution | https://www.kaggle.com/code/fernaandodantas/lgbm-0-8066-score-top-7-solution | Read via Kaggle API. Uses cabin split, KNN imputation, target encoding, and LightGBM tuning. Accessed 2026-07-03. |
| Kaggle notebook: Spaceship Titanic with TFDF | https://www.kaggle.com/code/gusthema/spaceship-titanic-with-tfdf | Read via Kaggle API. Demonstrates TensorFlow Decision Forests baseline, cabin split, and simple fill rules. Accessed 2026-07-03. |
