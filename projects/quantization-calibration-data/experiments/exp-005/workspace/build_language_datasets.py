import argparse
import json
from pathlib import Path

EXP_DIR = Path(__file__).resolve().parents[1]
CALIB_DIR = EXP_DIR / "artifacts" / "calibration"
EVAL_DIR = EXP_DIR / "artifacts" / "evaluation"
LOG_DIR = EXP_DIR / "logs"
SEED = 20260712


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")


def take_rows(dataset, n, offset=0):
    rows = []
    for i, row in enumerate(dataset):
        if i < offset:
            continue
        rows.append(dict(row))
        if len(rows) >= n:
            break
    return rows


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


def instruction_text(row):
    if "messages" in row and row["messages"]:
        return stringify_messages(row["messages"])
    if "conversations" in row and row["conversations"]:
        return stringify_messages(row["conversations"])

    instruction = row.get("instruction") or row.get("prompt") or row.get("input") or row.get("question") or row.get("text") or ""
    context = row.get("context") or row.get("input") or ""
    output = row.get("output") or row.get("response") or row.get("answer") or row.get("completion") or ""

    parts = []
    if instruction:
        parts.append(f"Instruction: {instruction}")
    if context and context != instruction:
        parts.append(f"Input: {context}")
    if output:
        parts.append(f"Response: {output}")
    if parts:
        return "\n".join(parts)
    return json.dumps(row, ensure_ascii=False)[:4000]


def load_first_available(candidates):
    from datasets import load_dataset

    errors = []
    for candidate in candidates:
        name = candidate["name"]
        parquet_url = candidate.get("parquet_url")
        configs = candidate.get("configs", [None])
        splits = candidate.get("splits", ["train"])
        data_dir = candidate.get("data_dir")
        if parquet_url:
            try:
                ds = load_dataset("parquet", data_files=parquet_url, split="train")
                return ds, {
                    "dataset": name,
                    "config": candidate.get("config"),
                    "split": candidate.get("split"),
                    "loader": "parquet_url",
                    "parquet_url": parquet_url,
                }, errors
            except Exception as exc:
                errors.append({"dataset": name, "loader": "parquet_url", "error": repr(exc)})
                continue
        for config in configs:
            for split in splits:
                try:
                    if config is None:
                        if data_dir is None:
                            ds = load_dataset(name, split=split)
                        else:
                            ds = load_dataset(name, data_dir=data_dir, split=split)
                    else:
                        ds = load_dataset(name, config, split=split)
                    return ds, {"dataset": name, "config": config, "data_dir": data_dir, "split": split}, errors
                except Exception as exc:
                    errors.append({"dataset": name, "config": config, "data_dir": data_dir, "split": split, "error": repr(exc)})
    raise RuntimeError(json.dumps(errors, indent=2, ensure_ascii=False))


ENGLISH_CANDIDATES = [
    {"name": "databricks/databricks-dolly-15k", "configs": [None], "splits": ["train"]},
    {"name": "HuggingFaceH4/ultrachat_200k", "configs": [None], "splits": ["train_sft", "train_gen", "train"]},
]

JAPANESE_CANDIDATES = [
    {
        "name": "llm-jp/llm-jp-instructions",
        "config": "v1.0",
        "split": "train",
        "parquet_url": "https://huggingface.co/datasets/llm-jp/llm-jp-instructions/resolve/refs%2Fconvert%2Fparquet/v1.0/train/0000.parquet",
    },
    {"name": "llm-jp/magpie-sft-v1.0", "configs": [None], "splits": ["train"]},
    {"name": "llm-jp/databricks-dolly-15k-ja", "configs": [None], "splits": ["train"]},
]


def build_language(language, candidates, num_calib, num_eval):
    ds, resolved, errors = load_first_available(candidates)
    source_rows = take_rows(ds, num_calib + num_eval, offset=0)
    if len(source_rows) < num_calib + num_eval:
        raise RuntimeError(f"insufficient rows for {language}: got {len(source_rows)} need {num_calib + num_eval}")
    calib_source = source_rows[:num_calib]
    eval_source = source_rows[num_calib:num_calib + num_eval]
    calib_rows = [
        {
            "sample_id": i,
            "language": language,
            "text": instruction_text(row),
            "source_row_offset": i,
            "dataset": resolved,
        }
        for i, row in enumerate(calib_source)
    ]
    eval_rows = [
        {
            "sample_id": i,
            "language": language,
            "text": instruction_text(row),
            "source_row_offset": num_calib + i,
            "dataset": resolved,
        }
        for i, row in enumerate(eval_source)
    ]
    return calib_rows, eval_rows, resolved, errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-calibration-samples", type=int, default=64)
    parser.add_argument("--num-eval-samples", type=int, default=100)
    args = parser.parse_args()

    CALIB_DIR.mkdir(parents=True, exist_ok=True)
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    manifest = {
        "status": "started",
        "generated_by": "workspace/build_language_datasets.py",
        "seed": SEED,
        "num_calibration_samples_requested": args.num_calibration_samples,
        "num_eval_samples_requested": args.num_eval_samples,
        "languages": {},
    }
    failures = {}

    try:
        en_calib, en_eval, en_resolved, en_errors = build_language(
            "english_instruction", ENGLISH_CANDIDATES, args.num_calibration_samples, args.num_eval_samples
        )
        ja_calib, ja_eval, ja_resolved, ja_errors = build_language(
            "japanese_instruction", JAPANESE_CANDIDATES, args.num_calibration_samples, args.num_eval_samples
        )

        mixed_half = args.num_calibration_samples // 2
        mixed_rows = en_calib[:mixed_half] + ja_calib[:args.num_calibration_samples - mixed_half]
        for i, row in enumerate(mixed_rows):
            row = dict(row)
            row["sample_id"] = i
            row["language"] = "bilingual_mixed"
            mixed_rows[i] = row

        outputs = {
            "english_instruction": (en_calib, en_eval, en_resolved, en_errors),
            "japanese_instruction": (ja_calib, ja_eval, ja_resolved, ja_errors),
            "bilingual_mixed": (mixed_rows, [], {"construction": "first English half plus first Japanese half"}, []),
        }
        for language, (calib_rows, eval_rows, resolved, errors) in outputs.items():
            write_jsonl(CALIB_DIR / f"{language}.jsonl", calib_rows)
            if eval_rows:
                write_jsonl(EVAL_DIR / f"{language}.jsonl", eval_rows)
            manifest["languages"][language] = {
                "status": "completed",
                "resolved_dataset": resolved,
                "calibration_file": f"artifacts/calibration/{language}.jsonl",
                "evaluation_file": f"artifacts/evaluation/{language}.jsonl" if eval_rows else None,
                "num_calibration_samples": len(calib_rows),
                "num_eval_samples": len(eval_rows),
                "nonfatal_load_errors": errors[:10],
            }
    except Exception as exc:
        failures["language_dataset_build"] = repr(exc)

    manifest["status"] = "completed" if not failures else "failed"
    manifest["failures"] = failures
    (CALIB_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (EVAL_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (LOG_DIR / "build_language_datasets.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    if failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
