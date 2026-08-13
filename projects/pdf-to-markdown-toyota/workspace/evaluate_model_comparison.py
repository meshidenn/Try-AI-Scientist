#!/usr/bin/env python3
"""複数のローカルモデル実行ログを、モデル名を保ったまま評価する。"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

import fitz

from evaluate_outputs import markdown_table_shapes, normalize_text, numeric_tokens
from run_experiment import DOCUMENTS, page_text
from run_general_vlm import load_source_pdf_dir


def score_record(record: dict[str, Any], pdf_path: Path) -> dict[str, Any]:
    if record.get("status") != "success":
        return {"status": record.get("status", "not_run"), "reason": record.get("reason", "")}
    output = Path(record["output_path"]).read_text(encoding="utf-8")
    with fitz.open(pdf_path) as document:
        reference = page_text(document[record["page"] - 1])
    reference_numbers = numeric_tokens(reference)
    output_numbers = numeric_tokens(output)
    matched = reference_numbers & output_numbers
    recall = len(matched) / len(reference_numbers) if reference_numbers else None
    precision = len(matched) / len(output_numbers) if output_numbers else None
    f1 = 2 * recall * precision / (recall + precision) if recall and precision else 0.0
    reference_norm = normalize_text(reference)
    output_norm = normalize_text(output)
    text_proxy = 1.0 - abs(len(reference_norm) - len(output_norm)) / max(len(reference_norm), len(output_norm)) if reference_norm and output_norm else 0.0
    shapes = markdown_table_shapes(output)
    return {
        "status": "success",
        "text_normalized_similarity_proxy": round(max(text_proxy, 0.0), 6),
        "numeric_token_recall": round(recall, 6) if recall is not None else None,
        "numeric_token_precision": round(precision, 6) if precision is not None else None,
        "numeric_token_f1": round(f1, 6),
        "reference_numeric_token_count": len(reference_numbers),
        "output_numeric_token_count": len(output_numbers),
        "matched_numeric_token_count": len(matched),
        "table_shapes": shapes,
        "table_row_width_consistent": all(shape[2] for shape in shapes) if shapes else None,
    }


def aggregate(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[(record.get("model", "unknown"), record.get("method", "unknown"))].append(record)
    summary = []
    for (model, method), group in sorted(groups.items()):
        successful = [item for item in group if item["metrics"]["status"] == "success"]
        row: dict[str, Any] = {"model": model, "method": method, "records": len(group), "successes": len(successful)}
        for metric in ("text_normalized_similarity_proxy", "numeric_token_recall", "numeric_token_precision", "numeric_token_f1", "wall_time_seconds"):
            values = [item["metrics"].get(metric, item.get(metric)) for item in successful]
            values = [value for value in values if isinstance(value, (int, float))]
            row[metric] = round(mean(values), 6) if values else None
        row["consistent_table_pages"] = sum(item["metrics"].get("table_row_width_consistent") is True for item in successful)
        summary.append(row)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--pdf-dir", type=Path, default=None)
    parser.add_argument("--log", type=Path, action="append", default=None)
    args = parser.parse_args()
    root = args.root.resolve()
    pdf_dir = args.pdf_dir.resolve() if args.pdf_dir else load_source_pdf_dir(root)
    log_paths = args.log or sorted(root.glob("logs/*-pilot.json"))
    pdf_by_document = {spec.key: pdf_dir / spec.filename for spec in DOCUMENTS}
    scored_records = []
    for log_path in log_paths:
        log = json.loads(log_path.read_text(encoding="utf-8"))
        for record in log.get("records", []):
            scored = dict(record)
            scored["metrics"] = score_record(record, pdf_by_document[record["document"]])
            scored_records.append(scored)
    result = {"experiment_id": root.name, "source_logs": [str(path) for path in log_paths], "records": scored_records, "summary": aggregate(scored_records)}
    output_path = root / "results" / "page_metrics.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": str(output_path), "records": len(scored_records)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
