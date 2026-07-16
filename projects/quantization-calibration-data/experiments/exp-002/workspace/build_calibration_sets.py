import argparse
import json
import random
from pathlib import Path

EXP_DIR = Path(__file__).resolve().parents[1]
CALIB_DIR = EXP_DIR / "artifacts" / "calibration"
SEED = 20260704

DOMAIN_PROMPTS = {
    "general_chat": [
        "User: 週末に短時間でリフレッシュする方法を3つ教えて。\nAssistant:",
        "User: Explain why sleep matters in simple terms.\nAssistant:",
        "User: 新しいチームメンバーへの歓迎メッセージを書いて。\nAssistant:",
        "User: What are practical tips for staying focused during work?\nAssistant:",
        "User: 旅行の持ち物リストを短く作って。\nAssistant:",
    ],
    "code": [
        "Write a Python function that merges overlapping intervals.\n\n```python\n",
        "Explain the bug in this JavaScript async code and fix it:\n\nasync function main() { return await items.map(fetchItem); }\n",
        "Implement binary search in Python with type hints.\n\n```python\n",
        "Given a SQL table orders(user_id, amount), write a query for total spend per user.\n",
        "Refactor this Python loop into a list comprehension and explain tradeoffs.\n",
    ],
    "math_reasoning": [
        "A train travels 120 km in 2 hours and then 90 km in 1.5 hours. What is the average speed? Show reasoning.\n",
        "Solve step by step: if 3x + 7 = 31, what is x?\n",
        "A bag has 5 red balls and 3 blue balls. Two are drawn without replacement. What is P(two red)?\n",
        "Prove briefly why the sum of two even numbers is even.\n",
        "A store discounts an item by 20%, then adds 10% tax. If original price is 50, final price?\n",
    ],
    "long_documents": [
        "Document:\n" + "The project report describes calibration data, quantization methods, evaluation metrics, deployment risks, and future work. " * 80 + "\nQuestion: Summarize the deployment risks.\nAnswer:",
        "Context:\n" + "Section A discusses retrieval quality. Section B discusses latency. Section C discusses memory. " * 90 + "\nQuestion: Which section discusses latency?\nAnswer:",
    ],
    "multilingual": [
        "User: Translate to English: 今日は量子化の実験計画を作ります。\nAssistant:",
        "User: 次の英語を自然な日本語にしてください: Calibration data affects quantization quality.\nAssistant:",
        "User: 日本語とEnglishが混ざった文章で、GPUメモリ節約の説明を書いて。\nAssistant:",
        "User: Explain in Japanese what post-training quantization means.\nAssistant:",
    ],
}


def expand(items, n):
    rng = random.Random(SEED)
    out = []
    while len(out) < n:
        item = rng.choice(items)
        out.append({"text": item, "sample_id": len(out)})
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--samples", type=int, default=None)
    args = parser.parse_args()
    n = args.samples or (20 if args.pilot else 128)
    CALIB_DIR.mkdir(parents=True, exist_ok=True)
    domains = ["general_chat", "code", "math_reasoning"] if args.pilot else list(DOMAIN_PROMPTS)
    manifest = {"num_samples_per_domain": n, "domains": domains, "files": {}}
    for domain in domains:
        path = CALIB_DIR / f"{domain}.jsonl"
        rows = expand(DOMAIN_PROMPTS[domain], n)
        path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
        manifest["files"][domain] = str(path.relative_to(EXP_DIR))
    mixed = []
    for domain in domains:
        mixed.extend(expand(DOMAIN_PROMPTS[domain], max(1, n // len(domains))))
    mixed = mixed[:n]
    mixed_path = CALIB_DIR / "mixed_balanced.jsonl"
    mixed_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in mixed), encoding="utf-8")
    manifest["files"]["mixed_balanced"] = str(mixed_path.relative_to(EXP_DIR))
    (CALIB_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
