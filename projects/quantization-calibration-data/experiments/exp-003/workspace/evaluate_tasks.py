
import argparse
import gc
import json
import math
import multiprocessing as mp
import re
from pathlib import Path

import torch

EXP_DIR = Path(__file__).resolve().parents[1]
EVAL_DIR = EXP_DIR / "artifacts" / "evaluation"
MODEL_DIR = EXP_DIR / "artifacts" / "models"
LOG_DIR = EXP_DIR / "logs"
RESULTS_DIR = EXP_DIR / "results"

BASE_MODEL_ID = "Qwen/Qwen3-4B-Instruct-2507"
QUANTIZED_VARIANTS = {
    "nvfp4_real_general_chat": MODEL_DIR / "Qwen--Qwen3-4B-Instruct-2507-NVFP4-real-general_chat",
    "nvfp4_real_code": MODEL_DIR / "Qwen--Qwen3-4B-Instruct-2507-NVFP4-real-code",
    "nvfp4_real_math_reasoning": MODEL_DIR / "Qwen--Qwen3-4B-Instruct-2507-NVFP4-real-math_reasoning",
}


def load_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def extract_number(text):
    if not text:
        return None
    marker = re.findall(r"####\s*([-+]?\d[\d,]*(?:\.\d+)?)", text)
    if marker:
        return marker[-1].replace(",", "")
    nums = re.findall(r"[-+]?\d[\d,]*(?:\.\d+)?", text)
    return nums[-1].replace(",", "") if nums else None


def normalize_number(text):
    num = extract_number(text)
    if num is None:
        return None
    try:
        val = float(num)
    except ValueError:
        return num
    if math.isfinite(val) and abs(val - round(val)) < 1e-9:
        return str(int(round(val)))
    return ("%.10f" % val).rstrip("0").rstrip(".")


def extract_tests(prompt):
    if "Tests:" not in prompt:
        return []
    block = prompt.split("Tests:", 1)[1].split("Answer:", 1)[0]
    return [line.strip() for line in block.splitlines() if line.strip().startswith("assert ")]


def extract_python_code(generated):
    text = generated.strip()
    if "```" in text:
        text = text.split("```", 1)[0]
    # Remove common chatty prefixes while keeping code lines.
    lines = []
    started = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(("def ", "import ", "from ", "class ")):
            started = True
        if started:
            lines.append(line)
    return "\n".join(lines).strip() if lines else text


def restricted_import(name, globals=None, locals=None, fromlist=(), level=0):
    allowed = {"math", "re", "collections", "itertools", "functools", "operator", "string", "heapq", "bisect"}
    root = name.split(".", 1)[0]
    if root not in allowed:
        raise ImportError(f"import not allowed: {name}")
    return __import__(name, globals, locals, fromlist, level)


def run_code_worker(code, tests, queue):
    safe_builtins = {
        "abs": abs, "all": all, "any": any, "bool": bool, "dict": dict, "enumerate": enumerate,
        "filter": filter, "float": float, "int": int, "len": len, "list": list, "map": map,
        "max": max, "min": min, "pow": pow, "range": range, "reversed": reversed, "round": round,
        "set": set, "slice": slice, "sorted": sorted, "str": str, "sum": sum, "tuple": tuple,
        "zip": zip, "True": True, "False": False, "None": None, "__import__": restricted_import,
    }
    ns = {"__builtins__": safe_builtins}
    try:
        exec(code, ns, ns)
        for test in tests:
            exec(test, ns, ns)
        queue.put({"passed": True, "error": None})
    except Exception as exc:
        queue.put({"passed": False, "error": repr(exc)})


def run_code_tests(code, tests, timeout_s):
    queue = mp.Queue()
    proc = mp.Process(target=run_code_worker, args=(code, tests, queue))
    proc.start()
    proc.join(timeout_s)
    if proc.is_alive():
        proc.terminate()
        proc.join(1)
        return {"passed": False, "error": "timeout"}
    if not queue.empty():
        return queue.get()
    return {"passed": False, "error": f"no_result_exitcode_{proc.exitcode}"}


