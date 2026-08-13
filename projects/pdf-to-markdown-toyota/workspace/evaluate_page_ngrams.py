#!/usr/bin/env python3
"""PDFページのtext layerと生成Markdownを文字n-gramで比較する。"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

import fitz

from run_experiment import DOCUMENTS, page_text
from run_general_vlm import load_source_pdf_dir


N_VALUES = tuple(range(1, 11))


def normalize_for_ngrams(text: str, output_format: str = "markdown") -> str:
    """表示上の構文を除き、ページ内文字列比較用に正規化する。"""
    if output_format == "html":
        text = re.sub(r"<[^>]+>", " ", text)
        text = html_lib.unescape(text)

    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("|") and line.endswith("|"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if cells and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                continue
            line = " ".join(cells)
        line = re.sub(r"^\s{0,3}#{1,6}\s+", "", line)
        line = re.sub(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)", "", line)
        line = re.sub(r"!\[([^]]*)\]\([^)]*\)", r"\1", line)
        line = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", line)
        line = line.replace("**", "").replace("__", "").replace("`", "")
        lines.append(line)
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", " ".join(lines)))


def character_ngrams(text: str, n: int) -> set[str]:
    """文字列から重複を除いた長さnの連続部分文字列を作る。"""
    if n <= 0:
        raise ValueError("nは正の整数である必要があります")
    return {text[index : index + n] for index in range(len(text) - n + 1)}


def score_page(reference: str, output: str, output_format: str = "markdown") -> dict[str, Any]:
    """1ページの出力とPDF参照文字列をn=1〜10で比較する。"""
    reference_norm = normalize_for_ngrams(reference)
    output_norm = normalize_for_ngrams(output, output_format)
    metrics: list[dict[str, Any]] = []
    for n in N_VALUES:
        reference_ngrams = character_ngrams(reference_norm, n)
        output_ngrams = character_ngrams(output_norm, n)
        matched = reference_ngrams & output_ngrams
        output_match_rate = len(matched) / len(output_ngrams) if output_ngrams else None
        reference_coverage = len(matched) / len(reference_ngrams) if reference_ngrams else None
        if output_match_rate is not None and reference_coverage is not None and output_match_rate + reference_coverage:
            f1 = 2 * output_match_rate * reference_coverage / (output_match_rate + reference_coverage)
        else:
            f1 = None
        metrics.append(
            {
                "n": n,
                "reference_ngram_count": len(reference_ngrams),
                "output_ngram_count": len(output_ngrams),
                "matched_ngram_count": len(matched),
                "output_page_ngram_match_rate": round(output_match_rate, 6) if output_match_rate is not None else None,
                "reference_page_ngram_coverage": round(reference_coverage, 6) if reference_coverage is not None else None,
                "f1": round(f1, 6) if f1 is not None else None,
            }
        )
    return {
        "reference_normalized_length": len(reference_norm),
        "output_normalized_length": len(output_norm),
        "metrics": metrics,
    }


def read_log_records(log_path: Path, method: str) -> dict[tuple[str, int], dict[str, Any]]:
    """指定methodの成功出力だけをページキーで読み込む。"""
    records: dict[tuple[str, int], dict[str, Any]] = {}
    payload = json.loads(log_path.read_text(encoding="utf-8"))
    for record in payload.get("records", []):
        if record.get("status") != "success" or record.get("method") != method:
            continue
        output_path = Path(record["output_path"])
        if not output_path.is_file() or output_path.stat().st_size == 0:
            raise FileNotFoundError(output_path)
        records[(str(record["document"]), int(record["page"]))] = record
    return records


def aggregate_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    """モデル単位のページ平均と全体のn別平均を作る。"""
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_model[str(record["model"])].append(record)

    def aggregate(group: list[dict[str, Any]]) -> list[dict[str, Any]]:
        rows = []
        for n in N_VALUES:
            values = [item["metrics"]["metrics"][n - 1] for item in group]
            row: dict[str, Any] = {"n": n, "records": len(values)}
            for key in ("output_page_ngram_match_rate", "reference_page_ngram_coverage", "f1"):
                numeric = [item[key] for item in values if isinstance(item[key], (int, float))]
                row[key] = round(mean(numeric), 6) if numeric else None
            rows.append(row)
        return rows

    model_summary = {model: aggregate(group) for model, group in sorted(by_model.items())}
    all_summary = aggregate(records)
    return {"by_model": model_summary, "overall": all_summary}


def run(root: Path, model_logs: dict[str, Path], method: str, pdf_dir: Path | None) -> dict[str, Any]:
    """既存モデルログを読み、ページ単位のn-gram評価artifactを作る。"""
    root = root.resolve()
    source_dir = pdf_dir.resolve() if pdf_dir else load_source_pdf_dir(root)
    pdf_by_document = {spec.key: source_dir / spec.filename for spec in DOCUMENTS}
    scored_records: list[dict[str, Any]] = []
    for model, log_path in sorted(model_logs.items()):
        for (document, page), record in sorted(read_log_records(log_path.resolve(), method).items()):
            pdf_path = pdf_by_document[document]
            with fitz.open(pdf_path) as pdf:
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
    if not scored_records:
        raise ValueError("評価可能な成功ページがありません")
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
        "records": scored_records,
        "summary": aggregate_records(scored_records),
    }
    result_path = root / "results" / "page_ngrams.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"result": str(result_path), "records": len(scored_records), "summary": result["summary"]}


def parse_model_log(value: str) -> tuple[str, Path]:
    """MODEL=PATH形式のCLI引数を解釈する。"""
    if "=" not in value:
        raise argparse.ArgumentTypeError("--model-logはMODEL=PATHの形式です")
    model, path = value.split("=", 1)
    return model, Path(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--model-log", type=parse_model_log, action="append", required=True)
    parser.add_argument("--method", default="hybrid")
    parser.add_argument("--pdf-dir", type=Path, default=None)
    args = parser.parse_args()
    model_logs = dict(args.model_log)
    if not model_logs:
        parser.error("少なくとも1モデルの--model-logが必要です")
    print(json.dumps(run(args.root, model_logs, args.method, args.pdf_dir), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
