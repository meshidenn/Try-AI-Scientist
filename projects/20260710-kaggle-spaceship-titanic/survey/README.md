# Kaggle Spaceship Titanic Survey

## Research Question

How should this project approach Kaggle Spaceship Titanic so that, once the
official CSV files are available, agents can improve accuracy through
evidence-based cross-validation rather than ad hoc leaderboard chasing?

Secondary question: can this benchmark validate the repository workflow
(`survey -> spec -> experiment -> audit -> interpretation -> claims -> archive`)
while still being realistic enough to exercise useful tabular ML choices?

## Current Understanding

Spaceship Titanic is a small Kaggle tabular binary classification task. Kaggle
describes the objective as predicting which passengers were transported to an
alternate dimension. It is a good first benchmark because it is cheap to run
locally, has mixed numeric and categorical columns, has missing values, and
requires a Kaggle-shaped submission file.

The task likely rewards three kinds of work:

- domain-shaped feature engineering from structured identifiers,
- careful missing-value handling,
- tree boosting or tree ensembles that handle nonlinear interactions.

Current local experiments are synthetic fixture runs only. They validate the
workflow but do not establish real Kaggle performance.

As of exp-008, this project has official-data results:

- exp-006 is the current public leaderboard baseline: local CV 0.808810, public
  score 0.803830.
- exp-008 improved local CV to 0.812261, but public score dropped to 0.802430.

This means the next improvements should not chase tiny local CV gains alone.
They should improve robustness, diversify models, or improve probability
calibration before another submission.

## Relevant Prior Work

### Benchmark selection

Compared with other quick Kaggle choices:

- Titanic is very small and well known, but it may be too toy-like to stress the
  workflow.
- House Prices is also a good candidate, but regression metrics and feature
  engineering choices make the first pass slightly heavier.
- Spaceship Titanic keeps the first pass simple while still requiring missing
  value handling, categorical features, grouped identifiers, and a submission
  file.

### Model families

For the first official-data experiments, the highest-value candidates are:

- `RandomForestClassifier` / `ExtraTreesClassifier`: strong baseline for mixed
  tabular data after simple imputation and one-hot encoding.
- `HistGradientBoostingClassifier`: attractive because scikit-learn documents
  native handling of `NaN` values and categorical feature support via dataframe
  categorical dtypes.
- LightGBM: relevant because its docs emphasize leaf-wise tree growth and
  categorical splitting without relying only on one-hot encoding.
- CatBoost: relevant because it is designed around categorical feature handling
  and ordered target-statistic style transformations, which match this dataset's
  many categorical columns.

CatBoost and LightGBM should be treated as optional dependencies. Start with
scikit-learn-only experiments for easy reproducibility, then add external
boosters if the official-data CV baseline is stable.

Recent Kaggle community work points in the same direction. Stronger public
solutions often use GBDT diversity rather than a single tuned model: CatBoost,
LightGBM, and XGBoost with fold-averaged predictions, then either weighted
averaging or a simple stacking layer. A public walkthrough reports a reproducible
stacking CV around 0.8138, with CatBoost, LightGBM, and XGBoost each close to
one another. This is directly relevant because our exp-008 single-model tuning
already shows a small CV gain can fail to transfer to public leaderboard.

## Methods And Design Ideas

### Feature engineering candidates

Use official train/test columns only. Candidate features:

- `PassengerId`:
  - `GroupId`
  - `GroupPosition`
  - `GroupSize`
  - group-level aggregates, such as number of passengers sharing the same group
- `Cabin`:
  - `CabinDeck`
  - `CabinNum`
  - `CabinSide`
  - missing cabin flag
- spending columns:
  - `TotalSpend = RoomService + FoodCourt + ShoppingMall + Spa + VRDeck`
  - `NoSpend = TotalSpend == 0`
  - per-spending missing flags
  - luxury/service splits, for example `LuxurySpend = Spa + VRDeck`
- consistency flags:
  - `CryoSleep` with positive spending
  - `VIP` with no spending
  - missingness patterns, such as all spending columns missing
- categorical combinations:
  - `HomePlanet + Destination`
  - `CabinDeck + CabinSide`
  - `HomePlanet + CabinDeck`

Additional high-priority candidates from public notebooks:

- spending profile features:
  - `LogTotalSpend`
  - log transforms of each spend column
  - `NumSpendCategories`
  - per-category spend ratios, such as `Spa / (TotalSpend + 1)`
  - `LuxurySpend = Spa + VRDeck + RoomService`
  - `BasicSpend = FoodCourt + ShoppingMall`
- age/name/group features:
  - `IsChild`, `IsMinor`
  - surname extracted from `Name`
  - `FamilySize` by surname
  - `IsSolo` from passenger group
- aggregate features:
  - group-level mean spend and age
  - deck-level mean spend

Aggregate features must be handled carefully. They may introduce mild leakage if
computed on the full train set before CV. One public analysis measured this with
StratifiedKFold vs GroupKFold and in-fold aggregate recomputation, finding the
effect small on this task, but this project should still record whether
aggregates are full-data or in-fold.

The first feature experiment should be deliberately small:

1. baseline derived features: `GroupSize`, cabin split, `TotalSpend`, `NoSpend`,
2. missing indicators for high-missingness columns,
3. compare RandomForest, ExtraTrees, and HistGradientBoosting under identical
   folds.

### Missing-value strategy

