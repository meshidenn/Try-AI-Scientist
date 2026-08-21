import argparse
import json
from shutil import copyfile
from pathlib import Path


def load_rows(path: Path, limit: int) -> list[dict[str, str]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rows.append({"text": row["text"]})
        if len(rows) >= limit:
            break
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--calibration",
        type=Path,
        default=Path(
            "projects/quantization-calibration-data/experiments/exp-005/"
            "artifacts/calibration/english_instruction.jsonl"
        ),
    )
    parser.add_argument("--num-calibration-samples", type=int, default=64)
    parser.add_argument("--max-seq-length", type=int, default=2048)
    args = parser.parse_args()

    from datasets import Dataset
    from llmcompressor import oneshot
    from llmcompressor.modifiers.quantization import QuantizationModifier
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if not args.model.exists():
        raise SystemExit(f"model path does not exist: {args.model}")
    rows = load_rows(args.calibration, args.num_calibration_samples)
    if not rows:
        raise SystemExit("calibration dataset is empty")

    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        device_map="auto",
        torch_dtype="auto",
        trust_remote_code=True,
    )
    recipe = QuantizationModifier(
        targets="Linear",
        scheme="NVFP4",
        ignore=["lm_head"],
    )
    oneshot(
        model=model,
        tokenizer=tokenizer,
        dataset=Dataset.from_list(rows),
        recipe=recipe,
        max_seq_length=args.max_seq_length,
        num_calibration_samples=len(rows),
    )
    args.output.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(args.output, save_compressed=True)
    tokenizer.save_pretrained(args.output)
    report = {
        "status": "completed",
        "model": str(args.model),
        "output": str(args.output),
        "scheme": "NVFP4",
        "num_calibration_samples": len(rows),
        "max_seq_length": args.max_seq_length,
    }
    source_config = json.loads((args.model / "config.json").read_text(encoding="utf-8"))
    output_config_path = args.output / "config.json"
    output_config = json.loads(output_config_path.read_text(encoding="utf-8"))
    for key in ("architectures", "model_type", "vision_config", "text_config"):
        if key in source_config:
            output_config[key] = source_config[key]
    output_config_path.write_text(
        json.dumps(output_config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    for filename in ("preprocessor_config.json", "video_preprocessor_config.json"):
        source = args.model / filename
        if source.exists():
            copyfile(source, args.output / filename)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
