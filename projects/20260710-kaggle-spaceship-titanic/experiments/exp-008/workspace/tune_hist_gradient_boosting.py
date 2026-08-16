from __future__ import annotations

import argparse
import itertools
import json
import logging
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedKFold, cross_val_score
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
    model = HistGradientBoostingClassifier(random_state=42, **params)
    return Pipeline([("preprocessor", preprocessor), ("model", model)])


def candidate_grid() -> list[dict]:
    grid = {
        "learning_rate": [0.04, 0.05, 0.06],
        "max_iter": [200, 300],
        "max_leaf_nodes": [15, 31],
        "l2_regularization": [0.0, 0.01, 0.05],
        "min_samples_leaf": [20],
    }
    keys = list(grid)
    return [dict(zip(keys, values)) for values in itertools.product(*(grid[key] for key in keys))]


def write_results(scores: dict, data_dir: Path) -> None:
    top_rows = "\n".join(
        "| {rank} | {candidate_id} | {mean:.6f} | {std:.6f} | {params} |".format(
            rank=idx + 1,
            candidate_id=item["candidate_id"],
            mean=item["accuracy_mean"],
            std=item["accuracy_std"],
            params=json.dumps(item["params"], sort_keys=True),
        )
        for idx, item in enumerate(scores["top_candidates"])
    )
    best = scores["selected_candidate"]
    delta_cv = scores["comparison"]["delta_vs_exp_006_cv"]
    text = f"""# Results

## Summary

Status: completed.

Ran a small HistGradientBoosting hyperparameter search on official Kaggle data.

## Setup

- Experiment: `exp-008`
- Data: official Kaggle CSV files in `{data_dir}`
- Feature bundle: same as exp-006
- CV: 5-fold StratifiedKFold, random_state=42
- Candidate count: {scores["candidate_count"]}

## Metrics

exp-006 CV baseline: {scores["comparison"]["exp_006_cv_accuracy"]:.6f}

Best exp-008 CV accuracy: {scores["metrics"]["primary"]["value"]:.6f}

Delta versus exp-006 CV: {delta_cv:.6f}

| Rank | Candidate | CV Accuracy Mean | CV Accuracy Std | Params |
| ---: | --- | ---: | ---: | --- |
{top_rows}

## Main Results

Selected candidate `{best["candidate_id"]}` with CV accuracy {best["accuracy_mean"]:.6f}.
The selected model wrote `workspace/submission.csv` with {scores["submission_rows"]} rows.

## Figures

No figures were generated.

## Failures And Negative Results

- Public leaderboard score is not recorded yet.
- This search only tunes HistGradientBoosting hyperparameters.

## Reproduction

```bash
uv run python tune_hist_gradient_boosting.py --data-dir {data_dir}
```

## Notes For Reviewer

Use `results/scores.json` for exact fold scores and all candidate parameters.
"""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "results.md").write_text(text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--folds", default=5, type=int)
    parser.add_argument("--exp006-cv", default=0.8088104680348149, type=float)
    parser.add_argument("--exp006-public", default=0.80383, type=float)
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

    cv = StratifiedKFold(n_splits=args.folds, shuffle=True, random_state=42)
    candidates = []
    for index, params in enumerate(candidate_grid(), start=1):
        candidate_id = f"hgb_{index:03d}"
        pipeline = build_pipeline(train_features, params)
        fold_scores = cross_val_score(
            pipeline,
            train_features,
            target,
            cv=cv,
            scoring="accuracy",
            n_jobs=1,
        )
        item = {
            "candidate_id": candidate_id,
            "params": params,
            "accuracy_mean": float(fold_scores.mean()),
            "accuracy_std": float(fold_scores.std()),
            "fold_scores": [float(score) for score in fold_scores],
        }
        candidates.append(item)
        logging.info("%s mean=%.6f std=%.6f params=%s", candidate_id, item["accuracy_mean"], item["accuracy_std"], params)

    candidates.sort(key=lambda item: item["accuracy_mean"], reverse=True)
    best = candidates[0]
    best_pipeline = build_pipeline(train_features, best["params"])
    best_pipeline.fit(train_features, target)
    submission = sample.copy()
    submission["Transported"] = best_pipeline.predict(test_features).astype(bool)
    submission_path = ROOT / "submission.csv"
    submission.to_csv(submission_path, index=False)

    scores = {
        "experiment_id": "exp-008",
        "status": "completed",
        "benchmark": "spaceship-titanic",
        "data_kind": "official_kaggle",
        "model": "HistGradientBoostingClassifier",
        "candidate_count": len(candidates),
        "selected_candidate": best,
        "top_candidates": candidates[:10],
        "all_candidates": candidates,
        "metrics": {
            "primary": {
                "name": "cross_validated_accuracy",
                "value": best["accuracy_mean"],
                "higher_is_better": True,
            },
            "fold_count": int(args.folds),
            "public_leaderboard_score": None,
            "private_leaderboard_score": None,
        },
        "comparison": {
            "exp_006_cv_accuracy": float(args.exp006_cv),
            "exp_006_public_score": float(args.exp006_public),
            "delta_vs_exp_006_cv": float(best["accuracy_mean"] - args.exp006_cv),
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
    logging.info("Selected %s mean=%.6f", best["candidate_id"], best["accuracy_mean"])
    logging.info("Wrote %s", submission_path)


if __name__ == "__main__":
    main()
