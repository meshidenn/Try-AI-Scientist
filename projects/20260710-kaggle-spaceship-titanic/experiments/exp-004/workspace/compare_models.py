from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parent
EXP_DIR = ROOT.parent
RESULTS_DIR = EXP_DIR / "results"
LOGS_DIR = EXP_DIR / "logs"


def configure_logging() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(LOGS_DIR / "run.log", mode="w"),
            logging.StreamHandler(),
        ],
    )


def add_basic_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    passenger_parts = out["PassengerId"].astype(str).str.split("_", expand=True)
    out["GroupId"] = passenger_parts[0]
    out["GroupPosition"] = pd.to_numeric(passenger_parts[1], errors="coerce")
    out["GroupSize"] = out.groupby("GroupId")["PassengerId"].transform("count")

    cabin_parts = out["Cabin"].astype(str).str.split("/", expand=True)
    out["CabinDeck"] = cabin_parts[0].replace("nan", float("nan"))
    out["CabinNum"] = pd.to_numeric(cabin_parts[1], errors="coerce")
    out["CabinSide"] = cabin_parts[2].replace("nan", float("nan"))
    return out


def build_preprocessor(features: pd.DataFrame, scale_numeric: bool) -> ColumnTransformer:
    numeric_features = features.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical_features = [col for col in features.columns if col not in numeric_features]
    numeric_steps = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        numeric_steps.append(("scaler", StandardScaler()))
    return ColumnTransformer(
        transformers=[
            ("numeric", Pipeline(numeric_steps), numeric_features),
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


def build_candidates(features: pd.DataFrame) -> dict[str, Pipeline]:
    return {
        "logistic_regression": Pipeline(
            [
                ("preprocessor", build_preprocessor(features, scale_numeric=True)),
                ("model", LogisticRegression(max_iter=1000, random_state=42)),
            ]
        ),
        "random_forest": Pipeline(
            [
                ("preprocessor", build_preprocessor(features, scale_numeric=False)),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=300,
                        min_samples_leaf=2,
                        random_state=42,
                        n_jobs=1,
                    ),
                ),
            ]
        ),
    }


def write_results_md(scores: dict) -> None:
    rows = "\n".join(
        f"| {name} | {item['accuracy_mean']:.6f} | {item['accuracy_std']:.6f} |"
        for name, item in scores["metrics"]["candidates"].items()
    )
    text = f"""# Results

## Summary

Status: completed.

Compared two sklearn model candidates on the same local fixture configuration as
exp-002.

## Setup

- Experiment: `exp-004`
- Data: synthetic fixture, 1200 train rows, 400 test rows, seed 42
- Evaluation: 5-fold stratified cross-validation

## Metrics

| Candidate | CV Accuracy Mean | CV Accuracy Std |
| --- | ---: | ---: |
{rows}

Majority baseline accuracy: {scores["metrics"]["majority_baseline_accuracy"]:.6f}

## Main Results

Selected candidate: `{scores["selected_model"]}`.

Best CV accuracy: {scores["metrics"]["primary"]["value"]:.6f}.

## Figures

No figures were generated.

## Failures And Negative Results

- Official Kaggle leaderboard score is unavailable.
- Candidate comparison is local to a synthetic fixture.

## Reproduction

```bash
uv run python make_fixture_data.py --out-dir data --train-rows 1200 --test-rows 400 --seed 42
uv run python compare_models.py --data-dir data --folds 5
```

## Notes For Reviewer

This experiment validates candidate comparison artifacts, not real Kaggle
generalization.
"""
    (RESULTS_DIR / "results.md").write_text(text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default=ROOT / "data", type=Path)
    parser.add_argument("--folds", default=5, type=int)
    args = parser.parse_args()

    configure_logging()
    data_dir = args.data_dir.resolve()
    train = add_basic_features(pd.read_csv(data_dir / "train.csv"))
    target = train["Transported"].astype(bool)
    drop_cols = ["Transported", "Name", "PassengerId", "Cabin"]
    feature_cols = [col for col in train.columns if col not in drop_cols]
    features = train[feature_cols]

    majority_baseline = max(target.mean(), 1 - target.mean())
    cv = StratifiedKFold(n_splits=args.folds, shuffle=True, random_state=42)
    candidates = build_candidates(features)
    candidate_scores = {}
    for name, pipeline in candidates.items():
        scores = cross_val_score(
            pipeline,
            features,
            target,
            cv=cv,
            scoring="accuracy",
            n_jobs=1,
        )
        candidate_scores[name] = {
            "accuracy_mean": float(scores.mean()),
            "accuracy_std": float(scores.std()),
            "fold_scores": [float(score) for score in scores],
        }
        logging.info("%s CV accuracy scores: %s", name, scores.tolist())

    selected_model = max(candidate_scores, key=lambda name: candidate_scores[name]["accuracy_mean"])
    scores = {
        "experiment_id": "exp-004",
        "status": "completed",
        "benchmark": "spaceship-titanic",
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
        },
        "artifacts": {
            "results_md": "results/results.md",
            "run_log": "logs/run.log",
        },
        "data_dir": str(data_dir),
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "scores.json").write_text(json.dumps(scores, indent=2) + "\n")
    write_results_md(scores)
    logging.info("Selected model: %s", selected_model)
    logging.info("Wrote %s", RESULTS_DIR / "scores.json")


if __name__ == "__main__":
    main()
