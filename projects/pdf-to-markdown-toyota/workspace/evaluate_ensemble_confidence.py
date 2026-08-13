#!/usr/bin/env python3
"""複数VLM出力の数値候補に、根拠付きconfidenceを付与する。"""

from __future__ import annotations

import argparse
import html
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

import fitz

from evaluate_outputs import markdown_table_shapes, numeric_tokens
from run_experiment import DOCUMENTS, page_text
from run_general_vlm import load_source_pdf_dir


WEIGHTS = {"model_agreement": 0.45, "pdf_evidence": 0.40, "structure": 0.15}


def read_log_argument(value: str) -> tuple[str, Path]:
    """`モデル名=ログpath` を安全に分解する。"""
    try:
        label, raw_path = value.split("=", maxsplit=1)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--model-log は MODEL=PATH の形式です") from exc
    if not label or not raw_path:
        raise argparse.ArgumentTypeError("--model-log は MODEL=PATH の形式です")
    return label, Path(raw_path)


def structural_validity(markdown: str) -> float:
    """表がある場合だけ列数の一貫性を確認し、ない場合は中立に扱う。"""
    shapes = markdown_table_shapes(markdown)
    if not shapes:
        return 1.0
    return 1.0 if all(shape[2] for shape in shapes) else 0.0


def confidence_label(value: float) -> str:
    if value >= 0.85:
        return "high"
    if value >= 0.65:
        return "medium"
    return "low"


def numeric_candidates(
    outputs: dict[str, str], reference_numbers: set[str]
) -> list[dict[str, Any]]:
    """数値tokenごとに、モデル支持とPDF text layerの根拠を集計する。"""
    models = sorted(outputs)
    tokens_by_model = {model: numeric_tokens(markdown) for model, markdown in outputs.items()}
    structures = {model: structural_validity(markdown) for model, markdown in outputs.items()}
    candidates = []
    for token in sorted(set().union(*tokens_by_model.values()), key=lambda value: (len(value), value)):
        supporting_models = [model for model in models if token in tokens_by_model[model]]
        agreement = len(supporting_models) / len(models)
        pdf_evidence = float(token in reference_numbers)
        structure = mean(structures[model] for model in supporting_models)
        score = (
            WEIGHTS["model_agreement"] * agreement
            + WEIGHTS["pdf_evidence"] * pdf_evidence
            + WEIGHTS["structure"] * structure
        )
        candidates.append(
            {
                "kind": "numeric_token",
                "value": token,
                "supporting_models": supporting_models,
                "model_agreement": round(agreement, 6),
                "pdf_text_evidence": bool(pdf_evidence),
                "structure_validity": round(structure, 6),
                "confidence": round(score, 6),
                "label": confidence_label(score),
            }
        )
    return candidates


def page_summary(candidates: list[dict[str, Any]], reference_numbers: set[str]) -> dict[str, Any]:
    """欠落を隠さないよう、平均confidenceとPDF数値被覆率を別々に算出する。"""
    present = {item["value"] for item in candidates}
    coverage = len(present & reference_numbers) / len(reference_numbers) if reference_numbers else None
    mean_confidence = mean(item["confidence"] for item in candidates) if candidates else 0.0
    combined = mean_confidence * coverage if coverage is not None else None
    counts = {label: sum(item["label"] == label for item in candidates) for label in ("high", "medium", "low")}
    return {
        "candidate_count": len(candidates),
        "pdf_numeric_token_count": len(reference_numbers),
        "pdf_numeric_coverage": round(coverage, 6) if coverage is not None else None,
        "mean_candidate_confidence": round(mean_confidence, 6),
        "coverage_adjusted_confidence": round(combined, 6) if combined is not None else None,
        "confidence_counts": counts,
    }


def page_review_html(document: str, page: int, models: list[str], summary: dict[str, Any], candidates: list[dict[str, Any]]) -> str:
    """最終変換物ではなく、人手確認用の数値candidate一覧をHTMLで出力する。"""
    rows = []
    for candidate in candidates:
        rows.append(
            "<tr>"
            f"<td>{html.escape(candidate['value'])}</td>"
            f"<td>{candidate['label']}</td>"
            f"<td>{candidate['confidence']:.3f}</td>"
            f"<td>{html.escape(', '.join(candidate['supporting_models']))}</td>"
            f"<td>{'yes' if candidate['pdf_text_evidence'] else 'no'}</td>"
            f"<td>{candidate['structure_validity']:.3f}</td>"
            "</tr>"
        )
    rows_html = "\n".join(rows)
    return f"""<!doctype html>
<html lang=\"ja\">
<head><meta charset=\"utf-8\"><title>Ensemble confidence review</title></head>
<body>
<h1>Ensemble confidence review</h1>
<p>document={html.escape(document)}, page={page}, models={html.escape(', '.join(models))}</p>
<p>PDF numeric coverage: {summary['pdf_numeric_coverage']}; coverage-adjusted confidence: {summary['coverage_adjusted_confidence']}</p>
<p>これは最終HTML変換結果ではなく、数値候補の人手確認用artifactです。</p>
<table>
<thead><tr><th>value</th><th>label</th><th>confidence</th><th>supporting models</th><th>PDF text evidence</th><th>structure validity</th></tr></thead>
<tbody>
{rows_html}
</tbody>
</table>
</body>
</html>
"""


