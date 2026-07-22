#!/usr/bin/env python3
"""exp-001 の全benchmarkとhigh-spec比較を構造化する。"""

from __future__ import annotations

import json
import re
from pathlib import Path


EXP_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = EXP_DIR / "results"
HIGH_SPEC_PATTERN = re.compile(
    r"^(?P<target>bf16|fp8)_s(?P<spec>8|16)_"
    r"in(?P<input>\d+)_out(?P<output>\d+)_c(?P<concurrency>\d+)$"
)


def metric_row(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "label": data["label"],
        "completed": data["completed"],
        "failed": data["failed"],
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


def ratio(numerator: float, denominator: float) -> float:
    return numerator / denominator


def main() -> None:
    rows = [metric_row(path) for path in sorted(RESULTS_DIR.glob("*.benchmark.json"))]
    high_spec: dict[tuple[str, int, int, int, int], dict[str, object]] = {}
    for row in rows:
        match = HIGH_SPEC_PATTERN.match(str(row["label"]))
        if not match:
            continue
        key = (
            match["target"],
            int(match["spec"]),
            int(match["input"]),
            int(match["output"]),
            int(match["concurrency"]),
        )
        high_spec[key] = row

    workloads = sorted({key[2:] for key in high_spec})
    s16_vs_s8 = []
    fp8_vs_bf16 = []
    for input_len, output_len, concurrency in workloads:
        for target in ("bf16", "fp8"):
            s8 = high_spec[(target, 8, input_len, output_len, concurrency)]
            s16 = high_spec[(target, 16, input_len, output_len, concurrency)]
            s16_vs_s8.append(
                {
                    "target": target,
                    "input_len": input_len,
                    "output_len": output_len,
                    "concurrency": concurrency,
                    "s8_output_throughput": s8["output_throughput"],
                    "s16_output_throughput": s16["output_throughput"],
                    "throughput_ratio": ratio(
                        float(s16["output_throughput"]),
                        float(s8["output_throughput"]),
                    ),
                    "s8_acceptance_rate": s8["acceptance_rate"],
                    "s16_acceptance_rate": s16["acceptance_rate"],
                }
            )
        for spec in (8, 16):
            bf16 = high_spec[("bf16", spec, input_len, output_len, concurrency)]
            fp8 = high_spec[("fp8", spec, input_len, output_len, concurrency)]
            fp8_vs_bf16.append(
                {
                    "spec_tokens": spec,
                    "input_len": input_len,
                    "output_len": output_len,
                    "concurrency": concurrency,
                    "bf16_output_throughput": bf16["output_throughput"],
                    "fp8_output_throughput": fp8["output_throughput"],
                    "throughput_ratio": ratio(
                        float(fp8["output_throughput"]),
                        float(bf16["output_throughput"]),
                    ),
                    "bf16_acceptance_rate": bf16["acceptance_rate"],
                    "fp8_acceptance_rate": fp8["acceptance_rate"],
                }
            )

    scores = {
        "experiment_id": "exp-001",
        "status": "completed",
        "benchmark_files": len(rows),
        "metrics": {
            "primary": {
                "name": "output_throughput_tokens_per_second",
                "higher_is_better": True,
            }
        },
        "variants": rows,
        "artifacts": {
            "results_md": "results/results.md",
            "high_spec_comparison": "results/high_spec_comparison.json",
            "figures": [],
            "logs": ["logs/"],
        },
    }
    comparison = {
        "experiment_id": "exp-001",
        "high_spec_run_count": len(high_spec),
        "s16_vs_s8": s16_vs_s8,
        "fp8_vs_bf16": fp8_vs_bf16,
    }
    (RESULTS_DIR / "scores.json").write_text(
        json.dumps(scores, indent=2) + "\n",
        encoding="utf-8",
    )
    (RESULTS_DIR / "high_spec_comparison.json").write_text(
        json.dumps(comparison, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(rows)} benchmark rows and {len(high_spec)} high-spec rows")


if __name__ == "__main__":
    main()
