#!/usr/bin/env python3
"""PDF text line境界と数値除外を考慮したページ内文字n-gram評価。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import fitz

from evaluate_box_aware_page_ngrams import (
    N_VALUES,
    aggregate_records,
    output_units,
    parse_model_log,
    read_log_records,
    score_page,
)
from run_experiment import DOCUMENTS
from run_general_vlm import load_source_pdf_dir


def pdf_text_lines(page: fitz.Page) -> list[str]:
    """PDFのdict text lineごとの文字列を座標順に取得する。"""
    lines: list[str] = []
    payload = page.get_text("dict", sort=False)
    for block in payload.get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            text = "".join(str(span.get("text", "")) for span in line.get("spans", [])).strip()
            if text:
                lines.append(text)
    return lines


def run(root: Path, model_logs: dict[str, Path], method: str, pdf_dir: Path | None) -> dict[str, Any]:
    """共通ページをline-awareに評価する。"""
    root = root.resolve()
    source_dir = pdf_dir.resolve() if pdf_dir else load_source_pdf_dir(root)
    pdf_by_document = {spec.key: source_dir / spec.filename for spec in DOCUMENTS}
    records_by_model = {model: read_log_records(path.resolve(), method) for model, path in sorted(model_logs.items())}
    shared_pages = set.intersection(*(set(records) for records in records_by_model.values()))
    if not shared_pages:
        raise ValueError("全モデルで共通する成功ページがありません")
    scored_records: list[dict[str, Any]] = []
    for model, records in records_by_model.items():
        for document, page in sorted(shared_pages):
            record = records[(document, page)]
            with fitz.open(pdf_by_document[document]) as pdf:
                reference_values = pdf_text_lines(pdf[page - 1])
            output_path = Path(record["output_path"])
            output_values = output_units(output_path.read_text(encoding="utf-8"), record.get("output_format", "markdown"))
            scored_records.append({"model": model, "method": method, "document": document, "page": page, "output_path": str(output_path), "metrics": score_page(reference_values, output_values)})
    result = {
        "experiment_id": root.name,
        "method": method,
        "n_values": list(N_VALUES),
        "definition": {
            "main_metric": "output_page_ngram_match_rate",
            "main_metric_definition": "各出力unitの非数値n-gramのうち、同じPDFページのいずれかのtext line内に存在する割合",
            "reference_metric_definition": "PDF text line内の非数値n-gramのうち、出力unitにも存在する割合",
            "text_box_boundary": "PDF get_text(dict)の各line内だけでn-gramを生成し、block内の別lineや別列を跨がない。出力側はMarkdownの行・表セル単位で生成する。",
            "numeric_exclusion": "NFKC後のNUMBER_PATTERNに一致する数値tokenを除外し、数値tokenを跨ぐn-gramも生成しない。",
            "counting": "各nのn-gramは重複を除いた集合として数え、ページを跨いだ一致は認めない。",
        },
        "source_logs": {model: str(path.resolve()) for model, path in sorted(model_logs.items())},
        "shared_pages": [{"document": document, "page": page} for document, page in sorted(shared_pages)],
        "records": scored_records,
        "summary": aggregate_records(scored_records),
    }
    result_path = root / "results" / "page_ngrams.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"result": str(result_path), "records": len(scored_records), "shared_pages": sorted(shared_pages), "summary": result["summary"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--model-log", type=parse_model_log, action="append", required=True)
    parser.add_argument("--method", default="hybrid")
    parser.add_argument("--pdf-dir", type=Path, default=None)
    args = parser.parse_args()
    print(json.dumps(run(args.root, dict(args.model_log), args.method, args.pdf_dir), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
