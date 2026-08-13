#!/usr/bin/env python3
"""PDF text block境界と数値除外を考慮したページ内文字n-gram評価。"""

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

from evaluate_outputs import NUMBER_PATTERN
from run_experiment import DOCUMENTS, page_text
from run_general_vlm import load_source_pdf_dir


N_VALUES = tuple(range(1, 11))


def clean_output_unit(text: str, output_format: str = "markdown") -> str:
    """Markdown/HTMLの表示構文を除き、1つの出力単位を正規化する。"""
    if output_format == "html":
        text = re.sub(r"<[^>]+>", " ", text)
        text = html_lib.unescape(text)
    text = re.sub(r"^\s{0,3}#{1,6}\s+", "", text.strip())
    text = re.sub(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)", "", text)
    text = re.sub(r"!\[([^]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", text)
    return text.replace("**", "").replace("__", "").replace("`", "")


def output_units(markdown: str, output_format: str = "markdown") -> list[str]:
    """Markdownの行・表セルを、単位を跨がないリストへ変換する。"""
    units: list[str] = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("|") and line.endswith("|"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if cells and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                continue
            units.extend(clean_output_unit(cell, output_format) for cell in cells if clean_output_unit(cell, output_format))
        else:
            value = clean_output_unit(line, output_format)
            if value:
                units.append(value)
    return units


def pdf_text_blocks(page: fitz.Page) -> list[str]:
    """PDF pageのtext blockごとの文字列を取得する。"""
    blocks: list[str] = []
    for block in page.get_text("blocks", sort=False):
        if len(block) >= 7 and int(block[6]) != 0:
            continue
        value = str(block[4]).strip()
        if value:
            blocks.append(value)
    return blocks


def normalize_block(text: str) -> str:
    """text block内の空白を除去し、UnicodeをNFKCへそろえる。"""
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", text))


def numeric_free_segments(unit: str) -> list[str]:
    """数値tokenを境界として除去し、数値を跨がない文字列segmentを返す。"""
    normalized = normalize_block(unit)
    return [segment for segment in NUMBER_PATTERN.split(normalized) if segment]


def ngrams_from_units(units: list[str], n: int) -> set[str]:
    """各unit・各非数値segment内だけで重複なしn-gram集合を作る。"""
    if n <= 0:
        raise ValueError("nは正の整数である必要があります")
    result: set[str] = set()
    for unit in units:
        for segment in numeric_free_segments(unit):
            result.update(segment[index : index + n] for index in range(len(segment) - n + 1))
    return result


def numeric_token_count(units: list[str]) -> int:
    """評価対象から除外した数値token数を数える。"""
    return sum(len(NUMBER_PATTERN.findall(normalize_block(unit))) for unit in units)


def score_page(reference_units: list[str], output_unit_values: list[str]) -> dict[str, Any]:
    """PDF block単位と出力単位を、数値除外後のn-gramで比較する。"""
    reference_segments = [segment for unit in reference_units for segment in numeric_free_segments(unit)]
    output_segments = [segment for unit in output_unit_values for segment in numeric_free_segments(unit)]
    metrics: list[dict[str, Any]] = []
    for n in N_VALUES:
        reference_ngrams = ngrams_from_units(reference_units, n)
        output_ngrams = ngrams_from_units(output_unit_values, n)
        matched = reference_ngrams & output_ngrams
        output_rate = len(matched) / len(output_ngrams) if output_ngrams else None
        reference_rate = len(matched) / len(reference_ngrams) if reference_ngrams else None
        f1 = 2 * output_rate * reference_rate / (output_rate + reference_rate) if output_rate is not None and reference_rate is not None and output_rate + reference_rate else None
        metrics.append(
            {
                "n": n,
                "reference_ngram_count": len(reference_ngrams),
                "output_ngram_count": len(output_ngrams),
                "matched_ngram_count": len(matched),
                "output_page_ngram_match_rate": round(output_rate, 6) if output_rate is not None else None,
                "reference_page_ngram_coverage": round(reference_rate, 6) if reference_rate is not None else None,
                "f1": round(f1, 6) if f1 is not None else None,
            }
        )
    return {
        "reference_block_count": len(reference_units),
        "output_unit_count": len(output_unit_values),
        "reference_numeric_token_count_excluded": numeric_token_count(reference_units),
        "output_numeric_token_count_excluded": numeric_token_count(output_unit_values),
        "reference_numeric_free_length": sum(map(len, reference_segments)),
        "output_numeric_free_length": sum(map(len, output_segments)),
        "metrics": metrics,
    }


def read_log_records(log_path: Path, method: str) -> dict[tuple[str, int], dict[str, Any]]:
    """指定methodの成功出力をページキーで読む。"""
    records: dict[tuple[str, int], dict[str, Any]] = {}
    for record in json.loads(log_path.read_text(encoding="utf-8")).get("records", []):
        if record.get("status") != "success" or record.get("method") != method:
            continue
        path = Path(record["output_path"])
        if not path.is_file() or path.stat().st_size == 0:
            raise FileNotFoundError(path)
        records[(str(record["document"]), int(record["page"]))] = record
    return records


def aggregate_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    """モデル単位と全体のn別平均を作る。"""
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_model[str(record["model"])].append(record)

    def aggregate(group: list[dict[str, Any]]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for n in N_VALUES:
            values = [item["metrics"]["metrics"][n - 1] for item in group]
            row: dict[str, Any] = {"n": n, "records": len(values)}
            for key in ("output_page_ngram_match_rate", "reference_page_ngram_coverage", "f1"):
                numeric = [item[key] for item in values if isinstance(item[key], (int, float))]
                row[key] = round(mean(numeric), 6) if numeric else None
            rows.append(row)
        return rows

    return {"by_model": {model: aggregate(group) for model, group in sorted(by_model.items())}, "overall": aggregate(records)}


def run(root: Path, model_logs: dict[str, Path], method: str, pdf_dir: Path | None) -> dict[str, Any]:
    """共通ページのPDF block-aware n-gram評価を実行する。"""
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
                reference_units = pdf_text_blocks(pdf[page - 1])
            output_path = Path(record["output_path"])
            output_values = output_units(output_path.read_text(encoding="utf-8"), record.get("output_format", "markdown"))
            scored_records.append({"model": model, "method": method, "document": document, "page": page, "output_path": str(output_path), "metrics": score_page(reference_units, output_values)})
    result = {
        "experiment_id": root.name,
        "method": method,
        "n_values": list(N_VALUES),
        "definition": {
            "main_metric": "output_page_ngram_match_rate",
            "main_metric_definition": "各出力unitの非数値n-gramのうち、同じPDFページのいずれかのtext block内に存在する割合",
            "reference_metric_definition": "PDF text block内の非数値n-gramのうち、出力unitにも存在する割合",
            "text_box_boundary": "PDF get_text(blocks)の各block内だけでn-gramを生成し、block間を跨がない。出力側はMarkdownの行・表セル単位で生成する。",
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


def parse_model_log(value: str) -> tuple[str, Path]:
    """MODEL=PATH形式の引数を読む。"""
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
    print(json.dumps(run(args.root, dict(args.model_log), args.method, args.pdf_dir), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
