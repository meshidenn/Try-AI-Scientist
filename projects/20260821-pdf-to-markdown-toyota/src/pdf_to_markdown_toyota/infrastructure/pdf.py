"""PyMuPDFを使ったPDF入出力adapter。"""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any

import fitz

from pdf_to_markdown_toyota.domain.models import DOCUMENTS


def sha256(path: Path) -> str:
    """ファイルのSHA-256を計算する。"""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def block_records(page: fitz.Page) -> list[dict[str, Any]]:
    """PDF pageのtext blockを座標順の辞書へ変換する。"""
    records: list[dict[str, Any]] = []
    for raw in page.get_text("blocks"):
        x0, y0, x1, y1, text, block_no, block_type = raw[:7]
        cleaned = re.sub(r"\s+", " ", text).strip()
        if not cleaned:
            continue
        records.append(
            {
                "bbox": [round(float(value), 2) for value in (x0, y0, x1, y1)],
                "text": cleaned,
                "block_no": int(block_no),
                "block_type": int(block_type),
            }
        )
    records.sort(key=lambda item: (item["bbox"][1], item["bbox"][0]))
    return records


def page_text(page: fitz.Page) -> str:
    """PDF pageのtext layerをblock単位で連結する。"""
    return "\n".join(item["text"] for item in block_records(page))


def selection_score(page: fitz.Page) -> tuple[float, dict[str, Any]]:
    """pilot対象ページ選択用の簡易情報量scoreを計算する。"""
    records = block_records(page)
    text = "\n".join(item["text"] for item in records)
    digit_count = sum(char.isdigit() for char in text)
    short_blocks = sum(len(item["text"]) <= 80 for item in records)
    return float(digit_count + 2 * short_blocks + len(records)), {
        "block_count": len(records),
        "digit_count": digit_count,
        "text_length": len(text),
    }


def select_pages(document: fitz.Document, max_pages: int) -> list[int]:
    """情報量scoreの高いページを先頭ページ込みで選択する。"""
    if len(document) == 0:
        return []
    candidates = list(range(len(document)))
    scored = [(selection_score(document[index])[0], index) for index in candidates]
    selected = {0}
    for _, index in sorted(scored, reverse=True):
        selected.add(index)
        if len(selected) >= max_pages:
            break
    return sorted(selected)[:max_pages]


def parse_first_payload(page: fitz.Page) -> str:
    """parse-first方式でVLMへ渡すページpayloadを作る。"""
    payload = {
        "page_number": page.number + 1,
        "page_size": [round(page.rect.width, 2), round(page.rect.height, 2)],
        "blocks": block_records(page),
        "instruction": "PDFの文字と座標だけを根拠に、推測や補完をせずMarkdownへ変換する。",
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def render_page(page: fitz.Page, image_path: Path, dpi: int = 300) -> None:
    """PDF pageを画像へrenderする。"""
    scale = dpi / 72.0
    pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    pixmap.save(str(image_path))


def write_json(path: Path, payload: Any) -> None:
    """JSON artifactを親directory作成込みで保存する。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepare_documents(pdf_dir: Path, metadata_path: Path) -> dict[str, Any]:
    """入力PDFの存在、hash、ページ数をmetadataへ記録する。"""
    metadata: dict[str, Any] = {"generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "documents": {}}
    for spec in DOCUMENTS:
        path = pdf_dir / spec.filename
        if not path.exists():
            metadata["documents"][spec.key] = {"status": "not_found", "url": spec.url}
            continue
        with fitz.open(path) as document:
            metadata["documents"][spec.key] = {
                "status": "ready",
                "label": spec.label,
                "url": spec.url,
                "path": str(path),
                "sha256": sha256(path),
                "page_count": len(document),
                "selected_pages": [index + 1 for index in select_pages(document, 3)],
            }
    write_json(metadata_path, metadata)
    return metadata
