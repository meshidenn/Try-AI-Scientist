#!/usr/bin/env python3
"""block-aware・数値除外n-gram評価をモデル別HTMLへ表示する。"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any, Iterable

import fitz

from pdf_to_markdown_toyota.interfaces.cli.evaluate_box_aware_page_ngrams import (
    N_VALUES,
    ngrams_from_units,
    numeric_free_segments,
    output_units,
    pdf_text_blocks,
    score_page,
)
from pdf_to_markdown_toyota.interfaces.cli.evaluate_outputs import NUMBER_PATTERN
from pdf_to_markdown_toyota.interfaces.cli.run_general_vlm import load_source_pdf_dir


def position_mask(text: str, n: int, accepted: set[str]) -> list[bool]:
    """1つの非数値segment内でaccepted n-gramが覆う位置を返す。"""
    mask = [False] * len(text)
    for index in range(len(text) - n + 1):
        if text[index : index + n] in accepted:
            for position in range(index, index + n):
                mask[position] = True
    return mask


def render_segment(text: str, mask: list[bool], true_class: str, false_class: str) -> str:
    """segmentの文字位置maskをHTML spanへ変換する。"""
    if not text:
        return ""
    parts: list[str] = []
    start = 0
    current = mask[0]
    for index in range(1, len(text) + 1):
        if index < len(text) and mask[index] == current:
            continue
        css_class = true_class if current else false_class
        parts.append(f'<span class="{css_class}">{html.escape(text[start:index])}</span>')
        if index < len(text):
            start = index
            current = mask[index]
    return "".join(parts)


def render_unit(unit: str, n: int, accepted: set[str], true_class: str, false_class: str) -> str:
    """数値tokenを除外表示し、非数値segmentだけを色付けする。"""
    normalized = "".join(numeric_free_segments(unit))
    # 数値を表示上も識別できるよう、元のunitをNFKC・空白除去してtoken単位に分ける。
    import re
    import unicodedata

    display = re.sub(r"\s+", "", unicodedata.normalize("NFKC", unit))
    pieces: list[str] = []
    cursor = 0
    for match in NUMBER_PATTERN.finditer(display):
        segment = display[cursor : match.start()]
        if segment:
            segment_mask = position_mask(segment, n, accepted)
            pieces.append(render_segment(segment, segment_mask, true_class, false_class))
        pieces.append(f'<span class="excluded-number" title="数字は評価対象外">{html.escape(match.group(0))}</span>')
        cursor = match.end()
    segment = display[cursor:]
    if segment:
        segment_mask = position_mask(segment, n, accepted)
        pieces.append(render_segment(segment, segment_mask, true_class, false_class))
    return "".join(pieces) if pieces else html.escape(normalized)


def render_units(units: list[str], n: int, accepted: set[str], true_class: str, false_class: str) -> str:
    """unit間にn-gramを作らず、表示上は区切りを付ける。"""
    return "".join(f'<span class="unit">{render_unit(unit, n, accepted, true_class, false_class)}</span>' for unit in units)


def missing_ngrams(reference_units: list[str], output_units_value: list[str], n: int) -> list[str]:
    """PDF blockにあり出力unitにないn-gramをPDF内のblock出現順で返す。"""
    reference = ngrams_from_units(reference_units, n)
    output = ngrams_from_units(output_units_value, n)
    missing = reference - output
    ordered: list[str] = []
    for unit in reference_units:
        for segment in numeric_free_segments(unit):
            for index in range(len(segment) - n + 1):
                value = segment[index : index + n]
                if value in missing and value not in ordered:
                    ordered.append(value)
    return ordered


def missing_list(values: Iterable[str]) -> str:
    """漏れn-gram一覧をHTML化する。"""
    values = list(values)
    return "<p>漏れはありません。</p>" if not values else "<ol>" + "".join(f"<li><code>{html.escape(value)}</code></li>" for value in values) + "</ol>"


def metric_table(scored: dict[str, Any]) -> str:
    rows = "".join(
        f"<tr><td>{item['n']}</td><td>{item['output_page_ngram_match_rate']:.6f}</td><td>{item['reference_page_ngram_coverage']:.6f}</td><td>{item['f1']:.6f}</td><td>{item['matched_ngram_count']}</td><td>{item['output_ngram_count']}</td><td>{item['reference_ngram_count']}</td></tr>"
        for item in scored["metrics"]
    )
    return "<table><thead><tr><th>n</th><th>out</th><th>cov</th><th>F1</th><th>一致</th><th>出力</th><th>PDF</th></tr></thead><tbody>" + rows + "</tbody></table>"


def panel(n: int, reference_units: list[str], output_units_value: list[str], scored: dict[str, Any]) -> str:
    reference_set = ngrams_from_units(reference_units, n)
    output_set = ngrams_from_units(output_units_value, n)
    matched = reference_set & output_set
    missing = missing_ngrams(reference_units, output_units_value, n)
    item = scored["metrics"][n - 1]
    return f"""