def records_by_page(label: str, log_path: Path, method: str) -> dict[tuple[str, int], dict[str, Any]]:
    log = json.loads(log_path.read_text(encoding="utf-8"))
    records = {}
    for record in log.get("records", []):
        if record.get("status") != "success" or record.get("method") != method:
            continue
        output_path = Path(record["output_path"])
        if not output_path.is_file():
            raise FileNotFoundError(f"{label} の出力がありません: {output_path}")
        records[(str(record["document"]), int(record["page"]))] = record
    return records


def run(root: Path, model_logs: dict[str, Path], method: str, pdf_dir: Path | None) -> dict[str, Any]:
    root = root.resolve()
    pdf_dir = pdf_dir.resolve() if pdf_dir else load_source_pdf_dir(root)
    model_records = {label: records_by_page(label, path.resolve(), method) for label, path in model_logs.items()}
    models = sorted(model_records)
    shared_pages = set.intersection(*(set(records) for records in model_records.values()))
    results = []
    pdf_by_key = {spec.key: pdf_dir / spec.filename for spec in DOCUMENTS}
    for document, page in sorted(shared_pages):
        outputs = {
            model: Path(model_records[model][(document, page)]["output_path"]).read_text(encoding="utf-8")
            for model in models
        }
        with fitz.open(pdf_by_key[document]) as pdf:
            reference_numbers = numeric_tokens(page_text(pdf[page - 1]))
        candidates = numeric_candidates(outputs, reference_numbers)
        summary = page_summary(candidates, reference_numbers)
        review_path = root / "outputs" / "confidence-review" / method / document / f"page-{page:04d}.html"
        review_path.parent.mkdir(parents=True, exist_ok=True)
        review_path.write_text(page_review_html(document, page, models, summary, candidates), encoding="utf-8")
        results.append(
            {
                "document": document,
                "page": page,
                "models": models,
                "summary": summary,
                "candidates": candidates,
                "review_html": str(review_path),
            }
        )
    if not results:
        raise ValueError("全モデルで共通する成功ページがありません")
    aggregate = {
        "pages": len(results),
        "mean_pdf_numeric_coverage": round(mean(item["summary"]["pdf_numeric_coverage"] for item in results), 6),
        "mean_candidate_confidence": round(mean(item["summary"]["mean_candidate_confidence"] for item in results), 6),
        "mean_coverage_adjusted_confidence": round(mean(item["summary"]["coverage_adjusted_confidence"] for item in results), 6),
        "confidence_counts": {
            label: sum(item["summary"]["confidence_counts"][label] for item in results)
            for label in ("high", "medium", "low")
        },
    }
    payload = {
        "experiment_id": root.name,
        "method": method,
        "models": models,
        "model_logs": {label: str(path) for label, path in model_logs.items()},
        "weights": WEIGHTS,
        "definition": {
            "confidence": "0.45 * モデル支持率 + 0.40 * PDF text layerに同じ数値tokenがあるか + 0.15 * 支持モデルのMarkdown表列数一貫性",
            "coverage_adjusted_confidence": "候補平均confidence × PDF text layer数値token被覆率。欠落した数値を隠さないためのページ集約値。",
            "scope": "数値token単位。表のセル位置・列対応、画像化された図表の数値、意味的な本文一致は未評価。確率校正前のevidence scoreであり、正答確率ではない。",
        },
        "pages": results,
        "aggregate": aggregate,
    }
    result_path = root / "results" / "ensemble_confidence.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"result": str(result_path), "pages": len(results), "aggregate": aggregate}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--model-log", type=read_log_argument, action="append", required=True)
    parser.add_argument("--method", default="hybrid")
    parser.add_argument("--pdf-dir", type=Path, default=None)
    args = parser.parse_args()
    model_logs = dict(args.model_log)
    if len(model_logs) < 2:
        parser.error("少なくとも2モデルの--model-logが必要です")
    print(json.dumps(run(args.root, model_logs, args.method, args.pdf_dir), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
