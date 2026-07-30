#!/usr/bin/env python3
"""exp-003の対応比較を要因別に集計し、JSONとMarkdownを生成する。"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import fmean


EXP_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = EXP_DIR / "results"
SCORES_PATH = RESULTS_DIR / "scores.json"
ANALYSIS_PATH = RESULTS_DIR / "factorial-analysis.json"
REPORT_PATH = RESULTS_DIR / "results.md"


def geometric_mean(values: list[float]) -> float:
    return math.exp(fmean(math.log(value) for value in values))


def marginal(
    rows: list[dict[str, object]], key: str
) -> list[dict[str, float | int]]:
    groups: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        groups[int(row[key])].append(float(row["fp8_over_bf16"]))
    return [
        {
            key: level,
            "geomean_fp8_over_bf16": geometric_mean(values),
            "delta_percent": (geometric_mean(values) - 1) * 100,
            "cell_count": len(values),
        }
        for level, values in sorted(groups.items())
    ]


def effect_range(rows: list[dict[str, float | int]]) -> float:
    values = [float(row["geomean_fp8_over_bf16"]) for row in rows]
    return max(values) / min(values)


def absolute_marginal(
    rows: list[dict[str, object]], target: str, key: str
) -> list[dict[str, float | int]]:
    groups: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        if row["target"] == target:
            groups[int(row[key])].append(float(row["output_throughput"]))
    return [
        {
            key: level,
            "geomean_output_throughput": geometric_mean(values),
            "cell_count": len(values),
        }
        for level, values in sorted(groups.items())
    ]


def absolute_effect_range(rows: list[dict[str, float | int]]) -> float:
    values = [float(row["geomean_output_throughput"]) for row in rows]
    return max(values) / min(values)


def interaction_residuals(
    rows: list[dict[str, object]],
) -> list[dict[str, float | int]]:
    by_workload: dict[tuple[int, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        key = (int(row["input_len"]), int(row["output_len"]))
        by_workload[key].append(row)

    output = []
    for (input_len, output_len), workload_rows in sorted(by_workload.items()):
        logs = [math.log(float(row["fp8_over_bf16"])) for row in workload_rows]
        grand = fmean(logs)
        spec_means = {
            spec: fmean(
                math.log(float(row["fp8_over_bf16"]))
                for row in workload_rows
                if int(row["spec_tokens"]) == spec
            )
            for spec in (4, 8, 16)
        }
        concurrency_means = {
            concurrency: fmean(
                math.log(float(row["fp8_over_bf16"]))
                for row in workload_rows
                if int(row["concurrency"]) == concurrency
            )
            for concurrency in (1, 2, 4, 8)
        }
        residuals = []
        for row in workload_rows:
            observed = math.log(float(row["fp8_over_bf16"]))
            additive = (
                spec_means[int(row["spec_tokens"])]
                + concurrency_means[int(row["concurrency"])]
                - grand
            )
            residuals.append(observed - additive)
        output.append(
            {
                "input_len": input_len,
                "output_len": output_len,
                "max_abs_log_residual": max(abs(value) for value in residuals),
                "max_multiplicative_residual": math.exp(
                    max(abs(value) for value in residuals)
                ),
                "rmse_log_residual": math.sqrt(fmean(value**2 for value in residuals)),
            }
        )
    return output


def fmt_ratio(value: float) -> str:
    return f"{value:.3f}x ({(value - 1) * 100:+.1f}%)"


def render_report(payload: dict[str, object], analysis: dict[str, object]) -> str:
    comparisons = list(payload["target_comparisons"])
    lines = [
        "# Results",
        "",
        "## Summary",
        "",
        "Status: completed. 72/72 runs succeeded and all 36 BF16/FP8 pairs are available.",
        "",
        f"FP8 was slower than BF16 in {analysis['fp8_slower_cells']}/36 cells. "
        f"The overall geometric-mean FP8/BF16 output-throughput ratio was "
        f"{fmt_ratio(float(analysis['overall_geomean_fp8_over_bf16']))}.",
        "",
        "## Setup",
        "",
        "See [`../spec.yaml`](../spec.yaml). Each cell used 16 measured prompts, "
        "2 warmups, `--ignore-eos`, and vLLM v0.24.0.",
        "",
        "## Marginal Effects",
        "",
        "Ratios are geometric means of matched FP8/BF16 output throughput. Values below 1 mean FP8 was slower.",
        "",
        "### By Spec Tokens",
        "",
        "| Spec tokens | FP8/BF16 | Cells |",
        "|---:|---:|---:|",
    ]
    for row in analysis["by_spec_tokens"]:
        lines.append(
            f"| {row['spec_tokens']} | "
            f"{fmt_ratio(float(row['geomean_fp8_over_bf16']))} | {row['cell_count']} |"
        )
    lines.extend(
        [
            "",
            "### By Concurrency",
            "",
            "| Concurrency | FP8/BF16 | Cells |",
            "|---:|---:|---:|",
        ]
    )
    for row in analysis["by_concurrency"]:
        lines.append(
            f"| {row['concurrency']} | "
            f"{fmt_ratio(float(row['geomean_fp8_over_bf16']))} | {row['cell_count']} |"
        )
    lines.extend(
        [
            "",
            "### Factor Range",
            "",
            "| Factor | Max/min marginal FP8/BF16 ratio |",
            "|---|---:|",
            f"| Spec tokens | {analysis['spec_effect_range']:.3f}x |",
            f"| Concurrency | {analysis['concurrency_effect_range']:.3f}x |",
            "",
            "The larger max/min range is the stronger marginal modifier of the FP8/BF16 ratio in this matrix. "
            "This is descriptive, not a variance-aware significance test.",
            "",
            "### Absolute Output Throughput",
            "",
            "These ranges describe absolute throughput within each precision. Concurrency and spec-token levels "
            "are each averaged geometrically over the other matrix dimensions.",
            "",
            "| Precision | Spec-token range | Concurrency range | Stronger absolute factor |",
            "|---|---:|---:|---|",
        ]
    )
    for target in ("bf16", "fp8"):
        target_analysis = analysis["absolute_by_target"][target]
        stronger = (
            "concurrency"
            if target_analysis["concurrency_effect_range"]
            > target_analysis["spec_effect_range"]
            else "spec tokens"
        )
        lines.append(
            f"| {target.upper()} | {target_analysis['spec_effect_range']:.3f}x | "
            f"{target_analysis['concurrency_effect_range']:.3f}x | {stronger} |"
        )
    lines.extend(
        [
            "",
            "## Detailed Matched Results",
        ]
    )

    for input_len, output_len in ((1024, 2048), (2048, 1024), (2048, 1536)):
        lines.extend(
            [
                "",
                f'<a id="random-in{input_len}-out{output_len}"></a>',
                f"### Random input={input_len}, output={output_len}",
                "",
                "| Concurrency | Spec | BF16 out tok/s | FP8 out tok/s | FP8/BF16 | BF16 accept (%) | FP8 accept (%) |",
                "|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        selected = [
            row
            for row in comparisons
            if row["input_len"] == input_len and row["output_len"] == output_len
        ]
        for row in sorted(selected, key=lambda item: (item["concurrency"], item["spec_tokens"])):
            lines.append(
                f"| {row['concurrency']} | {row['spec_tokens']} | "
                f"{row['bf16_output_throughput']:.2f} | {row['fp8_output_throughput']:.2f} | "
                f"{fmt_ratio(float(row['fp8_over_bf16']))} | "
                f"{row['bf16_acceptance_rate']:.3f} | {row['fp8_acceptance_rate']:.3f} |"
            )

    lines.extend(
        [
            "",
            "## Interaction Diagnostic",
            "",
            "A two-way additive model was fitted to log(FP8/BF16) within each workload. "
            "The residual reports how much a specific spec-token/concurrency pair departs from independent marginal effects.",
            "",
            "| Input | Output | Max residual multiplier | Log RMSE |",
            "|---:|---:|---:|---:|",
        ]
    )
    for row in analysis["interaction_by_workload"]:
        lines.append(
            f"| {row['input_len']} | {row['output_len']} | "
            f"{row['max_multiplicative_residual']:.3f}x | {row['rmse_log_residual']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "- Structured results: [`scores.json`](scores.json)",
            "- Factor analysis: [`factorial-analysis.json`](factorial-analysis.json)",
            "- Raw benchmark JSON: `*.benchmark.json` in this directory",
            "- Server and benchmark logs: [`../logs/`](../logs/)",
            "",
            "## Limitations",
            "",
            "Each matrix cell was run once. The 16 prompts expose within-cell latency variation, "
            "but repeated cell-level runs are still required before treating small ratio differences as stable.",
            "",
            "## Reproduction",
            "",
            "```bash",
            "bash projects/gemma4-fp8-mtp-acceptance/experiments/exp-003/workspace/run_factorial_matrix.sh",
            "uv run python projects/gemma4-fp8-mtp-acceptance/experiments/exp-003/workspace/summarize_results.py",
            "uv run python projects/gemma4-fp8-mtp-acceptance/experiments/exp-003/workspace/analyze_factorial.py",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    payload = json.loads(SCORES_PATH.read_text(encoding="utf-8"))
    comparisons = list(payload["target_comparisons"])
    if payload["status"] != "completed" or len(comparisons) != 36:
        raise RuntimeError("72 runs and 36 matched comparisons are required")

    by_spec = marginal(comparisons, "spec_tokens")
    by_concurrency = marginal(comparisons, "concurrency")
    variants = list(payload["variants"])
    absolute_by_target = {}
    for target in ("bf16", "fp8"):
        spec_rows = absolute_marginal(variants, target, "spec_tokens")
        concurrency_rows = absolute_marginal(variants, target, "concurrency")
        absolute_by_target[target] = {
            "by_spec_tokens": spec_rows,
            "by_concurrency": concurrency_rows,
            "spec_effect_range": absolute_effect_range(spec_rows),
            "concurrency_effect_range": absolute_effect_range(concurrency_rows),
        }
    ratios = [float(row["fp8_over_bf16"]) for row in comparisons]
    analysis = {
        "experiment_id": payload["experiment_id"],
        "comparison_count": len(comparisons),
        "overall_geomean_fp8_over_bf16": geometric_mean(ratios),
        "fp8_slower_cells": sum(value < 1 for value in ratios),
        "fp8_faster_or_equal_cells": sum(value >= 1 for value in ratios),
        "by_spec_tokens": by_spec,
        "by_concurrency": by_concurrency,
        "spec_effect_range": effect_range(by_spec),
        "concurrency_effect_range": effect_range(by_concurrency),
        "absolute_by_target": absolute_by_target,
        "interaction_by_workload": interaction_residuals(comparisons),
        "slowdown_cells": [
            row for row in comparisons if float(row["fp8_over_bf16"]) < 1
        ],
    }
    ANALYSIS_PATH.write_text(
        json.dumps(analysis, indent=2) + "\n", encoding="utf-8"
    )
    REPORT_PATH.write_text(render_report(payload, analysis), encoding="utf-8")
    print(
        f"wrote {ANALYSIS_PATH.name} and {REPORT_PATH.name}: "
        f"FP8 slower in {analysis['fp8_slower_cells']}/36 cells"
    )


if __name__ == "__main__":
    main()
