#!/usr/bin/env python3
"""3モデルのMarkdownからテキスト候補のevidence scoreを計算する。"""
from __future__ import annotations
import argparse
import html
import json
import re
from difflib import SequenceMatcher
from pathlib import Path
from statistics import mean
from typing import Any
import fitz
from pdf_to_markdown_toyota.interfaces.cli.evaluate_outputs import normalize_text
from pdf_to_markdown_toyota.domain.models import DOCUMENTS
from pdf_to_markdown_toyota.infrastructure.pdf import page_text
from pdf_to_markdown_toyota.interfaces.cli.run_general_vlm import load_source_pdf_dir

WEIGHTS = {"model_agreement": 0.55, "pdf_evidence": 0.45}

def read_log(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("--model-log は MODEL=PATH の形式です")
    label, path = value.split("=", 1)
    return label, Path(path)

def label(score: float) -> str:
    return "high" if score >= .85 else "medium" if score >= .65 else "low"

def clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"^\s{0,3}(?:#{1,6}\s+|[-*+]\s+|\d+[.)]\s+)", "", text)
    return re.sub(r"\s+", " ", text.replace("**", "").replace("__", "").replace("`", "")).strip()

def textual(text: str) -> bool:
    norm = normalize_text(text)
    return len(norm) >= 4 and not bool(re.fullmatch(r"[|:－—\-\s]+", text)) and bool(re.search(r"[^0-9０-９.,%％+\-－△▲▼()（）\[\]【】/:：\s]", norm))

def units(markdown: str) -> list[dict[str, str]]:
    result, seen = [], set()
    for line in markdown.splitlines():
        line = line.strip()
        if not line:
            continue
        values = [("table_cell_text", clean(cell)) for cell in line.strip("|").split("|")] if line.startswith("|") and line.endswith("|") else [("text_line", clean(line))]
        for kind, value in values:
            key = (kind, normalize_text(value))
            if textual(value) and key not in seen:
                seen.add(key)
                result.append({"kind": kind, "value": value, "normalized": key[1]})
    return result

def similar(left: str, right: str) -> bool:
    if left == right:
        return True
    short, long = sorted((left, right), key=len)
    return (len(short) >= 8 and short in long) or SequenceMatcher(None, left, right).ratio() >= .88

def text_candidates(outputs: dict[str, str], reference: str) -> list[dict[str, Any]]:
    clusters: list[dict[str, Any]] = []
    models = sorted(outputs)
    for model in models:
        for unit in units(outputs[model]):
            cluster = next((item for item in clusters if item["kind"] == unit["kind"] and model not in item["units"] and similar(item["normalized"], unit["normalized"])), None)
            if cluster is None:
                clusters.append({"kind": unit["kind"], "normalized": unit["normalized"], "units": {model: unit}})
            else:
                cluster["units"][model] = unit
    ref = normalize_text(reference)
    result = []
    for cluster in clusters:
        support = sorted(cluster["units"])
        value = max((unit["value"] for unit in cluster["units"].values()), key=len)
        agreement = len(support) / len(models)
        evidence = cluster["normalized"] in ref
        score = WEIGHTS["model_agreement"] * agreement + WEIGHTS["pdf_evidence"] * float(evidence)
        result.append({"kind": cluster["kind"], "value": value, "supporting_models": support, "model_agreement": round(agreement, 6), "pdf_text_evidence": evidence, "confidence": round(score, 6), "label": label(score)})
    return result

def summarize(candidates: list[dict[str, Any]], reference: str) -> dict[str, Any]:
    ref_units = [item for item in units(reference) if item["kind"] == "text_line"]
    generated = [normalize_text(item["value"]) for item in candidates]
    coverage = sum(any(similar(item["normalized"], value) for value in generated) for item in ref_units) / len(ref_units) if ref_units else None
    avg = mean(item["confidence"] for item in candidates) if candidates else 0.0
    return {"candidate_count": len(candidates), "pdf_text_unit_count": len(ref_units), "pdf_text_unit_coverage_proxy": round(coverage, 6) if coverage is not None else None, "mean_candidate_confidence": round(avg, 6), "coverage_adjusted_confidence": round(avg * coverage, 6) if coverage is not None else None, "confidence_counts": {name: sum(item["label"] == name for item in candidates) for name in ("high", "medium", "low")}}

