#!/usr/bin/env python3
"""Toyota PDFのParse-first/Image-first比較実験。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import fitz


MODEL_NAME = "gemma4-26b-moe"
MODEL_ID = "google/gemma-4-26B-A4B-it"


@dataclass(frozen=True)
class DocumentSpec:
    key: str
    label: str
    filename: str
    url: str


DOCUMENTS = (
    DocumentSpec(
        "securities_report",
        "有価証券報告書",
        "securities-report-2026.pdf",
        "https://global.toyota/pages/global_toyota/ir/library/securities-report/archives/archives_2026_03.pdf",
    ),
    DocumentSpec(
        "earnings_presentation",
        "決算説明会資料",
        "earnings-presentation-2026.pdf",
        "https://global.toyota/pages/global_toyota/ir/financial-results/2026_4q_presentation_jp.pdf",
    ),
    DocumentSpec(
        "integrated_report",
        "統合報告書",
        "integrated-report-2025.pdf",
        "https://global.toyota/pages/global_toyota/ir/library/annual/2025_001_integrated_jp.pdf",
    ),
    DocumentSpec(
        "midterm_policy",
        "中期経営計画書相当資料（2030年電動化戦略）",
        "midterm-policy-2030-electrification.pdf",
        "https://global.toyota/en/filedownload/20399572",
    ),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def block_records(page: fitz.Page) -> list[dict[str, Any]]:
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
    return "\n".join(item["text"] for item in block_records(page))


def selection_score(page: fitz.Page) -> tuple[float, dict[str, Any]]:
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
    payload = {
        "page_number": page.number + 1,
        "page_size": [round(page.rect.width, 2), round(page.rect.height, 2)],
        "blocks": block_records(page),
        "instruction": "PDFの文字と座標だけを根拠に、推測や補完をせずMarkdownへ変換する。",
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def render_page(page: fitz.Page, image_path: Path, dpi: int = 300) -> None:
    scale = dpi / 72.0
    pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    pixmap.save(str(image_path))


def prompt(method: str, page_number: int, content_hint: str) -> str:
    if method == "parse_first":
        source = "以下はPDFから抽出した文字block、座標、ページ番号です。"
    else:
        source = "添付画像はPDFの1ページです。画像に見える内容だけを読み取ってください。"
    return f"""あなたは企業PDFを忠実にMarkdown化する抽出器です。
{source}
ページ番号: {page_number}
出力規則:
- 出力はMarkdown本文だけにする。コードフェンスは使わない。
- 見出し、段落、箇条書き、表、脚注の順序を可能な限り保つ。
- 表はMarkdown tableにし、列数を各行で揃える。単位と注記も残す。
- 数字、符号、%などを変更・丸め・推測しない。
- 判読できない箇所は空欄にせず`[判読不能]`と書く。
- ページをまたぐ補完はせず、このページの内容だけを出力する。

入力補助:
{content_hint}
"""


def html_prompt(method: str, page_number: int, content_hint: str) -> str:
    if method == "parse_first":
        source = "以下はPDFから抽出した文字block、座標、ページ番号です。"
    else:
        source = "添付画像はPDFの1ページです。画像に見える内容だけを読み取ってください。"
    return f"""あなたは企業PDFを忠実にHTML化する抽出器です。
{source}
ページ番号: {page_number}
出力規則:
- 出力はHTML fragmentだけにする。コードフェンス、Markdown、html要素、body要素は使わない。
- 見出しはh1〜h6、段落はp、箇条書きはul/ol/li、表はtable/thead/tbody/tr/th/tdを使う。
- CSS、script、imgを出力しない。表では可能な限り各trのセル数を揃える。
- 数字、符号、%などを変更・丸め・推測しない。
- 判読できない箇所は空欄にせず[判読不能]と書く。
- ページをまたぐ補完はせず、このページの内容だけを出力する。

