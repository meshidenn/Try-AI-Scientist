#!/usr/bin/env python3
"""複数モデルで共通する成功ページだけを文字n-gram評価する。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import fitz

from pdf_to_markdown_toyota.interfaces.cli.evaluate_page_ngrams import (
    N_VALUES,
    aggregate_records,
    parse_model_log,
    read_log_records,
    score_page,
)
from pdf_to_markdown_toyota.domain.models import DOCUMENTS
from pdf_to_markdown_toyota.infrastructure.pdf import page_text
from pdf_to_markdown_toyota.interfaces.cli.run_general_vlm import load_source_pdf_dir


def run(root: Path, model_logs: dict[str, Path], method: str, pdf_dir: Path | None) -> dict[str, Any]:
    """各モデルのログから共通ページを抽出し、評価結果を書き出す。"""
    root = root.resolve()
    source_dir = pdf_dir.resolve() if pdf_dir else load_source_pdf_dir(root)
    pdf_by_document = {spec.key: source_dir / spec.filename for spec in DOCUMENTS}
    records_by_model = {
        model: read_log_records(log_path.resolve(), method)
        for model, log_path in sorted(model_logs.items())
    }
    shared_pages = set.intersection(*(set(records) for records in records_by_model.values()))
    if not shared_pages:
        raise ValueError("全モデルで共通する成功ページがありません")

    scored_records: list[dict[str, Any]] = []
    for model, records in records_by_model.items():
        for document, page in sorted(shared_pages):
            record = records[(document, page)]
            with fitz.open(pdf_by_document[document]) as pdf:
                reference = page_text(pdf[page - 1])
            output_path = Path(record["output_path"])
            output = output_path.read_text(encoding="utf-8")
            scored_records.append(
                {
                    "model": model,
                    "method": method,
                    "document": document,
                    "page": page,
                    "output_path": str(output_path),
                    "metrics": score_page(reference, output, record.get("output_format", "markdown")),
                }
            )

    result = {
        "experiment_id": root.name,
        "method": method,
        "n_values": list(N_VALUES),
        "definition": {
            "main_metric": "output_page_ngram_match_rate",
            "main_metric_definition": "出力Markdownのユニーク文字n-gramのうち、同じPDFページのtext layer内に存在する割合",
            "reference_metric_definition": "PDFページのユニーク文字n-gramのうち、出力Markdownにも存在する割合",
            "normalization": "NFKC、空白除去、Markdown/HTML表示構文の除去。文字の順序は維持する。",
            "counting": "各nのn-gramは重複を除いた集合として数える。ページをまたいで一致させない。",
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
    model_logs = dict(args.model_log)
    print(json.dumps(run(args.root, model_logs, args.method, args.pdf_dir), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
