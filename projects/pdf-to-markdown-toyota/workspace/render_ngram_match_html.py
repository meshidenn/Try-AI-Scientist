#!/usr/bin/env python3
"""ページ内文字n-gramの一致箇所と漏れ文字列をHTML表示する。"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any, Iterable

import fitz

from evaluate_page_ngrams import character_ngrams, normalize_for_ngrams, score_page
from run_experiment import page_text
from run_general_vlm import load_source_pdf_dir


N_VALUES = tuple(range(1, 11))


def matched_position_mask(text: str, n: int, accepted: set[str]) -> list[bool]:
    """acceptedに含まれるn-gramが覆う文字位置を返す。"""
    mask = [False] * len(text)
    for index in range(len(text) - n + 1):
        if text[index : index + n] not in accepted:
            continue
        for position in range(index, index + n):
            mask[position] = True
    return mask


def missing_ngrams(reference: str, output: str, n: int) -> list[str]:
    """PDF側にあり出力側にないn-gramをPDF内の出現順で返す。"""
    output_set = character_ngrams(output, n)
    reference_set = character_ngrams(reference, n)
    missing = reference_set - output_set
    return sorted(missing, key=lambda value: (reference.find(value), value))


def render_masked_text(text: str, mask: list[bool], true_class: str, false_class: str) -> str:
    """文字位置maskを連続spanへまとめてHTML化する。"""
    if not text:
        return "<em>(空)</em>"
    chunks: list[str] = []
    start = 0
    current = mask[0]
    for index in range(1, len(text) + 1):
        if index < len(text) and mask[index] == current:
            continue
        value = html.escape(text[start:index])
        css_class = true_class if current else false_class
        chunks.append(f'<span class="{css_class}">{value}</span>')
        if index < len(text):
            start = index
            current = mask[index]
    return "".join(chunks)


def metric_rows(scored: dict[str, Any]) -> str:
    """nごとのmetric表を作る。"""
    rows = []
    for item in scored["metrics"]:
        rows.append(
            "<tr>"
            f"<td>{item['n']}</td>"
            f"<td>{item['output_page_ngram_match_rate']:.6f}</td>"
            f"<td>{item['reference_page_ngram_coverage']:.6f}</td>"
            f"<td>{item['f1']:.6f}</td>"
            f"<td>{item['matched_ngram_count']}</td>"
            f"<td>{item['output_ngram_count']}</td>"
            f"<td>{item['reference_ngram_count']}</td>"
            "</tr>"
        )
    return "".join(rows)


def missing_list(values: Iterable[str]) -> str:
    """漏れn-gram一覧を安全なHTMLのcode要素へ変換する。"""
    values = list(values)
    if not values:
        return "<p>漏れはありません。</p>"
    return "<ol>" + "".join(f"<li><code>{html.escape(value)}</code></li>" for value in values) + "</ol>"


def ngram_panel(n: int, reference: str, output: str, scored: dict[str, Any]) -> str:
    """指定nの一致表示、漏れ一覧、metricを含むHTMLパネルを作る。"""
    reference_set = character_ngrams(reference, n)
    output_set = character_ngrams(output, n)
    matched = reference_set & output_set
    output_mask = matched_position_mask(output, n, matched)
    missing_mask = matched_position_mask(reference, n, reference_set - output_set)
    metric = scored["metrics"][n - 1]
    missing = missing_ngrams(reference, output, n)
    return f"""
