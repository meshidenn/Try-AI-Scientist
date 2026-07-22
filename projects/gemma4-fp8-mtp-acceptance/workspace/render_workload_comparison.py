#!/usr/bin/env python3
"""統合比較JSONを全行のMarkdown表へ変換する。"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def number(value: Any) -> str:
    if value is None:
        return "-"
    return f"{float(value):.2f}"


def percent(value: Any) -> str:
    if value is None:
        return "-"
    return f"{float(value):.2f}%"


def tokens(row: dict[str, Any]) -> str:
    bf16 = row["bf16_total_output_tokens"]
    fp8 = row["fp8_total_output_tokens"]
    if bf16 is None and fp8 is None:
        return "同一"
    return f"{bf16}/{fp8}"


def verdict(value: str) -> str:
    return {
        "fp8_faster": "FP8優位",
        "bf16_faster": "BF16優位",
        "parity": "同等",
        "not_comparable": "比較不能",
    }[value]


def random_table(rows: list[dict[str, Any]]) -> list[str]:
    order = {1: 1, 2: 2, 4: 3, 8: 4, 16: 5}
    lines = [
        "| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | 差分 | BF16 accept | FP8 accept | output tokens BF16/FP8 | 判定 |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in sorted(rows, key=lambda item: order[item["spec_tokens"]]):
        lines.append(
            f'| {row["spec_tokens"]} | {number(row["bf16_output_throughput"])} '
            f'| {number(row["fp8_output_throughput"])} '
            f'| {number(row["fp8_over_bf16"])}x '
            f'| {percent(row["throughput_delta_percent"])} '
            f'| {percent(row["bf16_acceptance_rate"])} '
            f'| {percent(row["fp8_acceptance_rate"])} '
            f'| {tokens(row)} | {verdict(row["verdict"])} |'
        )
    return lines


def agentic_table(rows: list[dict[str, Any]]) -> list[str]:
    order = {"off": 0, 1: 1, 2: 2, 4: 3, 8: 4, 16: 5}
    lines = [
        "| spec tokens | BF16 tok/s | FP8 tok/s | FP8/BF16 | 差分 | BF16 accept | FP8 accept | output tokens BF16/FP8 | 比較可能 | 判定 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for row in sorted(rows, key=lambda item: order[item["spec_tokens"]]):
        comparable = "yes" if row["output_length_comparable"] else "no"
        lines.append(
            f'| {row["spec_tokens"]} '
            f'| {number(row["bf16_output_throughput"])} '
            f'| {number(row["fp8_output_throughput"])} '
            f'| {number(row["fp8_over_bf16"])}x '
            f'| {percent(row["throughput_delta_percent"])} '
            f'| {percent(row["bf16_acceptance_rate"])} '
            f'| {percent(row["fp8_acceptance_rate"])} '
            f'| {tokens(row)} | {comparable} | {verdict(row["verdict"])} |'
        )
    return lines


def render(payload: dict[str, Any]) -> str:
    random_rows = payload["random"]["comparisons"]
    agentic_rows = payload["agentic_synthetic"]["comparisons"]
    lines = [
        "# Gemma 4 FP8/BF16 Workload Comparison",
        "",
        "`integrated-comparison.json`の全50比較をMarkdown表へ展開した詳細版。数値の正本は[統合JSON](integrated-comparison.json)。",
        "",
        "FP8/BF16のoutput throughput差が±5%以内なら「同等」。output token数が一致しないpairは「比較不能」とする。",
        "",
        "## Random Workload",
        "",
        "全32 pair。input/output/concurrencyを固定し、各表でspec depthによる変化を示す。spec 1/2/4とspec 8/16はprompt数と実施時期が異なるため、depthをまたぐ絶対throughput比較には注意する。",
        "",
    ]
    workloads = sorted(
        {
            (int(row["input_len"]), int(row["output_len"]), int(row["concurrency"]))
            for row in random_rows
        }
    )
    for input_len, output_len, concurrency in workloads:
        rows = [
            row
            for row in random_rows
            if row["input_len"] == input_len
            and row["output_len"] == output_len
            and row["concurrency"] == concurrency
        ]
        anchor = f"random-in{input_len}-out{output_len}-c{concurrency}"
        lines += [
            f'<a id="{anchor}"></a>',
            f"### Random input={input_len} output={output_len} concurrency={concurrency}",
            "",
            *random_table(rows),
            "",
        ]

    lines += [
        "## Agentic Synthetic Workload",
        "",
        "全18 pair。inputは1,006-4,993 token、output上限は512 token。output token数不一致の2 pairはcross-target判定から除外する。",
        "",
    ]
    for concurrency in (1, 2, 4):
        rows = [row for row in agentic_rows if row["concurrency"] == concurrency]
        lines += [
            f'<a id="agentic-concurrency-{concurrency}"></a>',
            f"### Agentic concurrency={concurrency}",
            "",
            *agentic_table(rows),
            "",
        ]

    lines += [
        "## Fields",
        "",
        "- `FP8/BF16`: output throughput比。1より大きい場合はFP8が高速。",
        "- `差分`: `(FP8/BF16 - 1) * 100`。",
        "- `accept`: speculative decoding acceptance rate。MTP offでは値なし。",
        "- `output tokens`: BF16/FP8のtotal output token。Random high-specは「同一」。",
        "- `判定`: ±5%以内は同等。output token不一致は比較不能。",
        "",
        "## Source Artifacts",
        "",
        "- [統合JSON](integrated-comparison.json)",
        "- [Random結果](../experiments/exp-001/results/results.md)",
        "- [Random high-spec比較](../experiments/exp-001/results/high_spec_comparison.json)",
        "- [Agentic結果](../experiments/exp-002/results/results.md)",
        "- [Agentic比較JSON](../experiments/exp-002/results/comparisons.json)",
        "",
    ]
    return "\n".join(lines)


def write_markdown(payload: dict[str, Any], output: Path) -> None:
    output.write_text(render(payload), encoding="utf-8")