Do not silently drop rows. Missingness is likely informative.

Recommended staged comparison:

- Simple baseline: median numeric imputation and most-frequent categorical
  imputation, plus missing indicators.
- HistGradientBoosting variant: preserve `NaN` where possible and use categorical
  dtypes.
- CatBoost variant: pass categorical columns directly and let CatBoost handle
  categorical transformations.

Add a domain-logic imputation experiment before more model tuning:

- If `CryoSleep == True`, missing spend values should be imputed to 0.
- If all known spend columns sum to 0 and `CryoSleep` is missing, impute
  `CryoSleep = True`.
- If any spend column is positive and `CryoSleep` is missing, impute
  `CryoSleep = False`.

This rule is explicitly discussed in recent Kaggle topics and notebooks and is
stronger than generic median/mode imputation because it follows the competition
data semantics.

### Validation strategy

Use 5-fold CV first. Record:

- fold scores,
- mean and standard deviation,
- exact fold splitter,
- random seed,
- feature set version,
- model and important hyperparameters.

Use `StratifiedKFold` for the first official-data baseline. Then add a
group-aware diagnostic split using `GroupKFold` or `StratifiedGroupKFold` with
`GroupId`. This checks whether the model is relying on group leakage. If
StratifiedKFold is much higher than group-aware CV, leaderboard expectations
should be conservative.

### Hyperparameter search

Keep the first search small and auditable:

- RandomForest / ExtraTrees:
  - `n_estimators`
  - `max_depth`
  - `min_samples_leaf`
  - `max_features`
- HistGradientBoosting:
  - `learning_rate`
  - `max_iter`
  - `max_leaf_nodes`
  - `l2_regularization`
  - `min_samples_leaf`
- LightGBM / CatBoost if added:
  - learning rate and number of iterations,
  - tree depth / leaves,
  - regularization,
  - early stopping on CV folds.

Avoid a large search before the feature pipeline and validation split are
stable.

exp-008 shows that a small single-model search can overfit local CV: local CV
increased by 0.003451, but public score decreased by 0.001400. Future searches
should add robustness criteria:

- compare candidate fold standard deviation, not only mean;
- prefer candidates that also hold up under group-aware CV;
- submit only when local CV margin is large enough or model diversity changes;
- preserve OOF probabilities for blending/stacking.

### Ensembling and post-processing

The next likely gain is not another tiny single-model tune. Higher-value
directions:

- 10-fold prediction averaging for the selected model family.
- Weighted blend of CatBoost, LightGBM, XGBoost, and current HistGradientBoosting.
- Stacking with OOF probabilities and a simple logistic meta-learner.
- Threshold tuning using OOF probabilities and predicted positive-rate
  diagnostics.

Threshold tuning should be treated as a separate experiment because it can
easily overfit public leaderboard feedback. Compare thresholds on OOF accuracy
first, then record the predicted positive rate on test before submission.

## Evaluation And Benchmarks

Primary local metric: cross-validated accuracy.

Kaggle metric: public leaderboard accuracy after submission.

Minimum evidence before claiming improvement:

- compare against majority baseline,
- compare against the current RandomForest baseline,
- use identical folds for candidate comparisons,
- write `scores.json` with per-fold scores,
- write `claims.json` that separates local CV claims from Kaggle leaderboard
  claims.

Leaderboard score should not replace CV. The leaderboard is useful as an
external check, but the repository should optimize by reproducible local
experiments first.

## Risks And Open Questions

- Current experiments are synthetic; real-data behavior may differ.
- Public leaderboard feedback can overfit if used too often.
- Group-derived features may create optimistic CV if related passengers are split
  across train and validation folds.
- CatBoost and LightGBM may improve accuracy, but they add dependencies and
  platform-specific friction. Add them only through `uv add` and document the
  change in the experiment spec.
- If the official data has subtle missingness or categorical cardinality issues,
  one-hot pipelines may be weaker than categorical-native boosters.

## Implications For Experiments

Recommended next experiments after official CSV files are placed:

1. `exp-005`: official-data baseline with current RandomForest pipeline.
2. `exp-006`: feature-engineering bundle: `TotalSpend`, `NoSpend`, cabin split,
   group size, missing indicators.
3. `exp-007`: model comparison under identical folds: RandomForest, ExtraTrees,
   HistGradientBoosting.
4. `exp-008`: group-aware CV diagnostic using `GroupId`.
5. `exp-009`: optional CatBoost or LightGBM comparison, added via `uv add`.

Do not make a real Kaggle performance claim until at least `exp-005` has an
official-data CV score and a public leaderboard score.

Updated next experiments after exp-008:

1. `exp-009`: domain imputation + richer spending profile features with
   HistGradientBoosting, no new dependency.
2. `exp-010`: add LightGBM through `uv add lightgbm`; use 5- or 10-fold OOF,
   early stopping, and the richer feature set.
3. `exp-011`: add CatBoost and optionally XGBoost; compare three GBDTs under the
   same folds.
4. `exp-012`: weighted average and stacking from OOF probabilities.
5. `exp-013`: threshold tuning / predicted-positive-rate calibration.

Public submission rule: keep exp-006 public score 0.803830 as the baseline.
Submit only if the experiment changes model family/ensemble strategy, or if CV
improves with lower fold variance and group-aware diagnostic support.

## Sources

See `sources.md` for source table and access dates.
