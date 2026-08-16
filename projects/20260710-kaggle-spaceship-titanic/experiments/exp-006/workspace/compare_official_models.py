from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder


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


def split_features(features: pd.DataFrame) -> tuple[list[str], list[str]]:
    numeric_features = features.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical_features = [col for col in features.columns if col not in numeric_features]
    return numeric_features, categorical_features


def onehot_preprocessor(features: pd.DataFrame) -> ColumnTransformer:
    numeric_features, categorical_features = split_features(features)
    return ColumnTransformer(
        transformers=[
            ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median"))]), numeric_features),
            (
                "categorical",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_features,
            ),
        ]
    )


def ordinal_preprocessor(features: pd.DataFrame) -> ColumnTransformer:
    numeric_features, categorical_features = split_features(features)
    return ColumnTransformer(
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


def build_candidates(features: pd.DataFrame) -> dict[str, Pipeline]:
    return {
        "random_forest": Pipeline(
            [
                ("preprocessor", onehot_preprocessor(features)),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=500,
                        min_samples_leaf=2,
                        random_state=42,
                        n_jobs=1,
                    ),
                ),
            ]
        ),
        "extra_trees": Pipeline(
            [
                ("preprocessor", onehot_preprocessor(features)),
                (
                    "model",
                    ExtraTreesClassifier(
                        n_estimators=500,
                        min_samples_leaf=2,
                        random_state=42,
                        n_jobs=1,
                    ),
                ),
            ]
        ),
        "hist_gradient_boosting": Pipeline(
            [
                ("preprocessor", ordinal_preprocessor(features)),
                (
                    "model",
                    HistGradientBoostingClassifier(
                        max_iter=250,
                        learning_rate=0.05,
                        max_leaf_nodes=31,
                        l2_regularization=0.01,
                        random_state=42,
                    ),
                ),
            ]
        ),
    }


def write_results(scores: dict, data_dir: Path) -> None:
    rows = "\n".join(
        f"| {name} | {item['accuracy_mean']:.6f} | {item['accuracy_std']:.6f} |"
        for name, item in scores["metrics"]["candidates"].items()
    )
    best = scores["selected_model"]
    baseline = scores["comparison"]["exp_005_accuracy_mean"]
    delta = scores["metrics"]["primary"]["value"] - baseline
    text = f"""# Results

## Summary

Status: completed.

Ran official-data feature bundle and model comparison.

## Setup

- Experiment: `exp-006`
- Data: official Kaggle CSV files in `{data_dir}`
- Feature bundle: group, cabin, spending, missingness, and categorical combinations
- CV: 5-fold StratifiedKFold, random_state=42

## Metrics

| Candidate | CV Accuracy Mean | CV Accuracy Std |
| --- | ---: | ---: |
{rows}

Selected model: `{best}`

exp-005 baseline accuracy: {baseline:.6f}

Delta versus exp-005: {delta:.6f}

## Main Results

Best official-data CV accuracy in this run is {scores["metrics"]["primary"]["value"]:.6f}.
The selected model wrote a valid submission with {scores["submission_rows"]} rows.

## Figures

No figures were generated.

## Failures And Negative Results

- Public leaderboard score is not recorded yet.
- HistGradientBoosting uses ordinal-encoded categoricals here, not native categorical dtypes.

## Reproduction

```bash
uv run python compare_official_models.py --data-dir {data_dir}
```

## Notes For Reviewer

Compare claims against `results/scores.json`; do not infer leaderboard accuracy.
"""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "results.md").write_text(text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--folds", default=5, type=int)
    parser.add_argument("--exp005-score", required=True, type=float)
    args = parser.parse_args()

    configure_logging()
    data_dir = args.data_dir.resolve()
    train = add_feature_bundle(pd.read_csv(data_dir / "train.csv"))
    test = add_feature_bundle(pd.read_csv(data_dir / "test.csv"))
    sample = pd.read_csv(data_dir / "sample_submission.csv")
    target = train["Transported"].astype(bool)

    drop_cols = ["Transported", "Name", "PassengerId", "Cabin"]
    feature_cols = [col for col in train.columns if col not in drop_cols]
    train_features = train[feature_cols]
    test_features = test[feature_cols]

    majority_baseline = max(target.mean(), 1 - target.mean())
    cv = StratifiedKFold(n_splits=args.folds, shuffle=True, random_state=42)
    candidates = build_candidates(train_features)
    candidate_scores: dict[str, dict] = {}
    for name, pipeline in candidates.items():
        scores = cross_val_score(pipeline, train_features, target, cv=cv, scoring="accuracy", n_jobs=1)
        candidate_scores[name] = {
            "accuracy_mean": float(scores.mean()),
            "accuracy_std": float(scores.std()),
            "fold_scores": [float(score) for score in scores],
        }
        logging.info("%s CV accuracy scores: %s", name, scores.tolist())

    selected_model = max(candidate_scores, key=lambda name: candidate_scores[name]["accuracy_mean"])
    selected_pipeline = candidates[selected_model]
    selected_pipeline.fit(train_features, target)
    submission = sample.copy()
    submission["Transported"] = selected_pipeline.predict(test_features).astype(bool)
    submission_path = ROOT / "submission.csv"
    submission.to_csv(submission_path, index=False)

    scores = {
        "experiment_id": "exp-006",
        "status": "completed",
        "benchmark": "spaceship-titanic",
        "data_kind": "official_kaggle",
        "selected_model": selected_model,
        "metrics": {
            "primary": {
                "name": "cross_validated_accuracy",
                "value": candidate_scores[selected_model]["accuracy_mean"],
                "higher_is_better": True,
            },
            "majority_baseline_accuracy": float(majority_baseline),
            "candidates": candidate_scores,
            "fold_count": int(args.folds),
            "public_leaderboard_score": None,
        },
        "comparison": {
            "exp_005_accuracy_mean": float(args.exp005_score),
            "delta_vs_exp_005": float(candidate_scores[selected_model]["accuracy_mean"] - args.exp005_score),
        },
        "submission_rows": int(len(submission)),
        "artifacts": {
            "results_md": "results/results.md",
            "scores_json": "results/scores.json",
            "submission_csv": "workspace/submission.csv",
            "run_log": "logs/run.log",
        },
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "scores.json").write_text(json.dumps(scores, indent=2) + "\n")
    write_results(scores, data_dir)
    logging.info("Selected model: %s", selected_model)
    logging.info("Wrote %s", submission_path)


if __name__ == "__main__":
    main()
