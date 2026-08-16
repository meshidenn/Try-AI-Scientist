from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold
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


def add_features(train: pd.DataFrame, test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    n_train = len(train)
    y = train["Transported"].copy()
    full = pd.concat([train.drop(columns=["Transported"]), test], ignore_index=True)
    diagnostics: dict[str, int] = {}

    passenger_parts = full["PassengerId"].astype(str).str.split("_", expand=True)
    full["GroupId"] = passenger_parts[0]
    full["GroupPosition"] = pd.to_numeric(passenger_parts[1], errors="coerce")
    full["GroupSize"] = full.groupby("GroupId")["PassengerId"].transform("count")
    full["IsSolo"] = full["GroupSize"].eq(1).astype(int)

    cabin_parts = full["Cabin"].astype(str).str.split("/", expand=True)
    full["CabinDeck"] = cabin_parts[0].replace("nan", float("nan"))
    full["CabinNum"] = pd.to_numeric(cabin_parts[1], errors="coerce")
    full["CabinSide"] = cabin_parts[2].replace("nan", float("nan"))
    full["CabinMissing"] = full["Cabin"].isna().astype(int)

    spend_known = full[SPEND_COLS].sum(axis=1, min_count=1)
    positive_spend_cryo_missing = full["CryoSleep"].isna() & spend_known.gt(0)
    zero_spend_cryo_missing = full["CryoSleep"].isna() & full[SPEND_COLS].fillna(0).sum(axis=1).eq(0)
    diagnostics["cryo_imputed_false_from_positive_spend"] = int(positive_spend_cryo_missing.sum())
    diagnostics["cryo_imputed_true_from_zero_spend"] = int(zero_spend_cryo_missing.sum())
    full.loc[positive_spend_cryo_missing, "CryoSleep"] = False
    full.loc[zero_spend_cryo_missing, "CryoSleep"] = True

    cryo_true = full["CryoSleep"].eq(True)
    for col in SPEND_COLS:
        missing_for_cryo = cryo_true & full[col].isna()
        diagnostics[f"{col}_imputed_zero_for_cryo"] = int(missing_for_cryo.sum())
        full.loc[missing_for_cryo, col] = 0.0

    for col in SPEND_COLS:
        full[f"{col}Missing"] = full[col].isna().astype(int)
    spend = full[SPEND_COLS].fillna(0)
    full["TotalSpend"] = spend.sum(axis=1)
    full["LogTotalSpend"] = np.log1p(full["TotalSpend"])
    full["NoSpend"] = full["TotalSpend"].eq(0).astype(int)
    full["NumSpendCategories"] = spend.gt(0).sum(axis=1)
    full["LuxurySpend"] = spend["Spa"] + spend["VRDeck"] + spend["RoomService"]
    full["BasicSpend"] = spend["FoodCourt"] + spend["ShoppingMall"]
    for col in SPEND_COLS:
        full[f"Log{col}"] = np.log1p(spend[col])
        full[f"{col}Ratio"] = spend[col] / (full["TotalSpend"] + 1.0)

    full["CryoSleepSpendMismatch"] = full["CryoSleep"].fillna(False).astype(bool) & full["TotalSpend"].gt(0)
    full["VIPNoSpend"] = full["VIP"].fillna(False).astype(bool) & full["NoSpend"].astype(bool)
    full["HomePlanetDestination"] = full["HomePlanet"].astype(str) + "__" + full["Destination"].astype(str)
    full["CabinDeckSide"] = full["CabinDeck"].astype(str) + "__" + full["CabinSide"].astype(str)
    full["HomePlanetCabinDeck"] = full["HomePlanet"].astype(str) + "__" + full["CabinDeck"].astype(str)

    full["IsChild"] = full["Age"].lt(12).fillna(False).astype(int)
    full["IsMinor"] = full["Age"].lt(18).fillna(False).astype(int)
    full["Surname"] = full["Name"].apply(lambda value: value.split()[-1] if isinstance(value, str) and value else "Unknown")
    full["FamilySize"] = full.groupby("Surname")["Surname"].transform("count")

    full["Group_TotalSpend_mean"] = full.groupby("GroupId")["TotalSpend"].transform("mean")
    full["Group_Age_mean"] = full.groupby("GroupId")["Age"].transform("mean")
    full["Deck_TotalSpend_mean"] = full.groupby("CabinDeck")["TotalSpend"].transform("mean")
    full["Deck_Age_mean"] = full.groupby("CabinDeck")["Age"].transform("mean")

    for col in ["Age", "CryoSleep", "VIP", "Cabin", "HomePlanet", "Destination", "Name"]:
        full[f"{col}Missing"] = full[col].isna().astype(int)

    drop_cols = ["PassengerId", "Name", "Cabin", "Surname"]
    full = full.drop(columns=drop_cols)
    train_features = full.iloc[:n_train].reset_index(drop=True)
    test_features = full.iloc[n_train:].reset_index(drop=True)
    train_features["Transported"] = y.reset_index(drop=True)
    return train_features, test_features, diagnostics


def build_pipeline(features: pd.DataFrame, params: dict) -> Pipeline:
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
    return Pipeline(
        [
            ("preprocessor", preprocessor),
            ("model", HistGradientBoostingClassifier(random_state=42, **params)),
        ]
    )


def write_results(scores: dict, data_dir: Path) -> None:
    text = f"""# Results

## Summary

Status: completed.

Ran domain imputation and richer spending features with HistGradientBoosting.

## Setup

- Experiment: `exp-009`
- Data: official Kaggle CSV files in `{data_dir}`
- CV: 5-fold StratifiedKFold, random_state=42
- Model: HistGradientBoostingClassifier

## Metrics

| Metric | Value |
| --- | ---: |
| exp-006 CV baseline | {scores["comparison"]["exp_006_cv_accuracy"]:.6f} |
| exp-008 CV baseline | {scores["comparison"]["exp_008_cv_accuracy"]:.6f} |
| exp-009 CV accuracy | {scores["metrics"]["primary"]["value"]:.6f} |
| Delta vs exp-006 CV | {scores["comparison"]["delta_vs_exp_006_cv"]:.6f} |
| Delta vs exp-008 CV | {scores["comparison"]["delta_vs_exp_008_cv"]:.6f} |
| Fold std | {scores["metrics"]["accuracy_std"]:.6f} |

Fold scores: {scores["metrics"]["fold_scores"]}

## Main Results

The domain-imputation feature set scored {scores["metrics"]["primary"]["value"]:.6f}.
OOF and test probabilities were saved for future ensembling.

## Figures

No figures were generated.

## Failures And Negative Results

- Public leaderboard score is not recorded yet.
- This run still uses only one model family.

## Reproduction

```bash
uv run python domain_imputation_hgb.py --data-dir {data_dir}
```

## Notes For Reviewer

Check `results/scores.json` for imputation diagnostics and exact fold scores.
"""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "results.md").write_text(text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--folds", default=5, type=int)
    parser.add_argument("--exp006-cv", default=0.8088104680348149, type=float)
    parser.add_argument("--exp006-public", default=0.80383, type=float)
    parser.add_argument("--exp008-cv", default=0.8122613223609723, type=float)
    parser.add_argument("--exp008-public", default=0.80243, type=float)
    args = parser.parse_args()

    configure_logging()
    data_dir = args.data_dir.resolve()
    raw_train = pd.read_csv(data_dir / "train.csv")
    raw_test = pd.read_csv(data_dir / "test.csv")
    sample = pd.read_csv(data_dir / "sample_submission.csv")
    train, test, diagnostics = add_features(raw_train, raw_test)
    target = train["Transported"].astype(bool)
    train_features = train.drop(columns=["Transported"])
    test_features = test

    params = {
        "learning_rate": 0.04,
        "max_iter": 200,
        "max_leaf_nodes": 31,
        "l2_regularization": 0.0,
        "min_samples_leaf": 20,
    }
    cv = StratifiedKFold(n_splits=args.folds, shuffle=True, random_state=42)
    oof = np.zeros(len(train_features), dtype=float)
    test_prob = np.zeros(len(test_features), dtype=float)
    fold_scores = []
    for fold, (train_idx, valid_idx) in enumerate(cv.split(train_features, target), start=1):
        pipeline = build_pipeline(train_features, params)
        pipeline.fit(train_features.iloc[train_idx], target.iloc[train_idx])
        valid_prob = pipeline.predict_proba(train_features.iloc[valid_idx])[:, 1]
        oof[valid_idx] = valid_prob
        test_prob += pipeline.predict_proba(test_features)[:, 1] / args.folds
        fold_accuracy = accuracy_score(target.iloc[valid_idx], valid_prob >= 0.5)
        fold_scores.append(float(fold_accuracy))
        logging.info("fold %d accuracy %.6f", fold, fold_accuracy)

    cv_mean = float(np.mean(fold_scores))
    cv_std = float(np.std(fold_scores))
    submission = sample.copy()
    submission["Transported"] = (test_prob >= 0.5).astype(bool)
    submission_path = ROOT / "submission.csv"
    submission.to_csv(submission_path, index=False)

    pd.DataFrame(
        {
            "PassengerId": raw_train["PassengerId"],
            "Transported": target,
            "oof_probability": oof,
            "oof_prediction": oof >= 0.5,
        }
    ).to_csv(ROOT / "oof_predictions.csv", index=False)
    pd.DataFrame(
        {
            "PassengerId": raw_test["PassengerId"],
            "test_probability": test_prob,
            "prediction": test_prob >= 0.5,
        }
    ).to_csv(ROOT / "test_probabilities.csv", index=False)

    scores = {
        "experiment_id": "exp-009",
        "status": "completed",
        "benchmark": "spaceship-titanic",
        "data_kind": "official_kaggle",
        "model": "HistGradientBoostingClassifier",
        "params": params,
        "feature_count": int(train_features.shape[1]),
        "imputation_diagnostics": diagnostics,
        "metrics": {
            "primary": {
                "name": "cross_validated_accuracy",
                "value": cv_mean,
                "higher_is_better": True,
            },
            "accuracy_std": cv_std,
            "fold_scores": fold_scores,
            "fold_count": int(args.folds),
            "public_leaderboard_score": None,
            "private_leaderboard_score": None,
            "oof_positive_rate": float((oof >= 0.5).mean()),
            "test_positive_rate": float((test_prob >= 0.5).mean()),
        },
        "comparison": {
            "exp_006_cv_accuracy": float(args.exp006_cv),
            "exp_006_public_score": float(args.exp006_public),
            "exp_008_cv_accuracy": float(args.exp008_cv),
            "exp_008_public_score": float(args.exp008_public),
            "delta_vs_exp_006_cv": float(cv_mean - args.exp006_cv),
            "delta_vs_exp_008_cv": float(cv_mean - args.exp008_cv),
        },
        "submission_rows": int(len(submission)),
        "artifacts": {
            "results_md": "results/results.md",
            "scores_json": "results/scores.json",
            "submission_csv": "workspace/submission.csv",
            "oof_predictions": "workspace/oof_predictions.csv",
            "test_probabilities": "workspace/test_probabilities.csv",
            "run_log": "logs/run.log",
        },
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "scores.json").write_text(json.dumps(scores, indent=2) + "\n")
    write_results(scores, data_dir)
    logging.info("CV mean %.6f std %.6f", cv_mean, cv_std)
    logging.info("Wrote %s", submission_path)


if __name__ == "__main__":
    main()
