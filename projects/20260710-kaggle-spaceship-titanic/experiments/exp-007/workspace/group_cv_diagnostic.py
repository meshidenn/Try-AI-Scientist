from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder


ROOT = Path(__file__).resolve().parent
EXP_DIR = ROOT.parent
RESULTS_DIR = EXP_DIR / "results"
LOGS_DIR = EXP_DIR / "logs"
SPEND_COLS = ["RoomService", "FoodCourt", "ShoppingMall", "Spa", "VRDeck"]


def configure_logging() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(LOGS_DIR / "run.log", mode="w"), logging.StreamHandler()],
    )


def add_feature_bundle(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    passenger_parts = out["PassengerId"].astype(str).str.split("_", expand=True)
    out["GroupId"] = passenger_parts[0]
    out["GroupPosition"] = pd.to_numeric(passenger_parts[1], errors="coerce")
    out["GroupSize"] = out.groupby("GroupId")["PassengerId"].transform("count")
    cabin_parts = out["Cabin"].astype(str).str.split("/", expand=True)
    out["CabinDeck"] = cabin_parts[0].replace("nan", float("nan"))
    out["CabinNum"] = pd.to_numeric(cabin_parts[1], errors="coerce")
    out["CabinSide"] = cabin_parts[2].replace("nan", float("nan"))
    out["CabinMissing"] = out["Cabin"].isna()
    for col in SPEND_COLS:
        out[f"{col}Missing"] = out[col].isna()
    spend = out[SPEND_COLS].fillna(0)
    out["TotalSpend"] = spend.sum(axis=1)
    out["NoSpend"] = out["TotalSpend"].eq(0)
    out["LuxurySpend"] = spend["Spa"] + spend["VRDeck"]
    out["ServiceSpend"] = spend["RoomService"] + spend["FoodCourt"] + spend["ShoppingMall"]
    out["CryoSleepSpendMismatch"] = out["CryoSleep"].fillna(False).astype(bool) & out["TotalSpend"].gt(0)
    out["VIPNoSpend"] = out["VIP"].fillna(False).astype(bool) & out["NoSpend"]
    out["HomePlanetDestination"] = out["HomePlanet"].astype(str) + "__" + out["Destination"].astype(str)
    out["CabinDeckSide"] = out["CabinDeck"].astype(str) + "__" + out["CabinSide"].astype(str)
    return out


def build_hist_gradient_boosting(features: pd.DataFrame) -> Pipeline:
    numeric_features = features.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical_features = [col for col in features.columns if col not in numeric_features]
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median"))]), numeric_features),
            (
                "categorical",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        (
                            "ordinal",
                            OrdinalEncoder(
                                handle_unknown="use_encoded_value",
                                unknown_value=-1,
                            ),
                        ),
                    ]
                ),
                categorical_features,
            ),
        ]
    )
    model = HistGradientBoostingClassifier(
        max_iter=250,
        learning_rate=0.05,
        max_leaf_nodes=31,
        l2_regularization=0.01,
        random_state=42,
    )
    return Pipeline([("preprocessor", preprocessor), ("model", model)])


def write_results(scores: dict, data_dir: Path) -> None:
    text = f"""# Results

## Summary

Status: completed.

Compared ordinary stratified CV with group-aware CV using PassengerId groups.

## Setup

- Experiment: `exp-007`
- Data: official Kaggle CSV files in `{data_dir}`
- Model: HistGradientBoostingClassifier with exp-006 feature bundle
- Splitters: StratifiedKFold and StratifiedGroupKFold

## Metrics

| Splitter | CV Accuracy Mean | CV Accuracy Std |
| --- | ---: | ---: |
| StratifiedKFold | {scores["metrics"]["stratified"]["accuracy_mean"]:.6f} | {scores["metrics"]["stratified"]["accuracy_std"]:.6f} |
| StratifiedGroupKFold | {scores["metrics"]["stratified_group"]["accuracy_mean"]:.6f} | {scores["metrics"]["stratified_group"]["accuracy_std"]:.6f} |

Gap, stratified minus group-aware: {scores["metrics"]["gap_stratified_minus_group"]:.6f}

## Main Results

The group-aware score is {scores["metrics"]["stratified_group"]["accuracy_mean"]:.6f}.
The gap is {scores["metrics"]["gap_stratified_minus_group"]:.6f}.

## Figures

No figures were generated.

## Failures And Negative Results

- This is a diagnostic run; no submission file was produced.
- Group-aware CV is not necessarily the leaderboard split, but it is useful for leakage checks.

## Reproduction

```bash
uv run python group_cv_diagnostic.py --data-dir {data_dir}
```

## Notes For Reviewer

Use this result to calibrate confidence in StratifiedKFold scores from exp-005
and exp-006.
"""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "results.md").write_text(text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--folds", default=5, type=int)
    args = parser.parse_args()

    configure_logging()
    data_dir = args.data_dir.resolve()
    train = add_feature_bundle(pd.read_csv(data_dir / "train.csv"))
    target = train["Transported"].astype(bool)
    groups = train["GroupId"].astype(str)
    drop_cols = ["Transported", "Name", "PassengerId", "Cabin"]
    feature_cols = [col for col in train.columns if col not in drop_cols]
    features = train[feature_cols]
    pipeline = build_hist_gradient_boosting(features)

    stratified = StratifiedKFold(n_splits=args.folds, shuffle=True, random_state=42)
    stratified_group = StratifiedGroupKFold(n_splits=args.folds, shuffle=True, random_state=42)
    stratified_scores = cross_val_score(pipeline, features, target, cv=stratified, scoring="accuracy", n_jobs=1)
    group_scores = cross_val_score(
        pipeline,
        features,
        target,
        cv=stratified_group,
        groups=groups,
        scoring="accuracy",
        n_jobs=1,
    )
    logging.info("Stratified scores: %s", stratified_scores.tolist())
    logging.info("StratifiedGroup scores: %s", group_scores.tolist())

    scores = {
        "experiment_id": "exp-007",
        "status": "completed",
        "benchmark": "spaceship-titanic",
        "data_kind": "official_kaggle",
        "metrics": {
            "primary": {
                "name": "gap_stratified_minus_group",
                "value": float(stratified_scores.mean() - group_scores.mean()),
                "higher_is_better": False,
            },
            "stratified": {
                "accuracy_mean": float(stratified_scores.mean()),
                "accuracy_std": float(stratified_scores.std()),
                "fold_scores": [float(score) for score in stratified_scores],
            },
            "stratified_group": {
                "accuracy_mean": float(group_scores.mean()),
                "accuracy_std": float(group_scores.std()),
                "fold_scores": [float(score) for score in group_scores],
            },
            "gap_stratified_minus_group": float(stratified_scores.mean() - group_scores.mean()),
            "fold_count": int(args.folds),
        },
        "model": "HistGradientBoostingClassifier",
        "artifacts": {
            "results_md": "results/results.md",
            "scores_json": "results/scores.json",
            "run_log": "logs/run.log",
        },
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "scores.json").write_text(json.dumps(scores, indent=2) + "\n")
    write_results(scores, data_dir)


if __name__ == "__main__":
    main()
