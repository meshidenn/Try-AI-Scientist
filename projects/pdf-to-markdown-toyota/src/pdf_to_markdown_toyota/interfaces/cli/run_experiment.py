"""Toyota PDFのParse-first/Image-first比較実験CLI。"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import fitz

from pdf_to_markdown_toyota.application.constants import MODEL_ID, MODEL_NAME
from pdf_to_markdown_toyota.application.prompts import html_prompt, normalize_markdown, prompt
from pdf_to_markdown_toyota.domain.models import DOCUMENTS
from pdf_to_markdown_toyota.infrastructure.local_model import ModelRunner
from pdf_to_markdown_toyota.infrastructure.pdf import (
    block_records,
    page_text,
    parse_first_payload,
    prepare_documents,
    render_page,
    select_pages,
    write_json,
)


def run_method(
    method: str,
    pdf_dir: Path,
    output_root: Path,
    metadata: dict[str, Any],
    run_model: bool,
    model_runner: ModelRunner | None,
    max_pages: int,
) -> list[dict[str, Any]]:
    """指定方式でPDFページを変換し、ページ単位の結果を返す。"""
    results: list[dict[str, Any]] = []
    for spec in DOCUMENTS:
        pdf_path = pdf_dir / spec.filename
        if not pdf_path.exists():
            results.append({"method": method, "document": spec.key, "status": "not_run", "reason": "PDF not found"})
            continue
        with fitz.open(pdf_path) as document:
            selected_pages = select_pages(document, max_pages)
            for page_index in selected_pages:
                page = document[page_index]
                page_dir = output_root / method / spec.key
                page_dir.mkdir(parents=True, exist_ok=True)
                image_path: Path | None = None
                if method == "image_first":
                    image_path = page_dir / f"page-{page_index + 1:04d}.png"
                    render_page(page, image_path)
                    content_hint = str(image_path)
                else:
                    content_hint = parse_first_payload(page)
                    (page_dir / f"page-{page_index + 1:04d}.input.json").write_text(content_hint + "\n", encoding="utf-8")
                record: dict[str, Any] = {
                    "method": method,
                    "document": spec.key,
                    "page": page_index + 1,
                    "status": "not_run",
                    "input_text_length": len(page_text(page)),
                    "model": MODEL_NAME,
                    "model_id": MODEL_ID,
                }
                if not run_model:
                    record["reason"] = "run_model was not requested"
                elif model_runner is None or model_runner.reason:
                    record["reason"] = model_runner.reason if model_runner else "model runner unavailable"
                else:
                    started = time.perf_counter()
                    try:
                        output = model_runner.generate(prompt(method, page_index + 1, content_hint), image_path)
                        output_path = page_dir / f"page-{page_index + 1:04d}.md"
                        output_path.write_text(normalize_markdown(output), encoding="utf-8")
                        record.update({"status": "success", "output_path": str(output_path), "wall_time_seconds": time.perf_counter() - started})
                    except Exception as exc:  # noqa: BLE001 - 失敗をページ単位で記録する
                        record.update({"status": "failed", "reason": f"{type(exc).__name__}: {exc}", "wall_time_seconds": time.perf_counter() - started})
                results.append(record)
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-model", action="store_true")
    parser.add_argument("--max-new-tokens", type=int, default=4096)
    parser.add_argument("--max-pages", type=int, default=3)
    parser.add_argument("--root", type=Path, required=True, help="結果を保存する experiments/exp-xxx ディレクトリ")
    args = parser.parse_args()
    root = args.root
    pdf_dir = root / "workspace" / "input" / "pdfs"
    metadata_path = root / "workspace" / "input" / "documents.json"
    output_root = root / "workspace" / "outputs"
    metadata = prepare_documents(pdf_dir, metadata_path)
    runner: ModelRunner | None = None
    if args.run_model:
        runner = ModelRunner(MODEL_ID, args.max_new_tokens)
        if not runner.load():
            print(json.dumps({"model_status": "not_run", "reason": runner.reason}, ensure_ascii=False))
    all_records: list[dict[str, Any]] = []
    for method in ("parse_first", "image_first"):
        all_records.extend(run_method(method, pdf_dir, output_root, metadata, args.run_model, runner, args.max_pages))
    log_path = root / "logs" / "run.json"
    write_json(log_path, {"model": MODEL_NAME, "model_id": MODEL_ID, "run_model": args.run_model, "records": all_records})
    print(json.dumps({"metadata": str(metadata_path), "log": str(log_path), "records": len(all_records)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
