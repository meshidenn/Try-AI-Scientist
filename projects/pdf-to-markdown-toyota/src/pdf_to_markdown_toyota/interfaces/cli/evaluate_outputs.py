#!/usr/bin/env python3
"""生成MarkdownとPDF text layerを比較する軽量評価。"""

from __future__ import annotations

import argparse
import json
import html as html_lib
import re
import unicodedata
from pathlib import Path
from typing import Any

import fitz

from pdf_to_markdown_toyota.application.constants import NUMBER_PATTERN
from pdf_to_markdown_toyota.domain.models import DOCUMENTS
from pdf_to_markdown_toyota.infrastructure.pdf import page_text


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    return re.sub(r"\s+", "", text)


def numeric_tokens(text: str) -> set[str]:
    return {unicodedata.normalize("NFKC", token).replace(",", "") for token in NUMBER_PATTERN.findall(text)}


def markdown_table_shapes(text: str) -> list[tuple[int, int, bool]]:
    rows: list[list[str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    if not rows:
        return []
    width = max(len(row) for row in rows)
    return [(len(rows), width, len({len(row) for row in rows}) == 1)]


def html_text(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", html_lib.unescape(text))

def html_table_shapes(text: str) -> list[tuple[int, int, bool]]:
    shapes: list[tuple[int, int, bool]] = []
    for table in re.findall(r"<table\b[^>]*>(.*?)</table>", text, flags=re.IGNORECASE | re.DOTALL):
        widths = []
        for row in re.findall(r"<tr\b[^>]*>(.*?)</tr>", table, flags=re.IGNORECASE | re.DOTALL):
            cells = re.findall(r"<(?:th|td)\b([^>]*)>", row, flags=re.IGNORECASE)
            widths.append(sum(int(match.group(1)) if (match := re.search(r"\bcolspan=[\"\x27]?(\d+)", attributes, flags=re.IGNORECASE)) else 1 for attributes in cells))
        if widths:
            shapes.append((len(widths), max(widths), len(set(widths)) == 1))
    return shapes

def score_record(record: dict[str, Any], pdf_path: Path) -> dict[str, Any]:
    if record.get("status") != "success":
        return {"status": record.get("status", "not_run"), "reason": record.get("reason", "")}
    output_path = Path(record["output_path"])
    output = output_path.read_text(encoding="utf-8")
    output_format = record.get("output_format", "markdown")
    output_for_metrics = html_text(output) if output_format == "html" else output
    with fitz.open(pdf_path) as document:
        reference = page_text(document[record["page"] - 1])
    reference_numbers = numeric_tokens(reference)
    output_numbers = numeric_tokens(output_for_metrics)
    reference_norm = normalize_text(reference)
    output_norm = normalize_text(output_for_metrics)
    if reference_norm and output_norm:
        text_similarity = 1.0 - (abs(len(reference_norm) - len(output_norm)) / max(len(reference_norm), len(output_norm)))
    else:
        text_similarity = 0.0
    shapes = html_table_shapes(output) if output_format == "html" else markdown_table_shapes(output)
    return {
        "status": "success",
        "output_format": output_format,
        "text_normalized_similarity_proxy": round(max(0.0, text_similarity), 6),
        "numeric_token_recall": round(len(reference_numbers & output_numbers) / len(reference_numbers), 6) if reference_numbers else None,
        "reference_numeric_token_count": len(reference_numbers),
        "matched_numeric_token_count": len(reference_numbers & output_numbers),
        "table_shapes": shapes,
        "markdown_table_shapes": shapes,
        "table_row_width_consistent": all(shape[2] for shape in shapes) if shapes else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True, help="評価対象の experiments/exp-xxx ディレクトリ")
    parser.add_argument("--pdf-dir", type=Path, default=None)
    parser.add_argument("--log", type=Path, action="append", default=None, help="評価対象の実行ログJSON（複数指定時は同一ページを後のログで上書き）")
    args = parser.parse_args()
    root = args.root
    log_paths = args.log or [root / "logs" / "run.json"]
    input_root = args.pdf_dir or (root / "workspace" / "input" / "pdfs")
    logs = [json.loads(path.read_text(encoding="utf-8")) for path in log_paths]
    records_by_key: dict[tuple[str, str, int], dict[str, Any]] = {}
    for log in logs:
        for record in log.get("records", []):
            key = (record.get("method", ""), record.get("document", ""), int(record.get("page", 0)))
            records_by_key[key] = record
    pdf_by_key = {spec.key: input_root / spec.filename for spec in DOCUMENTS}
    scored_records = []
    for record in records_by_key.values():
        scored = dict(record)
        scored["metrics"] = score_record(record, pdf_by_key[record["document"]])
        scored_records.append(scored)
    output = {"experiment_id": root.name, "model": logs[0].get("model"), "source_logs": [str(path) for path in log_paths], "records": scored_records}
    result_path = root / "results" / "page_metrics.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": str(result_path), "records": len(scored_records)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
