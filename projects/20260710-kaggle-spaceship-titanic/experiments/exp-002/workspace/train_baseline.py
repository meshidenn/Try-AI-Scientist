from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


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
    if "PassengerId" in out:
        passenger_parts = out["PassengerId"].astype(str).str.split("_", expand=True)
        out["GroupId"] = passenger_parts[0]
        out["GroupPosition"] = pd.to_numeric(passenger_parts[1], errors="coerce")
        out["GroupSize"] = out.groupby("GroupId")["PassengerId"].transform("count")
    if "Cabin" in out:
        cabin_parts = out["Cabin"].astype(str).str.split("/", expand=True)
        out["CabinDeck"] = cabin_parts[0].replace("nan", float("nan"))
        out["CabinNum"] = pd.to_numeric(cabin_parts[1], errors="coerce")
        out["CabinSide"] = cabin_parts[2].replace("nan", float("nan"))
    return out


def build_pipeline(train_features: pd.DataFrame) -> Pipeline:
    numeric_features = train_features.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical_features = [
        col for col in train_features.columns if col not in numeric_features
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                Pipeline([("imputer", SimpleImputer(strategy="median"))]),
                numeric_features,
            ),
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

    model = RandomForestClassifier(
        n_estimators=300,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=1,
    )

    return Pipeline([("preprocessor", preprocessor), ("model", model)])


def write_results_md(scores: dict, data_dir: Path) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    text = f"""# Results

Status: run

## Command

```bash
python3 train_baseline.py --data-dir {data_dir}
```

## Metrics

| Metric | Value |
| --- | ---: |
| Majority baseline accuracy | {scores["metrics"]["majority_baseline_accuracy"]:.6f} |
| CV accuracy mean | {scores["metrics"]["accuracy_mean"]:.6f} |
| CV accuracy std | {scores["metrics"]["accuracy_std"]:.6f} |
| Fold count | {scores["metrics"]["fold_count"]} |

## Artifacts

- `workspace/submission.csv`
- `results/scores.json`
- `logs/run.log`

## Limitations

- This is a workflow smoke test, not a leaderboard optimization run.
- Kaggle public leaderboard score is not recorded until the submission is uploaded.
- Feature engineering is intentionally minimal.
"""
    (RESULTS_DIR / "results.md").write_text(text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default=ROOT / "data", type=Path)
    parser.add_argument("--folds", default=5, type=int)
    args = parser.parse_args()

    configure_logging()
    data_dir = args.data_dir.resolve()
    train_path = data_dir / "train.csv"
    test_path = data_dir / "test.csv"
    sample_path = data_dir / "sample_submission.csv"

    for path in [train_path, test_path, sample_path]:
        if not path.exists():
            raise FileNotFoundError(
                f"Missing {path}. Download Kaggle data into {data_dir} first."
            )

    logging.info("Loading data from %s", data_dir)
    train = add_basic_features(pd.read_csv(train_path))
    test = add_basic_features(pd.read_csv(test_path))
    sample_submission = pd.read_csv(sample_path)

    target = train["Transported"].astype(bool)
    drop_cols = ["Transported", "Name", "PassengerId", "Cabin"]
    feature_cols = [col for col in train.columns if col not in drop_cols]
    train_features = train[feature_cols]
    test_features = test[feature_cols]

    majority_baseline = max(target.mean(), 1 - target.mean())
    pipeline = build_pipeline(train_features)
    cv = StratifiedKFold(n_splits=args.folds, shuffle=True, random_state=42)
    cv_scores = cross_val_score(
        pipeline,
        train_features,
        target,
        cv=cv,
        scoring="accuracy",
        n_jobs=1,
    )

    logging.info("CV accuracy scores: %s", cv_scores.tolist())
    pipeline.fit(train_features, target)
    train_accuracy = accuracy_score(target, pipeline.predict(train_features))
    predictions = pipeline.predict(test_features).astype(bool)

    submission = sample_submission.copy()
    submission["Transported"] = predictions
    submission_path = ROOT / "submission.csv"
    submission.to_csv(submission_path, index=False)

    scores = {
        "status": "run",
        "benchmark": "spaceship-titanic",
        "metrics": {
            "majority_baseline_accuracy": float(majority_baseline),
            "accuracy_mean": float(cv_scores.mean()),
            "accuracy_std": float(cv_scores.std()),
            "fold_count": int(args.folds),
            "train_accuracy": float(train_accuracy),
            "public_leaderboard_score": None,
        },
        "artifacts": {
            "submission_csv": str(submission_path.relative_to(EXP_DIR)),
            "run_log": "logs/run.log",
        },
        "data_dir": str(data_dir),
        "model": "RandomForestClassifier",
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "scores.json").write_text(json.dumps(scores, indent=2) + "\n")
    write_results_md(scores, data_dir)
    logging.info("Wrote %s", submission_path)
    logging.info("Wrote %s", RESULTS_DIR / "scores.json")


if __name__ == "__main__":
    main()
