
import argparse
import json
import random
from pathlib import Path

EXP_DIR = Path(__file__).resolve().parents[1]
CALIB_DIR = EXP_DIR / "artifacts" / "calibration"
EVAL_DIR = EXP_DIR / "artifacts" / "evaluation"
LOG_DIR = EXP_DIR / "logs"

SEED = 20260707


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")


def stringify_messages(messages, max_turns=6):
    parts = []
    for msg in messages[:max_turns]:
        if isinstance(msg, dict):
            role = msg.get("role") or msg.get("from") or "message"
            content = msg.get("content") or msg.get("value") or ""
        else:
            role = "message"
            content = str(msg)
        if content:
            parts.append(f"{role}: {content}")
    return "\n".join(parts)


def row_to_chat_text(row):
    for key in ["messages", "conversations"]:
        if key in row and row[key]:
            text = stringify_messages(row[key])
            if text:
                return text
    for key in ["prompt", "instruction", "text"]:
        if key in row and row[key]:
            return str(row[key])
    return json.dumps(row, ensure_ascii=False)[:4000]


def row_to_mbpp_text(row, include_answer=True):
    prompt = row.get("text") or row.get("prompt") or row.get("task") or ""
    code = row.get("code") or row.get("canonical_solution") or ""
    tests = row.get("test_list") or row.get("test") or []
    if isinstance(tests, list):
        tests_text = "\n".join(str(t) for t in tests[:3])
    else:
        tests_text = str(tests)
    if include_answer and code:
        return f"Task: {prompt}\nTests:\n{tests_text}\nAnswer:\n```python\n{code}\n```"
    return f"Task: {prompt}\nTests:\n{tests_text}\nAnswer:\n```python\n"


def row_to_gsm8k_text(row, include_answer=True):
    q = row.get("question") or row.get("prompt") or ""
    a = row.get("answer") or ""
    if include_answer:
        return f"Problem: {q}\nSolution: {a}"
    return f"Problem: {q}\nSolution:"


def take_rows(dataset, n, offset=0):
    rows = []
    for i, row in enumerate(dataset):
        if i < offset:
            continue
        rows.append(dict(row))
        if len(rows) >= n:
            break
    return rows


def try_load_dataset(specs, split_preference):
    from datasets import load_dataset

    errors = []
    for spec in specs:
        name = spec["name"]
        config = spec.get("config")
        split_candidates = spec.get("splits") or split_preference
        for split in split_candidates:
            try:
                if config is None:
                    ds = load_dataset(name, split=split)
                else:
                    ds = load_dataset(name, config, split=split)
                return ds, {"dataset": name, "config": config, "split": split}, errors
            except Exception as exc:
                errors.append({"dataset": name, "config": config, "split": split, "error": repr(exc)})
    raise RuntimeError(json.dumps(errors, ensure_ascii=False, indent=2))


def build_general_chat(num_calib, num_eval):
    ds, resolved, errors = try_load_dataset(
        [{"name": "HuggingFaceH4/ultrachat_200k", "config": None, "splits": ["train_sft", "train_gen", "train"]}],
        ["train"],
    )
    calib_rows = [
        {"sample_id": i, "text": row_to_chat_text(row), "source_row_offset": i, "dataset": resolved}
        for i, row in enumerate(take_rows(ds, num_calib, offset=0))
    ]
    eval_rows = [
        {"sample_id": i, "text": row_to_chat_text(row), "source_row_offset": num_calib + i, "dataset": resolved}
        for i, row in enumerate(take_rows(ds, num_eval, offset=num_calib))
    ]
    return calib_rows, eval_rows, resolved, errors


