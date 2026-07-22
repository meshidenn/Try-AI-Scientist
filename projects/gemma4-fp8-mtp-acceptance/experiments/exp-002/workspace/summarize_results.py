#!/usr/bin/env python3
"""benchmark JSON を比較しやすい scores.json に集約する。"""

from __future__ import annotations

import json
from pathlib import Path


EXP_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = EXP_DIR / "results"


def load_results() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted(RESULTS_DIR.glob("*_agent_c*.benchmark.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        rows.append(
            {
                "label": data["label"],
                "completed": data["completed"],
                "failed": data["failed"],
                "request_throughput": data["request_throughput"],
                "output_throughput": data["output_throughput"],
                "total_token_throughput": data["total_token_throughput"],
                "mean_ttft_ms": data["mean_ttft_ms"],
                "mean_tpot_ms": data["mean_tpot_ms"],
                "mean_e2el_ms": data.get("mean_e2el_ms"),
                "acceptance_rate": data.get("spec_decode_acceptance_rate"),
                "acceptance_length": data.get("spec_decode_acceptance_length"),
                "total_input_tokens": data["total_input_tokens"],
                "total_output_tokens": data["total_output_tokens"],
                "artifact": f"results/{path.name}",
            }
        )
    return rows


def main() -> None:
    rows = load_results()
    expected = 12 * 3
    status = "completed" if len(rows) == expected and all(row["failed"] == 0 for row in rows) else "partial"
    payload = {
        "experiment_id": "exp-002",
        "status": status,
        "expected_runs": expected,
        "completed_runs": len(rows),
        "metrics": {
            "primary": {
                "name": "output_throughput_tokens_per_second",
                "higher_is_better": True,
            }
        },
        "variants": rows,
        "artifacts": {
            "results_md": "results/results.md",
            "figures": [],
            "logs": ["logs/"],
        },
    }
    output = RESULTS_DIR / "scores.json"
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} rows to {output}")


if __name__ == "__main__":
    main()