<section class="panel" id="n-{n}">
<h2>n={n}</h2>
<p>一致 {item['matched_ngram_count']} / 出力 {item['output_ngram_count']} / PDF {item['reference_ngram_count']} / 漏れ {len(missing)}</p>
{metric_table(scored)}
<div class="columns"><section><h3>モデル出力</h3><div class="text output">{render_units(output_units_value, n, matched, 'match', 'unmatched')}</div></section>
<section><h3>PDF text block（漏れ位置）</h3><div class="text reference">{render_units(reference_units, n, reference_set - output_set, 'missing', 'reference')}</div></section></div>
<details open><summary>漏れていた文字列（{len(missing)}件）</summary>{missing_list(missing)}</details>
</section>
"""


def page_html(model: str, document: str, page: int, markdown: str, reference_units: list[str], output_units_value: list[str], scored: dict[str, Any]) -> str:
    panels = "".join(panel(n, reference_units, output_units_value, scored) for n in N_VALUES)
    options = "".join(f'<option value="n-{n}"{(" selected" if n == 3 else "")}>n={n}</option>' for n in N_VALUES)
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><title>{html.escape(model)} - {html.escape(document)} p{page}</title>
<style>
body {{ font-family: system-ui, sans-serif; line-height: 1.55; margin: 1.5rem auto; max-width: 1600px; padding: 0 1rem; color: #172033; }}
select {{ font-size: 1rem; padding: .3rem; }} table {{ border-collapse: collapse; margin: .7rem 0; }} th,td {{ border:1px solid #cbd5e1; padding:.3rem .55rem; }} th {{ background:#f1f5f9; }}
.legend {{ display:flex; gap:.8rem; flex-wrap:wrap; margin:1rem 0; }} .legend span,.match,.unmatched,.missing,.excluded-number {{ padding:.08rem .15rem; border-radius:.15rem; }}
.match {{ background:#bbf7d0; }} .unmatched,.missing {{ background:#fecaca; }} .reference {{ background:#f8fafc; }} .excluded-number {{ background:#e2e8f0; color:#475569; }}
.columns {{ display:grid; grid-template-columns:1fr 1fr; gap:1rem; }} .text {{ white-space:pre-wrap; overflow-wrap:anywhere; border:1px solid #cbd5e1; padding:1rem; min-height:8rem; }}
.unit {{ display:block; border-bottom:1px dotted #cbd5e1; padding:.12rem 0; }} .panel {{ border-top:2px solid #94a3b8; padding-top:.8rem; }} details {{ max-height:24rem; overflow:auto; }}
@media (max-width:900px) {{ .columns {{ grid-template-columns:1fr; }} }}
</style></head><body>
<h1>Block-aware n-gram一致表示</h1>
<p>モデル: <strong>{html.escape(model)}</strong> / 資料: <strong>{html.escape(document)}</strong> / ページ: {page} / 方式: hybrid</p>
<p>表示n: <select id="n-select" onchange="showNgram(this.value)">{options}</select></p>
<div class="legend"><span class="match">緑: 同一PDF text block内に一致</span><span class="unmatched">赤: PDF block内に一致しない出力</span><span class="missing">赤: 出力にないPDF文字列</span><span class="excluded-number">灰: 数字（評価対象外）</span></div>
<p>PDFはtext block単位、出力はMarkdownの行・表セル単位で評価し、単位間を跨ぐn-gramは生成していません。数字tokenと数字を跨ぐn-gramも評価対象外です。</p>
<main>{panels}</main>
<details><summary>元のMarkdown出力</summary><pre>{html.escape(markdown)}</pre></details>
<script>function showNgram(id) {{ document.querySelectorAll('.panel').forEach(function(p) {{ p.style.display = p.id === id ? 'block' : 'none'; }}); }} showNgram('n-3');</script>
</body></html>"""


def run(root: Path) -> dict[str, Any]:
    """修正版page_ngrams.jsonからモデル別HTMLを生成する。"""
    root = root.resolve()
    result = json.loads((root / "results" / "page_ngrams.json").read_text(encoding="utf-8"))
    source_dir = load_source_pdf_dir(root)
    from pdf_to_markdown_toyota.domain.models import DOCUMENTS

    pdf_by_document = {spec.key: source_dir / spec.filename for spec in DOCUMENTS}
    artifacts: list[dict[str, Any]] = []
    for record in result["records"]:
        document, page, model = str(record["document"]), int(record["page"]), str(record["model"])
        source_markdown = Path(record["output_path"])
        markdown = source_markdown.read_text(encoding="utf-8")
        output_values = output_units(markdown, record.get("output_format", "markdown"))
        with fitz.open(pdf_by_document[document]) as pdf:
            reference_values = pdf_text_blocks(pdf[page - 1])
        scored = score_page(reference_values, output_values)
        output = root / "outputs" / "ngram-match-html" / model / document / f"page-{page:04d}.html"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(page_html(model, document, page, markdown, reference_values, output_values, scored), encoding="utf-8")
        artifacts.append({"model": model, "document": document, "page": page, "html": str(output), "source_markdown": str(source_markdown)})
    manifest = {"experiment_id": root.name, "method": result["method"], "n_values": list(N_VALUES), "html_count": len(artifacts), "definition": "PDF text blockと出力unit内の非数値n-gramを色付けし、PDF側にのみ存在するn-gramを一覧表示。灰色は評価対象外の数字token。", "artifacts": artifacts}
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