def build_code(num_calib, num_eval):
    specs = []
    for name in ["google-research-datasets/mbpp", "mbpp"]:
        for config in ["full", "sanitized", None]:
            specs.append({"name": name, "config": config, "splits": ["train", "validation", "test"]})
    ds, resolved, errors = try_load_dataset(specs, ["train"])
    calib_source = take_rows(ds, num_calib, offset=0)
    eval_source = take_rows(ds, num_eval, offset=num_calib)
    if len(eval_source) < num_eval:
        eval_ds, eval_resolved, eval_errors = try_load_dataset(
            [{"name": resolved["dataset"], "config": resolved["config"], "splits": ["test", "validation", resolved["split"]]}],
            [resolved["split"]],
        )
        errors.extend(eval_errors)
        eval_source = take_rows(eval_ds, num_eval, offset=0)
        eval_resolved_for_rows = eval_resolved
    else:
        eval_resolved_for_rows = resolved
    calib_rows = [
        {"sample_id": i, "text": row_to_mbpp_text(row, include_answer=True), "source_row_offset": i, "dataset": resolved}
        for i, row in enumerate(calib_source)
    ]
    eval_rows = [
        {"sample_id": i, "text": row_to_mbpp_text(row, include_answer=True), "prompt": row_to_mbpp_text(row, include_answer=False), "source_row_offset": i, "dataset": eval_resolved_for_rows}
        for i, row in enumerate(eval_source)
    ]
    return calib_rows, eval_rows, resolved, errors


def build_math(num_calib, num_eval):
    train_ds, train_resolved, train_errors = try_load_dataset(
        [{"name": "openai/gsm8k", "config": "main", "splits": ["train"]}],
        ["train"],
    )
    test_ds, test_resolved, test_errors = try_load_dataset(
        [{"name": "openai/gsm8k", "config": "main", "splits": ["test"]}],
        ["test"],
    )
    calib_rows = [
        {"sample_id": i, "text": row_to_gsm8k_text(row, include_answer=True), "source_row_offset": i, "dataset": train_resolved}
        for i, row in enumerate(take_rows(train_ds, num_calib, offset=0))
    ]
    eval_rows = []
    for i, row in enumerate(take_rows(test_ds, num_eval, offset=0)):
        eval_rows.append({
            "sample_id": i,
            "text": row_to_gsm8k_text(row, include_answer=True),
            "prompt": row_to_gsm8k_text(row, include_answer=False),
            "answer": row.get("answer", ""),
            "source_row_offset": i,
            "dataset": test_resolved,
        })
    return calib_rows, eval_rows, train_resolved, train_errors + test_errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-calibration-samples", type=int, default=64)
    parser.add_argument("--num-eval-samples", type=int, default=12)
    args = parser.parse_args()

    random.seed(SEED)
    CALIB_DIR.mkdir(parents=True, exist_ok=True)
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    builders = {
        "general_chat": build_general_chat,
        "code": build_code,
        "math_reasoning": build_math,
    }
    manifest = {
        "status": "started",
        "generated_by": "workspace/build_real_datasets.py",
        "seed": SEED,
        "num_calibration_samples_requested": args.num_calibration_samples,
        "num_eval_samples_requested": args.num_eval_samples,
        "domains": {},
    }
    failures = {}
    for domain, builder in builders.items():
        try:
            calib_rows, eval_rows, resolved, errors = builder(args.num_calibration_samples, args.num_eval_samples)
            if len(calib_rows) < args.num_calibration_samples or len(eval_rows) < args.num_eval_samples:
                raise RuntimeError(f"insufficient rows: calibration={len(calib_rows)}, eval={len(eval_rows)}")
            write_jsonl(CALIB_DIR / f"{domain}.jsonl", calib_rows)
            write_jsonl(EVAL_DIR / f"{domain}.jsonl", eval_rows)
            manifest["domains"][domain] = {
                "status": "completed",
                "resolved_dataset": resolved,
                "calibration_file": f"artifacts/calibration/{domain}.jsonl",
                "evaluation_file": f"artifacts/evaluation/{domain}.jsonl",
                "num_calibration_samples": len(calib_rows),
                "num_eval_samples": len(eval_rows),
                "nonfatal_load_errors": errors[:10],
            }
        except Exception as exc:
            failures[domain] = repr(exc)
            manifest["domains"][domain] = {"status": "failed", "error": repr(exc)}

    manifest["status"] = "completed" if not failures else "partial_failed"
    manifest["failures"] = failures
    (CALIB_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (EVAL_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (LOG_DIR / "build_real_datasets.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    if failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
