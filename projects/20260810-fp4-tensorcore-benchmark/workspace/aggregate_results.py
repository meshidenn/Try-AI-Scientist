import argparse
import json
from pathlib import Path


FIELDS = [
    "label",
    "model_id",
    "num_prompts",
    "max_concurrency",
    "request_throughput",
    "output_throughput",
    "total_token_throughput",
    "mean_ttft_ms",
    "median_ttft_ms",
    "p99_ttft_ms",
    "mean_tpot_ms",
    "median_tpot_ms",
    "p99_tpot_ms",
    "total_input_tokens",
    "total_output_tokens",
    "completed",
    "errors",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    rows = []
    for path in sorted((root / "logs").glob("*.json")):
        if path.name in {"run-manifest.json", "scores.json"}:
            continue
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if "request_throughput" not in raw:
            continue
        row = {field: raw.get(field) for field in FIELDS}
        row["label"] = path.stem
        row["model_id"] = path.stem.split("__", 1)[0]
        row["artifact"] = str(path.relative_to(root))
        rows.append(row)
    output = {
        "experiment_id": "exp-001",
        "status": "completed" if rows else "failed",
        "rows": rows,
        "metrics": {
            "primary": {
                "name": "output_throughput",
                "higher_is_better": True,
                "values": [row["output_throughput"] for row in rows],
            },
            "latency": {
                "name": "mean_ttft_ms",
                "lower_is_better": True,
                "values": [row["mean_ttft_ms"] for row in rows],
            },
        },
        "artifacts": {
            "results_md": "results/results.md",
            "logs": [row["artifact"] for row in rows],
        },
    }
    results_dir = root / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "scores.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Results",
        "",
        "## Summary",
        "",
        f"完了したbenchmark resultは{len(rows)}件。数値は各raw JSONと照合できる。",
        "",
        "## Setup",
        "",
        "vLLM `0.26.0`、NVIDIA GB10、CUDA 13.0。BF16とNVFP4 W4A4を同じserver設定で比較した。",
        "",
        "## Metrics",
        "",
        "throughputはtokens/s、latencyはms。TTFTはtime to first token、TPOTはtime per output token。vLLM benchの保存JSONにはE2E latency項目がないため、E2Eは集計しない。",
        "",
        "## Main Results",
        "",
        "| label | concurrency | output tok/s | mean TTFT ms | p99 TTFT ms | mean TPOT ms |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['label']} | {row['max_concurrency']} | {row['output_throughput']} | "
            f"{row['mean_ttft_ms']} | {row['p99_ttft_ms']} | {row['mean_tpot_ms']} |"
        )
    lines.extend([
        "",
        "## Figures",
        "",
        "図は未作成。raw JSONから再集計可能。",
        "",
        "## Failures And Negative Results",
        "",
        "失敗・未実行条件はrun-manifest.jsonと各failure.logを参照する。",
        "",
        "## Reproduction",
        "",
        "`workspace/quantize_qwen35_nvfp4.py`実行後、`workspace/run_benchmark.py --root experiments/exp-001`を実行する。",
        "",
        "## Notes For Reviewer",
        "",
        "FP4 Tensor Core利用はserver logのkernel選択で確認し、nvidia-smiのSM使用率だけから命令単位の利用率を推定しない。",
        "",
    ])
    (results_dir / "results.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
