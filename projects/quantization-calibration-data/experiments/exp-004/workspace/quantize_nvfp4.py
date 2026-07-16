import argparse
import json
from pathlib import Path

EXP_DIR = Path(__file__).resolve().parents[1]
CALIB_DIR = EXP_DIR / "artifacts" / "calibration"
MODEL_DIR = EXP_DIR / "artifacts" / "models"
LOG_DIR = EXP_DIR / "logs"
LANGUAGES = ["english_instruction", "japanese_instruction", "bilingual_mixed"]


def load_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", required=True, choices=LANGUAGES)
    parser.add_argument("--model-id", default="Qwen/Qwen3-4B-Instruct-2507")
    parser.add_argument("--max-seq-length", type=int, default=2048)
    parser.add_argument("--num-calibration-samples", type=int, default=64)
    args = parser.parse_args()

    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from datasets import Dataset
        from llmcompressor import oneshot
        from llmcompressor.modifiers.quantization import QuantizationModifier
    except Exception as exc:
        raise SystemExit(f"Missing quantization dependencies: {exc}")

    calib_file = CALIB_DIR / f"{args.language}.jsonl"
    rows = load_jsonl(calib_file)
    num_samples = min(args.num_calibration_samples, len(rows))
    dataset = Dataset.from_list(rows[:num_samples])
    output_dir = MODEL_DIR / f"{args.model_id.replace('/', '--')}-NVFP4-lang-{args.language}"
    output_dir.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(args.model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id,
        device_map="auto",
        torch_dtype="auto",
        trust_remote_code=True,
    )

    recipe = QuantizationModifier(targets="Linear", scheme="NVFP4", ignore=["lm_head"])
    oneshot(
        model=model,
        tokenizer=tokenizer,
        dataset=dataset,
        recipe=recipe,
        max_seq_length=args.max_seq_length,
        num_calibration_samples=num_samples,
    )
    model.save_pretrained(output_dir, save_compressed=True)
    tokenizer.save_pretrained(output_dir)
    report = {
        "status": "completed",
        "language": args.language,
        "model_id": args.model_id,
        "scheme": "NVFP4",
        "num_calibration_samples": num_samples,
        "max_seq_length": args.max_seq_length,
        "calibration_file": str(calib_file.relative_to(EXP_DIR)),
        "output_dir": str(output_dir.relative_to(EXP_DIR)),
    }
    (LOG_DIR / f"quantize_{args.language}.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
