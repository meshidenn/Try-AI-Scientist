#!/usr/bin/env python3
"""PDF parse payloadとページ画像を融合するhybrid Markdown実験。"""

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
    normalize_markdown,
    page_text,
    parse_first_payload,
    prepare_documents,
    render_page,
    select_pages,
)


def hybrid_prompt(page_number: int, parse_payload: str) -> str:
    return f"""あなたは企業PDFを忠実にMarkdown化する抽出器です。
添付画像はPDFの1ページであり、入力補助は同じページから抽出した文字block・座標です。
ページ番号: {page_number}

根拠の優先規則:
- 表: 文字列、数値、符号、単位、注記は入力補助を正とする。画像はセルの行列・結合・読み順を判断するためだけに使う。
- グラフ・図: 棒の相対位置、系列、矢印、領域の対応は画像を正とする。ラベルと数値は入力補助にある値を優先し、推測しない。
- 本文・複合レイアウト: 画像で段組み・キャプション・見出しの親子関係を確認し、入力補助の文字列を用いる。

出力規則:
- 出力はMarkdown本文だけにする。コードフェンスは使わない。
- 見出し、段落、箇条書き、表、脚注の順序を可能な限り保つ。
- 表はMarkdown tableにし、列数を各行で揃える。単位と注記も残す。
- 数字、符号、%などを変更・丸め・補完しない。判読不能は`[判読不能]`と書く。
- 点線、罫線、軸、塗りつぶし、矢印の線分など装飾だけの図形は出力しない。同じ記号の反復で図形を描かない。
- グラフはラベル、数値、系列、位置関係を一度ずつ構造化して記述し、視覚的な点線・棒・グリッドを文字で再現しない。
- ページをまたぐ補完はせず、このページの内容だけを出力する。

入力補助:
{parse_payload}
"""


def local_media_url(image_path: Path, media_root: Path) -> str:
    return f"file:///workspace/{image_path.relative_to(media_root).as_posix()}"


def request_completion(base_url: str, model: str, messages: list[dict[str, Any]], max_tokens: int) -> str:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0,
        "top_p": 1,
        "max_tokens": max_tokens,
    }
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": "Bearer EMPTY"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=1800) as response:
        return json.loads(response.read().decode("utf-8"))["choices"][0]["message"]["content"]


def run(args: argparse.Namespace) -> dict[str, Any]:
    root = args.root
    pdf_dir = args.pdf_dir
    metadata_path = root / "workspace" / "input" / "documents.json"
    output_root = root / "workspace" / "outputs-hybrid"
    media_root = root / "workspace"
    prepare_documents(pdf_dir, metadata_path)
    selected_documents = set(args.documents or [spec.key for spec in DOCUMENTS])
    records: list[dict[str, Any]] = []

    import fitz

    for spec in DOCUMENTS:
        if spec.key not in selected_documents:
            continue
        pdf_path = pdf_dir / spec.filename
        if not pdf_path.exists():
            records.append({"method": "hybrid", "document": spec.key, "status": "not_run", "reason": "PDF not found"})
            continue
        with fitz.open(pdf_path) as document:
            page_indexes = [page - 1 for page in args.pages if 1 <= page <= len(document)] if args.pages else select_pages(document, args.max_pages)
            for page_index in page_indexes:
                page = document[page_index]
                page_dir = output_root / spec.key
                page_dir.mkdir(parents=True, exist_ok=True)
                image_path = page_dir / f"page-{page_index + 1:04d}.png"
                render_page(page, image_path)
                parse_payload = parse_first_payload(page)
                (page_dir / f"page-{page_index + 1:04d}.input.json").write_text(parse_payload + "\n", encoding="utf-8")
                record: dict[str, Any] = {
                    "method": "hybrid",
                    "document": spec.key,
                    "page": page_index + 1,
                    "model": MODEL_NAME,
                    "model_id": MODEL_ID,
                    "backend": "vllm_openai",
                    "output_format": "markdown",
                    "input_text_length": len(page_text(page)),
                    "input_modalities": ["parse_payload", "page_image"],
                    "status": "failed",
                }
                started = time.perf_counter()
                try:
                    messages = [{"role": "user", "content": [
                        {"type": "text", "text": hybrid_prompt(page_index + 1, parse_payload)},
                        {"type": "image_url", "image_url": {"url": local_media_url(image_path, media_root)}},
                    ]}]
                    output = request_completion(args.base_url, args.model, messages, args.max_new_tokens)
                    output_path = page_dir / f"page-{page_index + 1:04d}.md"
                    output_path.write_text(normalize_markdown(output), encoding="utf-8")
                    record.update({"status": "success", "output_path": str(output_path)})
                except urllib.error.HTTPError as exc:
                    record["reason"] = f"HTTPError: {exc.code} {exc.read().decode('utf-8', errors='replace')}"
                except Exception as exc:  # noqa: BLE001 - ページ単位の失敗をartifact化する
                    record["reason"] = f"{type(exc).__name__}: {exc}"
                record["wall_time_seconds"] = time.perf_counter() - started
                records.append(record)

    result = {
        "model": MODEL_NAME,
        "model_id": MODEL_ID,
        "backend": "vllm_openai",
        "base_url": args.base_url,
        "max_pages": args.max_pages,
        "max_new_tokens": args.max_new_tokens,
        "routing_policy": "table=parse; chart=image; layout=both",
        "records": records,
    }
    log_path = root / "logs" / args.log_name
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"log": str(log_path), "records": len(records)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True, help="結果を保存する experiments/exp-xxx ディレクトリ")
    parser.add_argument("--pdf-dir", type=Path, required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:18021/v1")
    parser.add_argument("--model", default="gemma4-26b-moe")
    parser.add_argument("--documents", nargs="+", choices=tuple(spec.key for spec in DOCUMENTS))
    parser.add_argument("--pages", nargs="+", type=int)
    parser.add_argument("--max-pages", type=int, default=3)
    parser.add_argument("--max-new-tokens", type=int, default=1024)
    parser.add_argument("--log-name", default="hybrid-run.json")
    args = parser.parse_args()
    print(json.dumps(run(args), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
