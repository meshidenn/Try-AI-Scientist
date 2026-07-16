import argparse
import gc
import json
import math
from pathlib import Path

import torch

EXP_DIR = Path(__file__).resolve().parents[1]
EVAL_DIR = EXP_DIR / "artifacts" / "evaluation"
MODEL_DIR = EXP_DIR / "artifacts" / "models"
LOG_DIR = EXP_DIR / "logs"
RESULTS_DIR = EXP_DIR / "results"

BASE_MODEL_ID = "Qwen/Qwen3-4B-Instruct-2507"
EVAL_LANGUAGES = ["english_instruction", "japanese_instruction"]
QUANTIZED_VARIANTS = {
    "nvfp4_lang_english_instruction": MODEL_DIR / "Qwen--Qwen3-4B-Instruct-2507-NVFP4-lang-english_instruction",
    "nvfp4_lang_japanese_instruction": MODEL_DIR / "Qwen--Qwen3-4B-Instruct-2507-NVFP4-lang-japanese_instruction",
    "nvfp4_lang_bilingual_mixed": MODEL_DIR / "Qwen--Qwen3-4B-Instruct-2507-NVFP4-lang-bilingual_mixed",
}


def load_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def evaluate_model(model_name, tokenizer, model, max_samples, max_length):
    rows = []
    model.eval()
    for language in EVAL_LANGUAGES:
        samples = load_jsonl(EVAL_DIR / f"{language}.jsonl")[:max_samples]
        total_loss = 0.0
        total_tokens = 0
        per_sample = []
        for sample in samples:
            encoded = tokenizer(sample["text"], return_tensors="pt", truncation=True, max_length=max_length)
            encoded = {key: value.to(model.device) for key, value in encoded.items()}
            labels = encoded["input_ids"].clone()
            with torch.no_grad():
                output = model(**encoded, labels=labels)
            token_count = int(encoded["attention_mask"].sum().item())
            loss = float(output.loss.item())
            total_loss += loss * token_count
            total_tokens += token_count
            per_sample.append({"sample_id": sample["sample_id"], "nll": loss, "tokens": token_count})
        mean_nll = total_loss / total_tokens if total_tokens else float("nan")
        rows.append({
            "model": model_name,
            "evaluation_language": language,
            "samples": len(samples),
            "tokens": total_tokens,
            "mean_nll": mean_nll,
            "perplexity": math.exp(mean_nll) if mean_nll < 20 else float("inf"),
            "per_sample": per_sample,
        })
    return rows


def load_model_and_tokenizer(model_ref):
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_ref, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_ref,
        device_map="auto",
        torch_dtype="auto",
        trust_remote_code=True,
    )
    return tokenizer, model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-samples", type=int, default=24)
    parser.add_argument("--max-length", type=int, default=768)
    parser.add_argument("--skip-base", action="store_true")
    parser.add_argument("--only-model", choices=["base", *QUANTIZED_VARIANTS.keys()], default=None)
    args = parser.parse_args()

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    plan = []
    if not args.skip_base:
        plan.append(("base", BASE_MODEL_ID))
    plan.extend((name, str(path)) for name, path in QUANTIZED_VARIANTS.items())
    if args.only_model:
        plan = [(name, ref) for name, ref in plan if name == args.only_model]

    all_rows = []
    for model_name, model_ref in plan:
        tokenizer, model = load_model_and_tokenizer(model_ref)
        rows = evaluate_model(model_name, tokenizer, model, args.max_samples, args.max_length)
        all_rows.extend(rows)
        (LOG_DIR / f"eval_nll_{model_name}.json").write_text(
            json.dumps({"model": model_name, "model_ref": model_ref, "rows": rows}, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        del model
        del tokenizer
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    base = {r["evaluation_language"]: r for r in all_rows if r["model"] == "base"}
    for r in all_rows:
        if r["model"] == "base" or r["evaluation_language"] not in base:
            r["delta_nll_vs_base"] = 0.0 if r["model"] == "base" else None
            r["relative_ppl_vs_base"] = 1.0 if r["model"] == "base" else None
        else:
            b = base[r["evaluation_language"]]
            r["delta_nll_vs_base"] = r["mean_nll"] - b["mean_nll"]
            r["relative_ppl_vs_base"] = r["perplexity"] / b["perplexity"]

    best_quantized = {}
    for language in EVAL_LANGUAGES:
        candidates = [r for r in all_rows if r["evaluation_language"] == language and r["model"] != "base"]
        if candidates:
            best = min(candidates, key=lambda row: row["mean_nll"])
            best_quantized[language] = {
                "model": best["model"],
                "mean_nll": best["mean_nll"],
                "delta_nll_vs_base": best["delta_nll_vs_base"],
            }

    output = {
        "status": "completed",
        "metric": "mean next-token negative log likelihood over held-out instruction texts by language",
        "higher_is_better": False,
        "max_samples_per_language": args.max_samples,
        "max_length": args.max_length,
        "evaluation_languages": EVAL_LANGUAGES,
        "rows": all_rows,
        "best_quantized_by_language": best_quantized,
    }
    (RESULTS_DIR / "eval_nll.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
