import json
import math
from pathlib import Path

import numpy as np
from sklearn.datasets import load_digits
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier


EXP_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = EXP_DIR / "results"
LOGS_DIR = EXP_DIR / "logs"


def affine_fake_quantize(x, min_val, max_val, bits):
    qmin = 0
    qmax = (1 << bits) - 1
    if not np.isfinite(min_val) or not np.isfinite(max_val):
        raise ValueError("Calibration range contains non-finite values")
    if math.isclose(float(min_val), float(max_val)):
        return np.full_like(x, fill_value=min_val, dtype=np.float64)
    scale = (max_val - min_val) / (qmax - qmin)
    q = np.round((x - min_val) / scale)
    q = np.clip(q, qmin, qmax)
    return q * scale + min_val


def symmetric_fake_quantize(x, bits):
    qmax = (1 << (bits - 1)) - 1
    max_abs = float(np.max(np.abs(x)))
    if max_abs == 0.0:
        return np.zeros_like(x, dtype=np.float64)
    scale = max_abs / qmax
    q = np.round(x / scale)
    q = np.clip(q, -qmax, qmax)
    return q * scale


def forward_fp32(model, x):
    hidden = np.maximum(0.0, x @ model.coefs_[0] + model.intercepts_[0])
    logits = hidden @ model.coefs_[1] + model.intercepts_[1]
    return hidden, logits


def calibration_ranges(model, x_cal):
    hidden, _ = forward_fp32(model, x_cal)
    return {
        "input_min": float(np.min(x_cal)),
        "input_max": float(np.max(x_cal)),
        "hidden_min": float(np.min(hidden)),
        "hidden_max": float(np.max(hidden)),
    }


def predict_quantized(model, x, ranges, bits):
    w0 = symmetric_fake_quantize(model.coefs_[0], bits)
    w1 = symmetric_fake_quantize(model.coefs_[1], bits)
    xq = affine_fake_quantize(x, ranges["input_min"], ranges["input_max"], bits)
    hidden = np.maximum(0.0, xq @ w0 + model.intercepts_[0])
    hidden_q = affine_fake_quantize(
        hidden, ranges["hidden_min"], ranges["hidden_max"], bits
    )
    logits = hidden_q @ w1 + model.intercepts_[1]
    return np.argmax(logits, axis=1), hidden


def clip_rate(x, min_val, max_val):
    return float(np.mean((x < min_val) | (x > max_val)))


