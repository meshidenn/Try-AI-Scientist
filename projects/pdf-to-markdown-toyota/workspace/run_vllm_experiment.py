#!/usr/bin/env python3
"""vLLM OpenAI互換APIでToyota PDFの2方式を比較するクライアント。"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from run_experiment import (
    DOCUMENTS,
    MODEL_ID,
    MODEL_NAME,
    html_prompt,
    normalize_markdown,
    page_text,
    parse_first_payload,
    prepare_documents,
    prompt,
    render_page,
    select_pages,
)


def local_media_url(image_path: Path, media_root: Path) -> str:
    relative = image_path.relative_to(media_root).as_posix()
    return f"file:///workspace/{relative}"


def request_completion(base_url: str, model: str, messages: list[dict[str, Any]], max_tokens: int) -> str:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0,
        "top_p": 1,
        "max_tokens": max_tokens,
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": "Bearer EMPTY"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=1800) as response:
        result = json.loads(response.read().decode("utf-8"))
    return result["choices"][0]["message"]["content"]


def build_messages(method: str, page_number: int, content_hint: str, image_url: str | None, output_format: str) -> list[dict[str, Any]]:
    text = html_prompt(method, page_number, content_hint) if output_format == "html" else prompt(method, page_number, content_hint)
    if image_url is None:
        return [{"role": "user", "content": text}]
    return [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": text},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        }
    ]


def run(args: argparse.Namespace) -> dict[str, Any]:
    root = args.root
    pdf_dir = args.pdf_dir or (root / "workspace" / "input" / "pdfs")
    metadata_path = root / "workspace" / "input" / "documents.json"
    output_root = root / "workspace" / ("outputs-vllm-html" if args.output_format == "html" else "outputs-vllm")
    media_root = root / "workspace"
    metadata = prepare_documents(pdf_dir, metadata_path)
    records: list[dict[str, Any]] = []
    selected_documents = set(args.documents or [spec.key for spec in DOCUMENTS])
    for method in args.methods:
        for spec in DOCUMENTS:
            if spec.key not in selected_documents:
                continue
            pdf_path = pdf_dir / spec.filename
            if not pdf_path.exists():
                records.append({"method": method, "document": spec.key, "status": "not_run", "reason": "PDF not found"})
                continue
            import fitz

            with fitz.open(pdf_path) as document:
                if args.pages:
                    page_indexes = [page - 1 for page in args.pages if 1 <= page <= len(document)]
                else:
                    page_indexes = select_pages(document, args.max_pages)
                for page_index in page_indexes:
                    page = document[page_index]
                    page_dir = output_root / method / spec.key
                    page_dir.mkdir(parents=True, exist_ok=True)
                    image_path: Path | None = None
                    if method == "image_first":
                        image_path = page_dir / f"page-{page_index + 1:04d}.png"
                        render_page(page, image_path)
                        content_hint = "ページ画像を参照する。"
                    else:
                        content_hint = parse_first_payload(page)
                        (page_dir / f"page-{page_index + 1:04d}.input.json").write_text(content_hint + "\n", encoding="utf-8")
                    record: dict[str, Any] = {
                        "method": method,
                        "document": spec.key,
                        "page": page_index + 1,
                        "model": MODEL_NAME,
                        "model_id": MODEL_ID,
                        "backend": "vllm_openai",
                        "output_format": args.output_format,
                        "status": "failed",
                        "input_text_length": len(page_text(page)),
                    }
                    started = time.perf_counter()
                    try:
                        image_url = local_media_url(image_path, media_root) if image_path else None
                        output = request_completion(args.base_url, args.model, build_messages(method, page_index + 1, content_hint, image_url, args.output_format), args.max_new_tokens)
                        extension = "html" if args.output_format == "html" else "md"
                        output_path = page_dir / f"page-{page_index + 1:04d}.{extension}"
                        output_path.write_text(normalize_markdown(output), encoding="utf-8")
                        record.update({"status": "success", "output_path": str(output_path)})
                    except urllib.error.HTTPError as exc:
                        detail = exc.read().decode("utf-8", errors="replace")
                        record["reason"] = f"HTTPError: {exc.code} {detail}"
                    except (OSError, urllib.error.URLError, KeyError, json.JSONDecodeError) as exc:
                        record["reason"] = f"{type(exc).__name__}: {exc}"
                    except Exception as exc:  # noqa: BLE001 - ページ単位の失敗を保存する
                        record["reason"] = f"{type(exc).__name__}: {exc}"
                    record["wall_time_seconds"] = time.perf_counter() - started
                    records.append(record)
    result = {
        "model": MODEL_NAME,
        "model_id": MODEL_ID,
        "backend": "vllm_openai",
        "base_url": args.base_url,
        "served_model": args.model,
        "max_pages": args.max_pages,
        "max_new_tokens": args.max_new_tokens,
        "output_format": args.output_format,
        "records": records,
    }
    log_path = root / "logs" / args.log_name
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"log": str(log_path), "records": len(records)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True, help="結果を保存する experiments/exp-xxx ディレクトリ")
    parser.add_argument("--pdf-dir", type=Path, default=None)
    parser.add_argument("--base-url", default="http://127.0.0.1:18021/v1")
    parser.add_argument("--model", default="gemma4-26b-moe")
    parser.add_argument("--methods", nargs="+", choices=("parse_first", "image_first"), default=("parse_first", "image_first"))
    parser.add_argument("--documents", nargs="+", choices=tuple(spec.key for spec in DOCUMENTS))
    parser.add_argument("--pages", nargs="+", type=int)
    parser.add_argument("--max-pages", type=int, default=1)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--output-format", choices=("markdown", "html"), default="markdown")
    parser.add_argument("--log-name", default="vllm-run.json")
    args = parser.parse_args()
    print(json.dumps(run(args), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
