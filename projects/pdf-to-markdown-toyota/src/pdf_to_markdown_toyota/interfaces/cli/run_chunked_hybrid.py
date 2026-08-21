#!/usr/bin/env python3
"""PDF座標でページを領域分割し、chunkごとにローカルVLMへ変換を依頼する。"""

from __future__ import annotations

import argparse
import json
import time
import urllib.request
from pathlib import Path
from typing import Any

import fitz

from pdf_to_markdown_toyota.domain.models import DOCUMENTS
from pdf_to_markdown_toyota.application.prompts import normalize_markdown
from pdf_to_markdown_toyota.infrastructure.pdf import block_records
from pdf_to_markdown_toyota.interfaces.cli.evaluate_outputs import numeric_tokens
from pdf_to_markdown_toyota.interfaces.cli.run_general_vlm import load_source_pdf_dir, require_local_base_url


def split_vertical_regions(
    blocks: list[dict[str, Any]], min_gap: float, min_text_chars: int
) -> list[list[dict[str, Any]]]:
    """縦方向の十分な空白で文字block群を分け、短いページ番号等は除外する。"""
    regions: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    bottom = 0.0
    for block in sorted(blocks, key=lambda item: (item["bbox"][1], item["bbox"][0])):
        top = float(block["bbox"][1])
        if current and top - bottom >= min_gap:
            regions.append(current)
            current = []
        current.append(block)
        bottom = max(bottom, float(block["bbox"][3]))
    if current:
        regions.append(current)
    return [region for region in regions if sum(len(item["text"]) for item in region) >= min_text_chars]


def region_bbox(region: list[dict[str, Any]], page: fitz.Page, margin: float = 8.0) -> list[float]:
    """領域の文字bboxに余白を足し、ページ範囲に収める。"""
    return [
        round(max(page.rect.x0, min(item["bbox"][0] for item in region) - margin), 2),
        round(max(page.rect.y0, min(item["bbox"][1] for item in region) - margin), 2),
        round(min(page.rect.x1, max(item["bbox"][2] for item in region) + margin), 2),
        round(min(page.rect.y1, max(item["bbox"][3] for item in region) + margin), 2),
    ]


def chunk_payload(page: fitz.Page, region: list[dict[str, Any]], bbox: list[float], index: int) -> str:
    payload = {
        "page_number": page.number + 1,
        "chunk_index": index,
        "chunk_bbox": bbox,
        "page_size": [round(page.rect.width, 2), round(page.rect.height, 2)],
        "blocks": region,
        "instruction": "この領域内の文字と座標だけを根拠にする。領域外の内容を補完しない。",
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def render_region(page: fitz.Page, bbox: list[float], output_path: Path, dpi: int = 300) -> None:
    scale = dpi / 72.0
    pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=fitz.Rect(bbox), alpha=False)
    pixmap.save(str(output_path))


def prompt(page_number: int, chunk_index: int, payload: str) -> str:
    return f"""あなたは企業PDFを忠実にMarkdown化する抽出器です。
添付画像はPDFの一部分であり、入力補助は同じ領域から抽出した文字block・座標です。
ページ番号: {page_number}、領域番号: {chunk_index}

出力規則:
- 出力はこの領域のMarkdown本文だけにする。コードフェンス、前置き、領域外の内容は出力しない。
- 表はMarkdown tableにし、列数を各行で揃える。表題、単位、注記を残す。
- 文字列、数値、符号、%は入力補助を正とし、変更・丸め・補完しない。
- 画像は表の行列、結合、読み順を判断するためにだけ使う。
- 判読できない箇所は`[判読不能]`と書く。

入力補助:
{payload}
"""


def request_completion(base_url: str, model: str, messages: list[dict[str, Any]], max_tokens: int) -> tuple[str, str | None, dict[str, Any] | None]:
    body = {
        "model": model,
        "messages": messages,
        "temperature": 0,
        "top_p": 1,
        "max_tokens": max_tokens,
    }
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": "Bearer EMPTY"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=3600) as response:
        result = json.loads(response.read().decode("utf-8"))
    choice = result["choices"][0]
    return choice["message"]["content"], choice.get("finish_reason"), result.get("usage")