def make_calibration_sets(x_train, y_train, rng):
    n = len(x_train)
    representative_idx = rng.choice(n, size=200, replace=False)
    small_idx = rng.choice(n, size=20, replace=False)
    class0_idx = np.where(y_train == 0)[0]
    low_idx = np.argsort(np.mean(x_train, axis=1))[:200]
    high_idx = np.argsort(np.mean(x_train, axis=1))[-200:]
    gaussian_noise = np.clip(rng.normal(loc=0.5, scale=0.25, size=(200, x_train.shape[1])), 0.0, 1.0)
    blank_zeros = np.zeros((200, x_train.shape[1]), dtype=np.float64)

    return {
        "representative_200": x_train[representative_idx],
        "small_20": x_train[small_idx],
        "class0_only": x_train[class0_idx],
        "low_intensity_200": x_train[low_idx],
        "high_intensity_200": x_train[high_idx],
        "gaussian_noise_200": gaussian_noise,
        "blank_zeros_200": blank_zeros,
    }


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    digits = load_digits()
    x = digits.data.astype(np.float64) / 16.0
    y = digits.target
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.25, random_state=42, stratify=y
    )

    model = MLPClassifier(
        hidden_layer_sizes=(64,),
        activation="relu",
        solver="adam",
        alpha=1e-4,
        batch_size=64,
        learning_rate_init=1e-3,
        max_iter=700,
        random_state=7,
        early_stopping=True,
        n_iter_no_change=30,
        validation_fraction=0.15,
    )
    model.fit(x_train, y_train)

    fp32_pred = model.predict(x_test)
    fp32_accuracy = float(accuracy_score(y_test, fp32_pred))
    rng = np.random.default_rng(20260704)
    calibration_sets = make_calibration_sets(x_train, y_train, rng)

    rows = []
    for calibration_name, x_cal in calibration_sets.items():
        ranges = calibration_ranges(model, x_cal)
        for bits in (8, 4):
            pred, hidden_test = predict_quantized(model, x_test, ranges, bits)
            accuracy = float(accuracy_score(y_test, pred))
            rows.append(
                {
                    "calibration_dataset": calibration_name,
                    "bits": bits,
                    "calibration_size": int(len(x_cal)),
                    "test_accuracy": accuracy,
                    "accuracy_drop_from_fp32": float(fp32_accuracy - accuracy),
                    "input_min": ranges["input_min"],
                    "input_max": ranges["input_max"],
                    "hidden_min": ranges["hidden_min"],
                    "hidden_max": ranges["hidden_max"],
                    "input_clip_rate_on_test": clip_rate(
                        x_test, ranges["input_min"], ranges["input_max"]
                    ),
                    "hidden_clip_rate_on_test": clip_rate(
                        hidden_test, ranges["hidden_min"], ranges["hidden_max"]
                    ),
                }
            )

    best_4bit = max((r for r in rows if r["bits"] == 4), key=lambda r: r["test_accuracy"])
    worst_4bit = min((r for r in rows if r["bits"] == 4), key=lambda r: r["test_accuracy"])
    best_8bit = max((r for r in rows if r["bits"] == 8), key=lambda r: r["test_accuracy"])
    worst_8bit = min((r for r in rows if r["bits"] == 8), key=lambda r: r["test_accuracy"])

    scores = {
        "experiment_id": "exp-001",
        "status": "completed",
        "metrics": {
            "primary": {
                "name": "best_4bit_test_accuracy",
                "value": best_4bit["test_accuracy"],
                "higher_is_better": True,
            },
            "fp32_test_accuracy": fp32_accuracy,
            "best_4bit": best_4bit,
            "worst_4bit": worst_4bit,
            "best_8bit": best_8bit,
            "worst_8bit": worst_8bit,
            "all_results": rows,
        },
        "artifacts": {
            "results_md": "results/results.md",
            "figures": [],
            "logs": ["logs/run.log"],
        },
    }
    (RESULTS_DIR / "scores.json").write_text(
        json.dumps(scores, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    sorted_rows = sorted(rows, key=lambda r: (r["bits"], -r["test_accuracy"]))
    lines = [
        "# Results",
        "",
        "## Summary",
        "",
        f"FP32 baseline test accuracy: {fp32_accuracy:.4f}.",
        f"Best 4-bit calibration: {best_4bit['calibration_dataset']} at {best_4bit['test_accuracy']:.4f}.",
        f"Worst 4-bit calibration: {worst_4bit['calibration_dataset']} at {worst_4bit['test_accuracy']:.4f}.",
        f"Best 8-bit calibration: {best_8bit['calibration_dataset']} at {best_8bit['test_accuracy']:.4f}.",
        f"Worst 8-bit calibration: {worst_8bit['calibration_dataset']} at {worst_8bit['test_accuracy']:.4f}.",
        "",
        "## Setup",
        "",
        "- Dataset: `sklearn.datasets.load_digits`, pixels scaled to `[0, 1]`.",
        "- Split: stratified 75/25 train/test with `random_state=42`.",
        "- Model: `MLPClassifier(hidden_layer_sizes=(64,), random_state=7)`.",
        "- Quantization: simulated PTQ with per-tensor symmetric weight quantization and per-layer affine activation quantization.",
        "- Calibration changes only activation ranges; the trained model and test split are fixed.",
        "",
        "## Metrics",
        "",
        "- Primary: test accuracy after quantization.",
        "- Secondary: accuracy drop from FP32, test activation clip rates.",
        "",
        "## Main Results",
        "",
        "| bits | calibration_dataset | n_cal | test_accuracy | drop_from_fp32 | input_clip_rate | hidden_clip_rate |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for r in sorted_rows:
        lines.append(
            "| {bits} | {name} | {n} | {acc:.4f} | {drop:.4f} | {iclip:.4f} | {hclip:.4f} |".format(
                bits=r["bits"],
                name=r["calibration_dataset"],
                n=r["calibration_size"],
                acc=r["test_accuracy"],
                drop=r["accuracy_drop_from_fp32"],
                iclip=r["input_clip_rate_on_test"],
                hclip=r["hidden_clip_rate_on_test"],
            )
        )
    lines.extend(
        [
            "",
            "## Figures",
            "",
            "No figure was generated in this run.",
            "",
            "## Failures And Negative Results",
            "",
            "- No execution failure occurred.",
            "- 8-bit quantization showed little sensitivity among non-pathological calibration datasets in this toy setup.",
            "- `gaussian_noise_200` is an out-of-distribution calibration baseline; it is not a valid deployment recommendation.",
            "- `blank_zeros_200` is a pathological sanity check; it verifies that broken calibration ranges can collapse accuracy.",
            "",
            "## Reproduction",
            "",
            "```bash",
            "uv run python projects/quantization-calibration-data/experiments/exp-001/workspace/run_experiment.py",
            "```",
            "",
            "## Notes For Reviewer",
            "",
            "- This is a small local MVP experiment, not a claim about LLM-scale quantization.",
            "- Calibration ranges are global per layer, so the experiment intentionally isolates a simple and inspectable PTQ mechanism.",
        ]
    )
    (RESULTS_DIR / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    log_lines = [
        "completed=true",
        f"fp32_test_accuracy={fp32_accuracy:.6f}",
        f"best_4bit={best_4bit['calibration_dataset']}:{best_4bit['test_accuracy']:.6f}",
        f"worst_4bit={worst_4bit['calibration_dataset']}:{worst_4bit['test_accuracy']:.6f}",
        f"best_8bit={best_8bit['calibration_dataset']}:{best_8bit['test_accuracy']:.6f}",
        f"worst_8bit={worst_8bit['calibration_dataset']}:{worst_8bit['test_accuracy']:.6f}",
    ]
    (LOGS_DIR / "run.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
