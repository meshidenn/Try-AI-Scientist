import argparse
import json
from pathlib import Path

EXP_DIR = Path(__file__).resolve().parents[1]
EVAL_DIR = EXP_DIR / "artifacts" / "evaluation"


EVAL_SETS = {
    "general_chat": [
        "User: 明日の朝を気持ちよく始めるための小さな習慣を3つ教えて。\nAssistant: 1. 寝る前に水を用意する。2. 起きたらカーテンを開ける。3. 最初の5分だけ軽く体を動かす。",
        "User: Write a friendly thank-you note to a coworker who helped debug an issue.\nAssistant: Thanks for jumping in and helping track down the issue. Your careful debugging saved us a lot of time, and I really appreciate it.",
        "User: 夕食の献立を考えるのが面倒です。簡単な案をください。\nAssistant: ごはん、味噌汁、焼き魚か豆腐、冷凍野菜の炒め物にすると、短時間で栄養のバランスも取りやすいです。",
        "User: Explain cloud storage to a beginner in two sentences.\nAssistant: Cloud storage lets you save files on remote computers run by a provider instead of only on your own device. You can access those files from different devices when you sign in.",
        "User: 友人の誕生日に送る短いメッセージを書いて。\nAssistant: 誕生日おめでとう。いつも楽しい時間をありがとう。新しい一年が穏やかで実り多いものになりますように。",
        "User: Give three practical ways to reduce screen fatigue.\nAssistant: Take short breaks, increase text size when needed, and keep the screen brightness close to the room brightness.",
        "User: 会議の冒頭で使える一言を考えて。\nAssistant: 本日はお時間ありがとうございます。まず目的と進め方を確認してから、各論点に入っていきます。",
        "User: What is a polite way to ask for a deadline extension?\nAssistant: You can say that you want to deliver good work, explain the reason briefly, and propose a specific new deadline.",
        "User: 雨の日の通勤を少し快適にする工夫は？\nAssistant: 防水の靴を選び、替えの靴下を持ち、混雑を避けられるよう少し早めに出ると快適になります。",
        "User: Summarize why daily planning can help productivity.\nAssistant: Daily planning turns vague work into concrete next steps, which reduces decision fatigue and makes progress easier to track.",
        "User: 新しい趣味を始めたい人に短く助言して。\nAssistant: 最初から上手くやろうとせず、週に一度だけ試すくらいの小ささで始めると続けやすいです。",
        "User: How should I respond if I do not know the answer in a meeting?\nAssistant: Be honest, say you will check, and give a clear follow-up time so the group knows when to expect an answer.",
    ],
    "code": [
        "Task: Write a Python function that returns the squares of even numbers from a list.\nAnswer:\n```python\ndef even_squares(values: list[int]) -> list[int]:\n    return [x * x for x in values if x % 2 == 0]\n```",
        "Task: Explain why this code is slow: for each user it scans the whole orders list.\nAnswer: The code repeats a full scan for every user, so the runtime grows with users times orders. Building a dictionary keyed by user_id makes each lookup cheaper.",
        "Task: Write SQL to count orders per customer from orders(customer_id, id).\nAnswer:\n```sql\nSELECT customer_id, COUNT(*) AS order_count\nFROM orders\nGROUP BY customer_id;\n```",
        "Task: Fix the JavaScript promise usage: const data = urls.map(fetch);\nAnswer:\n```javascript\nconst data = await Promise.all(urls.map((url) => fetch(url)));\n```",
        "Task: Implement a guard clause for None in Python.\nAnswer:\n```python\ndef normalize(text: str | None) -> str:\n    if text is None:\n        return \"\"\n    return text.strip().lower()\n```",
        "Task: What does Big O describe?\nAnswer: Big O describes how the cost of an algorithm grows as the input size grows, usually ignoring constant factors.",
        "Task: Write a TypeScript type for a user with id and email.\nAnswer:\n```typescript\ntype User = {\n  id: string;\n  email: string;\n};\n```",
        "Task: Explain a race condition in one paragraph.\nAnswer: A race condition happens when the result depends on the timing of concurrent operations, such as two workers updating shared state without coordination.",
        "Task: Write Python code to safely open and read a UTF-8 file.\nAnswer:\n```python\nfrom pathlib import Path\ntext = Path(\"notes.txt\").read_text(encoding=\"utf-8\")\n```",
        "Task: Give a simple unit test for add(a, b).\nAnswer:\n```python\ndef test_add():\n    assert add(2, 3) == 5\n```",
        "Task: Refactor repeated condition checks into a helper function.\nAnswer: Move the shared condition into a named function, call that function from each branch, and keep the branch-specific behavior separate.",
        "Task: Write a Python function that filters empty strings.\nAnswer:\n```python\ndef non_empty(items: list[str]) -> list[str]:\n    return [item for item in items if item]\n```",
    ],
    "math_reasoning": [
        "Problem: A box has 3 red balls and 2 blue balls. What fraction are red?\nSolution: There are 5 balls total and 3 are red, so the fraction is 3/5.",
        "Problem: If 4 notebooks cost 800 yen, how much do 7 notebooks cost at the same price?\nSolution: One notebook costs 800 / 4 = 200 yen. Seven notebooks cost 7 * 200 = 1400 yen.",
        "Problem: Solve for x: 2x + 5 = 17.\nSolution: Subtract 5 from both sides to get 2x = 12, then divide by 2, so x = 6.",
        "Problem: A train travels 90 km in 1.5 hours. What is its average speed?\nSolution: Speed is distance divided by time, so 90 / 1.5 = 60 km/h.",
        "Problem: What is the next number in 2, 4, 8, 16?\nSolution: Each number is doubled, so the next number is 32.",
        "Problem: A rectangle has width 6 and height 9. What is its area?\nSolution: Area is width times height, so 6 * 9 = 54.",
        "Problem: If a price drops from 100 to 80, what is the percent decrease?\nSolution: The decrease is 20 out of 100, so the percent decrease is 20%.",
        "Problem: There are 12 apples split equally among 4 people. How many apples per person?\nSolution: 12 divided by 4 is 3, so each person gets 3 apples.",
        "Problem: Which is larger, 3/4 or 2/3?\nSolution: Compare cross products: 3 * 3 = 9 and 2 * 4 = 8, so 3/4 is larger.",
        "Problem: If x is even, is x + 3 even or odd?\nSolution: Adding an odd number to an even number gives an odd number, so x + 3 is odd.",
        "Problem: A bag has 5 coins. You add 7 and remove 3. How many coins remain?\nSolution: Start with 5, add 7 to get 12, then remove 3 to get 9.",
        "Problem: What is 15% of 200?\nSolution: 10% of 200 is 20 and 5% is 10, so 15% is 30.",
    ],
}


def write_jsonl(path, rows):
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()

    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "status": "generated",
        "generated_by": "workspace/build_evaluation_sets.py",
        "split": "synthetic_pilot_heldout",
        "note": "Small held-out synthetic evaluation texts. These are separate from calibration JSONL files and intended only for the exp-002 pilot.",
        "domains": {},
    }
    for domain, texts in EVAL_SETS.items():
        rows = [{"sample_id": i, "text": text} for i, text in enumerate(texts)]
        write_jsonl(EVAL_DIR / f"{domain}.jsonl", rows)
        manifest["domains"][domain] = {
            "file": f"artifacts/evaluation/{domain}.jsonl",
            "num_samples": len(rows),
        }
    write_jsonl(EVAL_DIR / "mixed_balanced.jsonl", [
        {"sample_id": i, "text": text}
        for i, text in enumerate(
            text
            for row in zip(*(EVAL_SETS[domain][:6] for domain in EVAL_SETS))
            for text in row
        )
    ])
    manifest["domains"]["mixed_balanced"] = {
        "file": "artifacts/evaluation/mixed_balanced.jsonl",
        "num_samples": 18,
    }
    (EVAL_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
