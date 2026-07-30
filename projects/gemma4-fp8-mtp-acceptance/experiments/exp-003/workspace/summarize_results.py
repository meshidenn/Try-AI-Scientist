#!/usr/bin/env python3
"""exp-003の72-cell factorial matrixを構造化する。"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


EXP_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = EXP_DIR / "results"
PATTERN = re.compile(
    r"^(?P<target>bf16|fp8)_s(?P<spec>4|8|16)_"
    r"in(?P<input>\d+)_out(?P<output>\d+)_c(?P<concurrency>\d+)$"
)
EXPECTED_RUNS = 72


def load_rows() -> list[dict[str, object]]:
    rows = []
    for path in sorted(RESULTS_DIR.glob("*.benchmark.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        match = PATTERN.match(str(data.get("label", "")))
        if not match:
            continue
        rows.append(
            {
                "target": match["target"],
                "spec_tokens": int(match["spec"]),
                "input_len": int(match["input"]),
                "output_len": int(match["output"]),
                "concurrency": int(match["concurrency"]),
                "completed": data["completed"],
                "failed": data["failed"],
                "output_throughput": data["output_throughput"],
                "total_token_throughput": data["total_token_throughput"],
                "mean_ttft_ms": data["mean_ttft_ms"],
                "mean_tpot_ms": data["mean_tpot_ms"],
                "acceptance_rate": data.get("spec_decode_acceptance_rate"),
                "acceptance_length": data.get("spec_decode_acceptance_length"),
                "total_input_tokens": data["total_input_tokens"],
                "total_output_tokens": data["total_output_tokens"],
                "artifact": f"results/{path.name}",
            }
        )
    return rows


def main() -> None:
    rows = load_rows()
    index = {
        (
            row["target"],
            row["spec_tokens"],
            row["input_len"],
            row["output_len"],
            row["concurrency"],
        ): row
        for row in rows
    }
    comparisons = []
    for input_len, output_len in ((1024, 2048), (2048, 1024), (2048, 1536)):
        for concurrency in (1, 2, 4, 8):
            for spec in (4, 8, 16):
                bf16 = index.get(("bf16", spec, input_len, output_len, concurrency))
                fp8 = index.get(("fp8", spec, input_len, output_len, concurrency))
                if bf16 is None or fp8 is None:
                    continue
                ratio = float(fp8["output_throughput"]) / float(bf16["output_throughput"])
                comparisons.append(
                    {
                        "input_len": input_len,
                        "output_len": output_len,
                        "concurrency": concurrency,
                        "spec_tokens": spec,
                        "bf16_output_throughput": bf16["output_throughput"],
                        "fp8_output_throughput": fp8["output_throughput"],
                        "fp8_over_bf16": ratio,
                        "throughput_delta_percent": (ratio - 1) * 100,
                        "bf16_acceptance_rate": bf16["acceptance_rate"],
                        "fp8_acceptance_rate": fp8["acceptance_rate"],
                    }
                )

    status_counts = Counter(
        "success" if row["completed"] == 16 and row["failed"] == 0 else "partial_or_failed"
        for row in rows
    )
    payload = {
        "experiment_id": "exp-003",
        "status": "completed" if len(rows) == EXPECTED_RUNS and status_counts["success"] == EXPECTED_RUNS else "partial",
        "expected_runs": EXPECTED_RUNS,
        "observed_runs": len(rows),
        "status_counts": dict(status_counts),
        "metrics": {
            "primary": {
                "name": "output_throughput_tokens_per_second",
                "higher_is_better": True,
            }
        },
        "variants": rows,
        "target_comparisons": comparisons,
        "artifacts": {
            "results_md": "results/results.md",
            "logs": ["logs/"],
        },
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "scores.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"wrote {len(rows)}/{EXPECTED_RUNS} runs and "
        f"{len(comparisons)}/36 target comparisons"
    )


if __name__ == "__main__":
    main()

