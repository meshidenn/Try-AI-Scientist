#!/usr/bin/env python3
"""line-aware n-gram評価結果をモデル別HTMLへ表示する。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import fitz

from evaluate_box_aware_page_ngrams import output_units, score_page
from evaluate_line_aware_page_ngrams import pdf_text_lines
from render_box_aware_ngram_html import page_html
from run_general_vlm import load_source_pdf_dir
from run_experiment import DOCUMENTS


def run(root: Path) -> dict[str, object]:
    """line-aware page_ngrams.jsonからHTMLを生成する。"""
    root = root.resolve()
    result = json.loads((root / "results" / "page_ngrams.json").read_text(encoding="utf-8"))
    source_dir = load_source_pdf_dir(root)
    pdf_by_document = {spec.key: source_dir / spec.filename for spec in DOCUMENTS}
    artifacts: list[dict[str, object]] = []
    for record in result["records"]:
        document, page, model = str(record["document"]), int(record["page"]), str(record["model"])
        source_markdown = Path(record["output_path"])
        markdown = source_markdown.read_text(encoding="utf-8")
        output_values = output_units(markdown, record.get("output_format", "markdown"))
        with fitz.open(pdf_by_document[document]) as pdf:
            reference_values = pdf_text_lines(pdf[page - 1])
        scored = score_page(reference_values, output_values)
        rendered = page_html(model, document, page, markdown, reference_values, output_values, scored)
        rendered = rendered.replace("PDF text block（漏れ位置）", "PDF text line（漏れ位置）")
        rendered = rendered.replace("同一PDF text block内に一致", "同一PDF text line内に一致")
        rendered = rendered.replace("PDF text blockとMarkdown行・表セル", "PDF text lineとMarkdown行・表セル")
        output = root / "outputs" / "ngram-match-html" / model / document / f"page-{page:04d}.html"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        artifacts.append({"model": model, "document": document, "page": page, "html": str(output), "source_markdown": str(source_markdown)})
    manifest = {"experiment_id": root.name, "method": result["method"], "unit": "pdf_text_line", "n_values": result["n_values"], "html_count": len(artifacts), "artifacts": artifacts}
    path = root / "results" / "ngram_html_manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"result": str(path), "html_count": len(artifacts)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.root), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
