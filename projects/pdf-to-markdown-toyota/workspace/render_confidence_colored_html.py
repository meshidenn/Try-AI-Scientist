#!/usr/bin/env python3
"""アンサンブル根拠を各モデルの実出力HTMLへ重ねて表示する。"""
from __future__ import annotations

import argparse
import html
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

from evaluate_ensemble_text_confidence import clean, similar, textual
from evaluate_outputs import NUMBER_PATTERN, normalize_text


LABELS = ("high", "medium", "low")
MODEL_ORDER = ("gemma4-26b-moe", "qwen3.6-27b", "glm-4.6v-flash")


def normalize_number(value: str) -> str:
    return unicodedata.normalize("NFKC", value).replace(",", "")


def number_labels(candidates: list[dict[str, Any]], model: str) -> dict[str, str]:
    """そのモデル自身が出力した数値だけを着色対象にする。"""
    return {
        normalize_number(str(item["value"])): str(item["label"])
        for item in candidates
        if model in item["supporting_models"]
    }


def text_label(value: str, kind: str, candidates: list[dict[str, Any]], model: str) -> str | None:
    """実出力unitに対応するテキスト候補の信頼ラベルを返す。"""
    value = clean(value)
    normalized = normalize_text(value)
    if not textual(value):
        return None
    matched = [
        item for item in candidates
        if item["kind"] == kind
        and model in item["supporting_models"]
        and similar(normalized, normalize_text(str(item["value"])))
    ]
    if not matched:
        return None
    return max(matched, key=lambda item: len(str(item["value"]))) ["label"]


def render_inline(value: str, numeric_labels: dict[str, str]) -> str:
    """文字列をエスケープし、数値tokenだけを信頼ラベルで囲む。"""
    parts: list[str] = []
    position = 0
    for match in NUMBER_PATTERN.finditer(value):
        parts.append(html.escape(value[position:match.start()]))
        token = match.group(0)
        label = numeric_labels.get(normalize_number(token))
        escaped = html.escape(token)
        parts.append(
            f'<span class="confidence-{label}" title="numeric evidence: {label}">{escaped}</span>'
            if label else escaped
        )
        position = match.end()
    parts.append(html.escape(value[position:]))
    return "".join(parts)


def wrap_text(value: str, kind: str, text_candidates: list[dict[str, Any]], model: str, numeric_labels: dict[str, str]) -> str:
    rendered = render_inline(value, numeric_labels)
    label = text_label(value, kind, text_candidates, model)
    if label:
        return f'<span class="confidence-{label} text-evidence" title="text evidence: {label}">{rendered}</span>'
    return rendered


def is_table_row(line: str) -> bool:
    line = line.strip()
    return line.startswith("|") and line.endswith("|")


def is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def split_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def render_table(lines: list[str], text_candidates: list[dict[str, Any]], model: str, numeric_labels: dict[str, str]) -> str:
    rows = [split_cells(line) for line in lines]
    header = rows[0]
    body = rows[2:] if len(rows) > 1 and is_separator(rows[1]) else rows[1:]

    def cells(values: list[str], tag: str) -> str:
        return "".join(
            f"<{tag}>{wrap_text(value, 'table_cell_text', text_candidates, model, numeric_labels)}</{tag}>"
            for value in values
        )

    head = f"<thead><tr>{cells(header, 'th')}</tr></thead>"
    rows_html = "".join(f"<tr>{cells(row, 'td')}</tr>" for row in body)
    return f"<table>{head}<tbody>{rows_html}</tbody></table>"


def render_markdown(markdown: str, text_candidates: list[dict[str, Any]], model: str, numeric_labels: dict[str, str]) -> str:
    """対象出力で使う見出し・箇条書き・Markdown表を安全なHTMLへ変換する。"""
    lines = markdown.splitlines()
    output: list[str] = []
    index = 0
    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        if not stripped:
            index += 1
            continue
        if is_table_row(stripped):
            table_lines = []
            while index < len(lines) and is_table_row(lines[index].strip()):
                table_lines.append(lines[index])
                index += 1
            output.append(render_table(table_lines, text_candidates, model, numeric_labels))
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            level, value = len(heading.group(1)), heading.group(2)
            output.append(f"<h{level}>{wrap_text(value, 'text_line', text_candidates, model, numeric_labels)}</h{level}>")
            index += 1
            continue
        if re.match(r"^[-*+]\s+", stripped):
            items = []
            while index < len(lines) and (matched := re.match(r"^\s*[-*+]\s+(.+)$", lines[index])):
                items.append(f"<li>{wrap_text(matched.group(1), 'text_line', text_candidates, model, numeric_labels)}</li>")
                index += 1
            output.append("<ul>" + "".join(items) + "</ul>")
            continue
        output.append(f"<p>{wrap_text(stripped, 'text_line', text_candidates, model, numeric_labels)}</p>")
        index += 1
    return "\n".join(output)