def records(log_path: Path, method: str) -> dict[tuple[str, int], dict[str, Any]]:
    result = {}
    for item in json.loads(log_path.read_text(encoding="utf-8")).get("records", []):
        if item.get("status") == "success" and item.get("method") == method:
            path = Path(item["output_path"])
            if not path.is_file():
                raise FileNotFoundError(path)
            result[(str(item["document"]), int(item["page"]))] = item
    return result

def review(document: str, page: int, models: list[str], summary: dict[str, Any], candidates: list[dict[str, Any]]) -> str:
    rows = "".join(f"<tr><td>{html.escape(item['kind'])}</td><td>{html.escape(item['value'])}</td><td>{item['label']}</td><td>{item['confidence']:.3f}</td><td>{html.escape(', '.join(item['supporting_models']))}</td><td>{'yes' if item['pdf_text_evidence'] else 'no'}</td></tr>" for item in candidates)
    return f"<!doctype html><html lang='ja'><head><meta charset='utf-8'><title>Text ensemble confidence</title></head><body><h1>Text ensemble confidence review</h1><p>document={html.escape(document)}, page={page}, models={html.escape(', '.join(models))}</p><p>PDF text-unit coverage proxy: {summary['pdf_text_unit_coverage_proxy']}; coverage-adjusted confidence: {summary['coverage_adjusted_confidence']}</p><table><thead><tr><th>kind</th><th>value</th><th>label</th><th>confidence</th><th>supporting models</th><th>PDF text evidence</th></tr></thead><tbody>{rows}</tbody></table></body></html>\n"

def run(root: Path, logs: dict[str, Path], method: str, pdf_dir: Path | None) -> dict[str, Any]:
    root = root.resolve()
    source = pdf_dir.resolve() if pdf_dir else load_source_pdf_dir(root)
    by_model = {name: records(path.resolve(), method) for name, path in logs.items()}
    models = sorted(by_model)
    shared = set.intersection(*(set(value) for value in by_model.values()))
    paths = {spec.key: source / spec.filename for spec in DOCUMENTS}
    pages = []
    for document, page in sorted(shared):
        outputs = {model: Path(by_model[model][(document, page)]["output_path"]).read_text(encoding="utf-8") for model in models}
        with fitz.open(paths[document]) as pdf:
            reference = page_text(pdf[page - 1])
        candidates = text_candidates(outputs, reference)
        page_summary = summarize(candidates, reference)
        html_path = root / "outputs" / "text-confidence-review" / method / document / f"page-{page:04d}.html"
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(review(document, page, models, page_summary, candidates), encoding="utf-8")
        pages.append({"document": document, "page": page, "models": models, "summary": page_summary, "candidates": candidates, "review_html": str(html_path)})
    if not pages:
        raise ValueError("全モデルで共通する成功ページがありません")
    aggregate = {"pages": len(pages), "mean_pdf_text_unit_coverage_proxy": round(mean(item["summary"]["pdf_text_unit_coverage_proxy"] for item in pages if item["summary"]["pdf_text_unit_coverage_proxy"] is not None), 6), "mean_candidate_confidence": round(mean(item["summary"]["mean_candidate_confidence"] for item in pages), 6), "mean_coverage_adjusted_confidence": round(mean(item["summary"]["coverage_adjusted_confidence"] for item in pages if item["summary"]["coverage_adjusted_confidence"] is not None), 6), "confidence_counts": {name: sum(item["summary"]["confidence_counts"][name] for item in pages) for name in ("high", "medium", "low")}}
    payload = {"experiment_id": root.name, "method": method, "models": models, "model_logs": {name: str(path) for name, path in logs.items()}, "weights": WEIGHTS, "definition": {"confidence": "0.55 * モデル支持率 + 0.45 * PDF text layerでの正規化文字列包含", "coverage": "PDF text block相当のtext unitに対する近似被覆率。意味的同義、図中文字、表セル位置を評価しない。", "scope": "本文行・見出し・Markdown表内の非数値セル。未校正のevidence scoreであり、正答確率ではない。"}, "pages": pages, "aggregate": aggregate}
    path = root / "results" / "ensemble_text_confidence.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"result": str(path), "pages": len(pages), "aggregate": aggregate}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--model-log", type=read_log, action="append", required=True)
    parser.add_argument("--method", default="hybrid")
    parser.add_argument("--pdf-dir", type=Path, default=None)
    args = parser.parse_args()
    model_logs = dict(args.model_log)
    if len(model_logs) < 2:
        parser.error("少なくとも2モデルの--model-logが必要です")
    print(json.dumps(run(args.root, model_logs, args.method, args.pdf_dir), ensure_ascii=False))

if __name__ == "__main__":
    main()