入力補助:
{content_hint}
"""

def normalize_markdown(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:markdown|html)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    text = re.sub(r"<\|(?:begin|end)_of_box\|>", "", text)
    return text.strip() + "\n"


class ModelRunner:
    """Transformers経路を遅延ロードし、モデル未取得時はnot_runにする。"""

    def __init__(self, model_id: str, max_new_tokens: int = 4096) -> None:
        self.model_id = model_id
        self.max_new_tokens = max_new_tokens
        self.processor = None
        self.model = None
        self.reason: str | None = None

    def load(self) -> bool:
        try:
            from transformers import AutoModelForMultimodalLM, AutoProcessor

            self.processor = AutoProcessor.from_pretrained(self.model_id)
            self.model = AutoModelForMultimodalLM.from_pretrained(
                self.model_id,
                dtype="auto",
                device_map="auto",
            )
            return True
        except Exception as exc:  # noqa: BLE001 - 失敗理由をartifactへ記録する
            self.reason = f"{type(exc).__name__}: {exc}"
            return False

    def generate(self, instruction: str, image_path: Path | None = None) -> str:
        if self.processor is None or self.model is None:
            raise RuntimeError("model is not loaded")
        content: list[dict[str, Any]] = [{"type": "text", "text": instruction}]
        if image_path is not None:
            content.insert(0, {"type": "image", "url": str(image_path)})
        messages = [{"role": "user", "content": content}]
        inputs = self.processor.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self.model.device)
        input_length = inputs["input_ids"].shape[-1]
        output = self.model.generate(**inputs, max_new_tokens=self.max_new_tokens, do_sample=False)
        return self.processor.decode(output[0][input_length:], skip_special_tokens=True)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepare_documents(pdf_dir: Path, metadata_path: Path) -> dict[str, Any]:
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


def run_method(
    method: str,
    pdf_dir: Path,
    output_root: Path,
    metadata: dict[str, Any],
    run_model: bool,
    model_runner: ModelRunner | None,
    max_pages: int,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for spec in DOCUMENTS:
        document_meta = metadata["documents"].get(spec.key, {})
        pdf_path = pdf_dir / spec.filename
        if not pdf_path.exists():
            results.append({"method": method, "document": spec.key, "status": "not_run", "reason": "PDF not found"})
            continue
        with fitz.open(pdf_path) as document:
            selected_pages = select_pages(document, 3)
            for page_index in selected_pages:
                page = document[page_index]
                page_dir = output_root / method / spec.key
                page_dir.mkdir(parents=True, exist_ok=True)
                image_path: Path | None = None
                if method == "image_first":
                    image_path = page_dir / f"page-{page_index + 1:04d}.png"
                    render_page(page, image_path)
                    content_hint = str(image_path)
                else:
                    content_hint = parse_first_payload(page)
                    (page_dir / f"page-{page_index + 1:04d}.input.json").write_text(content_hint + "\n", encoding="utf-8")
                record: dict[str, Any] = {
                    "method": method,
                    "document": spec.key,
                    "page": page_index + 1,
                    "status": "not_run",
                    "input_text_length": len(page_text(page)),
                    "model": MODEL_NAME,
                    "model_id": MODEL_ID,
                }
                if not run_model:
                    record["reason"] = "run_model was not requested"
                elif model_runner is None or model_runner.reason:
                    record["reason"] = model_runner.reason if model_runner else "model runner unavailable"
                else:
                    started = time.perf_counter()
                    try:
                        output = model_runner.generate(prompt(method, page_index + 1, content_hint), image_path)
                        output_path = page_dir / f"page-{page_index + 1:04d}.md"
                        output_path.write_text(normalize_markdown(output), encoding="utf-8")
                        record.update({"status": "success", "output_path": str(output_path), "wall_time_seconds": time.perf_counter() - started})
                    except Exception as exc:  # noqa: BLE001 - 失敗をページ単位で記録する
                        record.update({"status": "failed", "reason": f"{type(exc).__name__}: {exc}", "wall_time_seconds": time.perf_counter() - started})
                results.append(record)
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-model", action="store_true")
    parser.add_argument("--max-new-tokens", type=int, default=4096)
    parser.add_argument("--max-pages", type=int, default=3)
    parser.add_argument("--root", type=Path, required=True, help="結果を保存する experiments/exp-xxx ディレクトリ")
    args = parser.parse_args()
    root = args.root
    pdf_dir = root / "workspace" / "input" / "pdfs"
    metadata_path = root / "workspace" / "input" / "documents.json"
    output_root = root / "workspace" / "outputs"
    metadata = prepare_documents(pdf_dir, metadata_path)
    runner: ModelRunner | None = None
    if args.run_model:
        runner = ModelRunner(MODEL_ID, args.max_new_tokens)
        if not runner.load():
            print(json.dumps({"model_status": "not_run", "reason": runner.reason}, ensure_ascii=False))
    all_records: list[dict[str, Any]] = []
    for method in ("parse_first", "image_first"):
        all_records.extend(run_method(method, pdf_dir, output_root, metadata, args.run_model, runner, args.max_pages))
    log_path = root / "logs" / "run.json"
    write_json(log_path, {"model": MODEL_NAME, "model_id": MODEL_ID, "run_model": args.run_model, "records": all_records})
    print(json.dumps({"metadata": str(metadata_path), "log": str(log_path), "records": len(all_records)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