def page_html(document: str, page: int, model: str, markdown: str, text_candidates: list[dict[str, Any]], numeric_labels: dict[str, str]) -> str:
    body = render_markdown(markdown, text_candidates, model, numeric_labels)
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><title>{html.escape(model)} — {html.escape(document)} p{page}</title>
<style>
body {{ font-family: system-ui, sans-serif; line-height: 1.65; margin: 2rem auto; max-width: 1100px; padding: 0 1rem; }}
table {{ border-collapse: collapse; display: block; max-width: 100%; overflow-x: auto; margin: 1rem 0; }}
th, td {{ border: 1px solid #cbd5e1; padding: .38rem .55rem; vertical-align: top; white-space: pre-wrap; }} th {{ background: #f1f5f9; }}
.legend {{ display: flex; gap: .8rem; flex-wrap: wrap; padding: .6rem; border: 1px solid #cbd5e1; border-radius: .4rem; }}
.confidence-high {{ background: #bbf7d0; }} .confidence-medium {{ background: #fef08a; }} .confidence-low {{ background: #fecaca; }}
.text-evidence {{ box-decoration-break: clone; -webkit-box-decoration-break: clone; }}
details {{ margin-top: 2rem; }} pre {{ white-space: pre-wrap; background: #f8fafc; padding: 1rem; overflow-x: auto; }}
</style></head><body>
<h1>実出力（{html.escape(model)}）</h1>
<p>資料: {html.escape(document)} / ページ: {page} / 方式: hybrid。本文と表はこのモデルの元のMarkdown出力をHTML表示したものです。</p>
<div class="legend"><span class="confidence-high">High: 3モデル一致または強いPDF根拠</span><span class="confidence-medium">Medium: 部分的な根拠</span><span class="confidence-low">Low: 一致またはPDF文字列根拠が弱い</span></div>
<main>{body}</main>
<details><summary>元のMarkdownを表示</summary><pre>{html.escape(markdown)}</pre></details>
</body></html>
"""


def load_records(log_path: Path, method: str) -> dict[tuple[str, int], dict[str, Any]]:
    return {
        (str(item["document"]), int(item["page"])): item
        for item in json.loads(log_path.read_text(encoding="utf-8"))["records"]
        if item.get("status") == "success" and item.get("method") == method
    }


def run(root: Path, method: str = "hybrid") -> dict[str, Any]:
    root = root.resolve()
    numeric = json.loads((root / "results" / "ensemble_confidence.json").read_text(encoding="utf-8"))
    text = json.loads((root / "results" / "ensemble_text_confidence.json").read_text(encoding="utf-8"))
    model_logs = {name: Path(path) for name, path in numeric["model_logs"].items()}
    by_model = {model: load_records(path, method) for model, path in model_logs.items()}
    numeric_pages = {(item["document"], item["page"]): item for item in numeric["pages"]}
    text_pages = {(item["document"], item["page"]): item for item in text["pages"]}
    shared = set(numeric_pages) & set(text_pages) & set.intersection(*(set(records) for records in by_model.values()))
    artifacts = []
    for document, page in sorted(shared):
        for model in MODEL_ORDER:
            record = by_model[model][(document, page)]
            markdown = Path(record["output_path"]).read_text(encoding="utf-8")
            labels = number_labels(numeric_pages[(document, page)]["candidates"], model)
            text_candidates = text_pages[(document, page)]["candidates"]
            output = root / "outputs" / "colorized-model-output" / model / method / document / f"page-{page:04d}.html"
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(page_html(document, page, model, markdown, text_candidates, labels), encoding="utf-8")
            artifacts.append({"document": document, "page": page, "model": model, "source_markdown": record["output_path"], "html": str(output)})
    payload = {"experiment_id": root.name, "method": method, "models": list(MODEL_ORDER), "definition": "各モデル自身の元MarkdownをHTML表示し、exp-008の数値・テキストevidence scoreを重ねて着色。候補一覧ではない。", "artifacts": artifacts}
    manifest = root / "results" / "colorized_html_manifest.json"
    manifest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"result": str(manifest), "html_count": len(artifacts)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--method", default="hybrid")
    args = parser.parse_args()
    print(json.dumps(run(args.root, args.method), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