def generate_text(tokenizer, model, prompt, max_new_tokens):
    encoded = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024).to(model.device)
    with torch.no_grad():
        out = model.generate(
            **encoded,
            do_sample=False,
            max_new_tokens=max_new_tokens,
            pad_token_id=tokenizer.eos_token_id,
        )
    new_tokens = out[0][encoded["input_ids"].shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True)


def evaluate_gsm8k(tokenizer, model, max_samples, max_new_tokens):
    rows = []
    for sample in load_jsonl(EVAL_DIR / "math_reasoning.jsonl")[:max_samples]:
        prompt = sample.get("prompt") or sample["text"].split("Solution:", 1)[0] + "Solution:"
        prompt = prompt + "\nGive the final answer after ####.\n"
        generated = generate_text(tokenizer, model, prompt, max_new_tokens)
        pred = normalize_number(generated)
        gold = normalize_number(sample.get("answer") or sample["text"])
        rows.append({
            "sample_id": sample["sample_id"],
            "prompt": prompt,
            "generated": generated,
            "prediction": pred,
            "gold": gold,
            "correct": pred is not None and gold is not None and pred == gold,
        })
    return rows


def evaluate_mbpp(tokenizer, model, max_samples, max_new_tokens, timeout_s):
    rows = []
    for sample in load_jsonl(EVAL_DIR / "code.jsonl")[:max_samples]:
        prompt = sample["prompt"]
        generated = generate_text(tokenizer, model, prompt, max_new_tokens)
        code = extract_python_code(generated)
        tests = extract_tests(prompt)
        result = run_code_tests(code, tests, timeout_s)
        rows.append({
            "sample_id": sample["sample_id"],
            "prompt": prompt,
            "generated": generated,
            "extracted_code": code,
            "tests": tests,
            "passed": bool(result["passed"]),
            "error": result.get("error"),
        })
    return rows


def load_model_and_tokenizer(model_ref):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_ref, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(model_ref, device_map="auto", torch_dtype="auto", trust_remote_code=True)
    return tokenizer, model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-samples", type=int, default=8)
    parser.add_argument("--gsm8k-max-new-tokens", type=int, default=192)
    parser.add_argument("--mbpp-max-new-tokens", type=int, default=256)
    parser.add_argument("--code-timeout-s", type=float, default=2.0)
    parser.add_argument("--only-model", choices=["base", *QUANTIZED_VARIANTS.keys()], default=None)
    args = parser.parse_args()

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    plan = [("base", BASE_MODEL_ID)] + [(k, str(v)) for k, v in QUANTIZED_VARIANTS.items()]
    if args.only_model:
        plan = [(name, ref) for name, ref in plan if name == args.only_model]

    models = []
    for model_name, model_ref in plan:
        tokenizer, model = load_model_and_tokenizer(model_ref)
        model.eval()
        gsm_rows = evaluate_gsm8k(tokenizer, model, args.max_samples, args.gsm8k_max_new_tokens)
        mbpp_rows = evaluate_mbpp(tokenizer, model, args.max_samples, args.mbpp_max_new_tokens, args.code_timeout_s)
        summary = {
            "model": model_name,
            "model_ref": model_ref,
            "gsm8k_exact_match": sum(r["correct"] for r in gsm_rows) / len(gsm_rows) if gsm_rows else None,
            "gsm8k_correct": sum(r["correct"] for r in gsm_rows),
            "gsm8k_total": len(gsm_rows),
            "mbpp_pass_at_1": sum(r["passed"] for r in mbpp_rows) / len(mbpp_rows) if mbpp_rows else None,
            "mbpp_passed": sum(r["passed"] for r in mbpp_rows),
            "mbpp_total": len(mbpp_rows),
            "gsm8k_rows": gsm_rows,
            "mbpp_rows": mbpp_rows,
        }
        models.append(summary)
        (LOG_DIR / f"eval_tasks_{model_name}.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        del model
        del tokenizer
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    output = {
        "status": "completed",
        "max_samples_per_task": args.max_samples,
        "tasks": ["gsm8k_exact_match", "mbpp_pass_at_1_restricted"],
        "notes": "MBPP generated code is executed in a restricted subprocess with timeout; this is a small pilot metric.",
        "models": models,
    }
    (RESULTS_DIR / "eval_tasks.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