def local_media_url(image_path: Path, root: Path) -> str:
    return f"file:///workspace/{image_path.relative_to(root).as_posix()}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--document", choices=tuple(spec.key for spec in DOCUMENTS), required=True)
    parser.add_argument("--page", type=int, required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:18028/v1")
    parser.add_argument("--model", default="gemma4-26b-moe")
    parser.add_argument("--max-new-tokens", type=int, default=4096)
    parser.add_argument("--min-gap", type=float, default=20.0)
    parser.add_argument("--min-text-chars", type=int, default=50)
    args = parser.parse_args()
    require_local_base_url(args.base_url)
    root = args.root.resolve()
    pdf_dir = load_source_pdf_dir(root)
    spec = next(item for item in DOCUMENTS if item.key == args.document)
    with fitz.open(pdf_dir / spec.filename) as document:
        page = document[args.page - 1]
        regions = split_vertical_regions(block_records(page), args.min_gap, args.min_text_chars)
        records: list[dict[str, Any]] = []
        for index, region in enumerate(regions, start=1):
            bbox = region_bbox(region, page)
            chunk_dir = root / "outputs" / args.document / f"page-{args.page:04d}" / f"chunk-{index:02d}"
            chunk_dir.mkdir(parents=True, exist_ok=True)
            image_path = chunk_dir / "region.png"
            payload_path = chunk_dir / "input.json"
            output_path = chunk_dir / "output.md"
            payload = chunk_payload(page, region, bbox, index)
            payload_path.write_text(payload + "\n", encoding="utf-8")
            render_region(page, bbox, image_path)
            record: dict[str, Any] = {
                "chunk_index": index,
                "chunk_bbox": bbox,
                "source_text_length": sum(len(item["text"]) for item in region),
                "reference_numeric_tokens": sorted(numeric_tokens("\n".join(item["text"] for item in region))),
                "input_path": str(payload_path),
                "image_path": str(image_path),
                "output_path": str(output_path),
                "status": "failed",
            }
            started = time.perf_counter()
            try:
                messages = [{"role": "user", "content": [
                    {"type": "text", "text": prompt(args.page, index, payload)},
                    {"type": "image_url", "image_url": {"url": local_media_url(image_path, root)}},
                ]}]
                output, finish_reason, usage = request_completion(args.base_url, args.model, messages, args.max_new_tokens)
                output_path.write_text(normalize_markdown(output), encoding="utf-8")
                output_numbers = numeric_tokens(output)
                reference_numbers = set(record["reference_numeric_tokens"])
                record.update({
                    "status": "success",
                    "finish_reason": finish_reason,
                    "usage": usage,
                    "output_characters": len(output),
                    "numeric_recall": round(len(output_numbers & reference_numbers) / len(reference_numbers), 6) if reference_numbers else None,
                    "output_numeric_token_count": len(output_numbers),
                    "matched_numeric_token_count": len(output_numbers & reference_numbers),
                })
            except Exception as exc:  # noqa: BLE001 - chunk単位の失敗を記録する
                record["reason"] = f"{type(exc).__name__}: {exc}"
            record["wall_time_seconds"] = round(time.perf_counter() - started, 6)
            records.append(record)

    all_reference = set().union(*(set(record["reference_numeric_tokens"]) for record in records))
    all_output = set()
    for record in records:
        if record["status"] == "success":
            all_output |= numeric_tokens(Path(record["output_path"]).read_text(encoding="utf-8"))
    result = {
        "experiment_id": root.name,
        "model": args.model,
        "method": "coordinate_chunked_hybrid",
        "document": args.document,
        "page": args.page,
        "max_new_tokens": args.max_new_tokens,
        "region_split": {"min_gap": args.min_gap, "min_text_chars": args.min_text_chars},
        "records": records,
        "page_numeric_recall": round(len(all_output & all_reference) / len(all_reference), 6) if all_reference else None,
        "page_reference_numeric_token_count": len(all_reference),
        "page_matched_numeric_token_count": len(all_output & all_reference),
    }
    log_path = root / "logs" / "chunked-hybrid-run.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    metrics_path = root / "results" / "chunk_metrics.json"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"log": str(log_path), "chunks": len(records), "page_numeric_recall": result["page_numeric_recall"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
