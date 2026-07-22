#!/usr/bin/env python3
"""random と agentic workload の BF16/FP8 比較を統合する。"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from render_workload_comparison import write_markdown


PROJECT_DIR = Path(__file__).resolve().parent.parent
EXP1_RESULTS = PROJECT_DIR / "experiments" / "exp-001" / "results"
EXP2_RESULTS = PROJECT_DIR / "experiments" / "exp-002" / "results"
OUTPUT = PROJECT_DIR / "review" / "integrated-comparison.json"
MARKDOWN_OUTPUT = PROJECT_DIR / "review" / "workload-comparison.md"
PARITY_THRESHOLD = 0.05


# exp-001 は実施時期ごとにlabel形式が異なるため、比較可能なpairを明示する。
RANDOM_PAIRS = (
    (1, 128, 512, 1, "bf16_s1_in128_out512.benchmark.json", "fp8_s1_in128_out512.benchmark.json"),
    (1, 1024, 1024, 1, "bf16_s1_in1024_out1024.benchmark.json", "fp8_s1_in1024_out1024.benchmark.json"),
    (2, 128, 512, 1, "bf16_s2_in128_out512.benchmark.json", "fp8_s2_in128_out512.benchmark.json"),
    (4, 128, 128, 1, "bf16_target_mtp.benchmark.json", "fp8_dynamic_target_mtp.benchmark.json"),
    (4, 128, 512, 1, "bf16_out512_s4.benchmark.json", "fp8_out512_s4.benchmark.json"),
    (4, 128, 512, 4, "bf16_out512_s4_c4.benchmark.json", "fp8_out512_s4_c4.benchmark.json"),
    (4, 1024, 1024, 2, "bf16_s4_in1024_out1024_c2.benchmark.json", "fp8_s4_in1024_out1024_c2.benchmark.json"),
    (4, 1024, 1024, 4, "bf16_s4_in1024_out1024_c4.benchmark.json", "fp8_s4_in1024_out1024_c4.benchmark.json"),
    (4, 1024, 1024, 8, "bf16_s4_in1024_out1024_c8.benchmark.json", "fp8_s4_in1024_out1024_c8.benchmark.json"),
    (4, 1024, 2048, 1, "bf16_s4_in1024_out2048.benchmark.json", "fp8_s4_in1024_out2048.benchmark.json"),
    (4, 2048, 1024, 1, "bf16_s4_in2048_out1024.benchmark.json", "fp8_s4_in2048_out1024.benchmark.json"),
    (4, 2048, 1536, 1, "bf16_s4_in2048_out1536.benchmark.json", "fp8_s4_in2048_out1536.benchmark.json"),
)


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def verdict(ratio: float) -> str:
    if ratio > 1 + PARITY_THRESHOLD:
        return "fp8_faster"
    if ratio < 1 - PARITY_THRESHOLD:
        return "bf16_faster"
    return "parity"


def comparison(
    workload: str,
    spec_tokens: int | str,
    concurrency: int,
    bf16: dict[str, object],
    fp8: dict[str, object],
    *,
    input_len: int | None = None,
    output_len: int | None = None,
) -> dict[str, object]:
    bf16_throughput = float(bf16["output_throughput"])
    fp8_throughput = float(fp8["output_throughput"])
    ratio = fp8_throughput / bf16_throughput
    comparable = bf16["total_output_tokens"] == fp8["total_output_tokens"]
    return {
        "workload": workload,
        "spec_tokens": spec_tokens,
        "input_len": input_len,
        "output_len": output_len,
        "concurrency": concurrency,
        "bf16_output_throughput": bf16_throughput,
        "fp8_output_throughput": fp8_throughput,
        "fp8_over_bf16": ratio,
        "throughput_delta_percent": (ratio - 1) * 100,
        "bf16_acceptance_rate": bf16.get("spec_decode_acceptance_rate"),
        "fp8_acceptance_rate": fp8.get("spec_decode_acceptance_rate"),
        "bf16_total_output_tokens": bf16["total_output_tokens"],
        "fp8_total_output_tokens": fp8["total_output_tokens"],
        "output_length_comparable": comparable,
        "verdict": verdict(ratio) if comparable else "not_comparable",
    }


def random_comparisons() -> list[dict[str, object]]:
    rows = []
    for spec, input_len, output_len, concurrency, bf16_name, fp8_name in RANDOM_PAIRS:
        rows.append(
            comparison(
                "random",
                spec,
                concurrency,
                load(EXP1_RESULTS / bf16_name),
                load(EXP1_RESULTS / fp8_name),
                input_len=input_len,
                output_len=output_len,
            )
        )

    high_spec = load(EXP1_RESULTS / "high_spec_comparison.json")
    for item in high_spec["fp8_vs_bf16"]:
        ratio = float(item["throughput_ratio"])
        rows.append(
            {
                "workload": "random",
                "spec_tokens": item["spec_tokens"],
                "input_len": item["input_len"],
                "output_len": item["output_len"],
                "concurrency": item["concurrency"],
                "bf16_output_throughput": item["bf16_output_throughput"],
                "fp8_output_throughput": item["fp8_output_throughput"],
                "fp8_over_bf16": ratio,
                "throughput_delta_percent": (ratio - 1) * 100,
                "bf16_acceptance_rate": item["bf16_acceptance_rate"],
                "fp8_acceptance_rate": item["fp8_acceptance_rate"],
                "bf16_total_output_tokens": None,
                "fp8_total_output_tokens": None,
                "output_length_comparable": True,
                "verdict": verdict(ratio),
            }
        )
    return rows


def agentic_comparisons() -> list[dict[str, object]]:
    source = load(EXP2_RESULTS / "comparisons.json")
    rows = []
    for item in source["target_comparisons"]:
        spec = item["spec"]
        spec_tokens: int | str = "off" if spec == "off" else int(spec[1:])
        ratio = float(item["throughput_ratio"])
        comparable = bool(item["output_length_comparable"])
        rows.append(
            {
                "workload": "agentic_synthetic",
                "spec_tokens": spec_tokens,
                "input_len": "1006-4993",
                "output_len": 512,
                "concurrency": item["concurrency"],
                "bf16_output_throughput": item["bf16_output_throughput"],
                "fp8_output_throughput": item["fp8_output_throughput"],
                "fp8_over_bf16": ratio,
                "throughput_delta_percent": (ratio - 1) * 100,
                "bf16_acceptance_rate": item["bf16_acceptance_rate"],
                "fp8_acceptance_rate": item["fp8_acceptance_rate"],
                "bf16_total_output_tokens": item["bf16_total_output_tokens"],
                "fp8_total_output_tokens": item["fp8_total_output_tokens"],
                "output_length_comparable": comparable,
                "verdict": verdict(ratio) if comparable else "not_comparable",
            }
        )
    return rows


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    counts = Counter(str(row["verdict"]) for row in rows)
    return {
        "comparison_count": len(rows),
        "verdict_counts": dict(sorted(counts.items())),
    }


def main() -> None:
    random_rows = random_comparisons()
    agentic_rows = agentic_comparisons()
    payload = {
        "project": "gemma4-fp8-mtp-acceptance",
        "metric": "output_throughput_tokens_per_second",
        "parity_threshold_percent": PARITY_THRESHOLD * 100,
        "classification_note": "±5%以内は単発測定の小差としてparity扱い",
        "random": {
            "summary": summarize(random_rows),
            "comparisons": random_rows,
        },
        "agentic_synthetic": {
            "summary": summarize(agentic_rows),
            "comparisons": agentic_rows,
        },
        "limitations": [
            "各条件は原則1 runで、分散は未推定",
            "randomのspec 1/2/4と8/16はprompt数と実施時期が異なる",
            "agentic workloadはsynthetic raw completionで実tool API replayではない",
            "agenticの2条件はtotal output token不一致のためcross-target比較対象外",
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload, MARKDOWN_OUTPUT)
    print(
        f"wrote {OUTPUT} and {MARKDOWN_OUTPUT}: "
        f"random={len(random_rows)}, agentic={len(agentic_rows)}"
    )


if __name__ == "__main__":
    main()