<section class="ngram-panel" id="n-{n}">
<h2>n={n}</h2>
<p>一致n-gram: {metric['matched_ngram_count']} / 出力n-gram: {metric['output_ngram_count']} / PDF n-gram: {metric['reference_ngram_count']} / 漏れ: {len(missing)}</p>
<table class="metrics"><thead><tr><th>out</th><th>cov</th><th>F1</th></tr></thead><tbody><tr><td>{metric['output_page_ngram_match_rate']:.6f}</td><td>{metric['reference_page_ngram_coverage']:.6f}</td><td>{metric['f1']:.6f}</td></tr></tbody></table>
<div class="columns">
<section><h3>モデル出力（正規化後）</h3><p class="text-output">{render_masked_text(output, output_mask, 'match', 'unmatched')}</p></section>
<section><h3>PDF text layer（漏れ位置）</h3><p class="text-reference">{render_masked_text(reference, missing_mask, 'missing', 'reference')}</p></section>
</div>
<details class="missing-list" open><summary>漏れていた文字列（{len(missing)}件）</summary>{missing_list(missing)}</details>
</section>
"""


def page_html(model: str, document: str, page: int, markdown: str, reference: str, scored: dict[str, Any]) -> str:
    """モデル・資料・ページ単位のHTMLを作る。"""
    output = normalize_for_ngrams(markdown, "markdown")
    reference = normalize_for_ngrams(reference)
    panels = "".join(ngram_panel(n, reference, output, scored) for n in N_VALUES)
    options = "".join(f'<option value="n-{n}"{(" selected" if n == 3 else "")}>n={n}</option>' for n in N_VALUES)
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><title>{html.escape(model)} - {html.escape(document)} p{page} n-gram</title>
<style>
body {{ font-family: system-ui, sans-serif; line-height: 1.55; margin: 1.5rem auto; max-width: 1500px; padding: 0 1rem; color: #172033; }}
select {{ font-size: 1rem; padding: .3rem; }}
table {{ border-collapse: collapse; margin: .7rem 0; }} th, td {{ border: 1px solid #cbd5e1; padding: .3rem .55rem; }} th {{ background: #f1f5f9; }}
.legend {{ display: flex; gap: .8rem; flex-wrap: wrap; margin: 1rem 0; }}
.legend span, .match, .unmatched, .missing {{ padding: .08rem .15rem; border-radius: .15rem; }}
.match {{ background: #bbf7d0; }} .unmatched, .missing {{ background: #fecaca; }} .reference {{ background: #f8fafc; }}
.columns {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }}
.text-output, .text-reference {{ white-space: pre-wrap; overflow-wrap: anywhere; border: 1px solid #cbd5e1; padding: 1rem; min-height: 8rem; background: #fff; }}
.text-reference {{ background: #f8fafc; }} .missing-list {{ margin: 1rem 0; max-height: 24rem; overflow: auto; }}
.ngram-panel {{ border-top: 2px solid #94a3b8; padding-top: .8rem; }}
@media (max-width: 900px) {{ .columns {{ grid-template-columns: 1fr; }} }}
</style></head><body>
<h1>ページ内n-gram一致表示</h1>
<p>モデル: <strong>{html.escape(model)}</strong> / 資料: <strong>{html.escape(document)}</strong> / ページ: {page} / 方式: hybrid</p>
<p>表示nを選択: <select id="n-select" onchange="showNgram(this.value)">{options}</select></p>
<div class="legend"><span class="match">緑: 出力n-gramがPDFページ内に存在</span><span class="unmatched">赤: 出力n-gramがPDFページ内に存在しない</span><span class="missing">赤: PDF側にあり出力にないn-gram</span></div>
<p>表示テキストは比較用にNFKC、空白除去、Markdown構文除去を適用しています。元Markdownは下部にあります。</p>
<main>{panels}</main>
<details><summary>元のMarkdown出力</summary><pre>{html.escape(markdown)}</pre></details>
<script>
function showNgram(id) {{ document.querySelectorAll('.ngram-panel').forEach(function(panel) {{ panel.style.display = panel.id === id ? 'block' : 'none'; }}); }}
showNgram('n-3');
</script></body></html>
"""


def run(root: Path) -> dict[str, Any]:
    """page_ngrams.jsonの全model-page recordからHTMLを生成する。"""
    root = root.resolve()
    result = json.loads((root / "results" / "page_ngrams.json").read_text(encoding="utf-8"))
    source_dir = load_source_pdf_dir(root)
    pdf_by_document = {item["document"]: source_dir / item["filename"] for item in json.loads((root / "inputs" / "source-manifest.json").read_text(encoding="utf-8")).get("documents", []) if isinstance(item, dict)}
    # source-manifestのdocumentsは既存artifactではファイル名配列なので、PDF specから解決する。
    if not pdf_by_document:
        from run_experiment import DOCUMENTS

        pdf_by_document = {spec.key: source_dir / spec.filename for spec in DOCUMENTS}
    artifacts: list[dict[str, Any]] = []
    for record in result["records"]:
        document = str(record["document"])
        page = int(record["page"])
        model = str(record["model"])
        output_path = Path(record["output_path"])
        markdown = output_path.read_text(encoding="utf-8")
        with fitz.open(pdf_by_document[document]) as pdf:
            reference = page_text(pdf[page - 1])
        scored = score_page(reference, markdown, record.get("output_format", "markdown"))
        output_path = root / "outputs" / "ngram-match-html" / model / document / f"page-{page:04d}.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(page_html(model, document, page, markdown, reference, scored), encoding="utf-8")
        artifacts.append({"model": model, "document": document, "page": page, "html": str(output_path), "source_markdown": str(record["output_path"])})
    manifest = {"experiment_id": root.name, "method": result["method"], "n_values": list(N_VALUES), "html_count": len(artifacts), "definition": "緑は出力n-gramが同一PDFページに存在する位置、赤は出力側の不一致位置とPDF側の漏れn-gram位置。漏れn-gramは各nの一覧にも掲載。", "artifacts": artifacts}
    manifest_path = root / "results" / "ngram_html_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"result": str(manifest_path), "html_count": len(artifacts)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.root), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
