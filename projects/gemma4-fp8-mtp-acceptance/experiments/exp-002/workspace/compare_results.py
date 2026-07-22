#!/usr/bin/env python3
"""exp-002 のtarget/spec比較を構造化する。"""

from __future__ import annotations

import json
import re
from pathlib import Path


EXP_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = EXP_DIR / "results"
LABEL_PATTERN = re.compile(
    r"^(?P<target>bf16|fp8)_(?P<spec>off|s1|s2|s4|s8|s16)_agent_c"
    r"(?P<concurrency>\d+)$"
)


def main() -> None:
    scores = json.loads((RESULTS_DIR / "scores.json").read_text(encoding="utf-8"))
    indexed: dict[tuple[str, str, int], dict[str, object]] = {}
    for row in scores["variants"]:
        match = LABEL_PATTERN.match(str(row["label"]))
        if not match:
            continue
        indexed[(match["target"], match["spec"], int(match["concurrency"]))] = row

    specs = ("off", "s1", "s2", "s4", "s8", "s16")
    target_comparisons = []
    best_by_target = []
    for concurrency in (1, 2, 4):
        for spec in specs:
            bf16 = indexed[("bf16", spec, concurrency)]
            fp8 = indexed[("fp8", spec, concurrency)]
            comparable_output = bf16["total_output_tokens"] == fp8["total_output_tokens"]
            target_comparisons.append(
                {
                    "spec": spec,
                    "concurrency": concurrency,
                    "bf16_output_throughput": bf16["output_throughput"],
                    "fp8_output_throughput": fp8["output_throughput"],
                    "throughput_ratio": (
                        float(fp8["output_throughput"])
                        / float(bf16["output_throughput"])
                    ),
                    "bf16_acceptance_rate": bf16["acceptance_rate"],
                    "fp8_acceptance_rate": fp8["acceptance_rate"],
                    "bf16_total_output_tokens": bf16["total_output_tokens"],
                    "fp8_total_output_tokens": fp8["total_output_tokens"],
                    "output_length_comparable": comparable_output,
                }
            )
        for target in ("bf16", "fp8"):
            candidates = [
                indexed[(target, spec, concurrency)]
                for spec in specs
                if indexed[(target, spec, concurrency)]["total_output_tokens"] == 8192
            ]
            best = max(candidates, key=lambda row: float(row["output_throughput"]))
            best_by_target.append(
                {
                    "target": target,
                    "concurrency": concurrency,
                    "label": best["label"],
                    "output_throughput": best["output_throughput"],
                    "acceptance_rate": best["acceptance_rate"],
                }
            )

    payload = {
        "experiment_id": "exp-002",
        "target_comparisons": target_comparisons,
        "best_by_target_and_concurrency": best_by_target,
        "output_length_anomalies": [
            {
                "label": row["label"],
                "total_output_tokens": row["total_output_tokens"],
            }
            for row in scores["variants"]
            if row["total_output_tokens"] != 8192
        ],
    }
    output = RESULTS_DIR / "comparisons.json"
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
