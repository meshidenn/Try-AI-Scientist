#!/usr/bin/env python3
"""ローカルvLLMで複数VLMを同じPDFページへ適用する共有実行器。"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import fitz

from run_experiment import (
    DOCUMENTS,
    normalize_markdown,
    page_text,
    parse_first_payload,
    prompt,
    render_page,
)
from run_hybrid_experiment import hybrid_prompt


def require_local_base_url(base_url: str) -> None:
    """外部のOpenAI互換endpointを誤って使わないようにする。"""
    host = urllib.parse.urlparse(base_url).hostname
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError(f"外部endpointは使用できません: {base_url}")


def load_source_pdf_dir(root: Path) -> Path:
    manifest_path = root / "inputs" / "source-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source = (manifest_path.parent / manifest["source_pdf_directory"]).resolve()
    if not source.is_dir():
        raise FileNotFoundError(f"PDF入力ディレクトリがありません: {source}")
    return source


def load_pages(root: Path, pilot: bool) -> dict[str, list[int]]:
    if not pilot:
        return {}
    payload = json.loads((root / "inputs" / "pilot-pages.json").read_text(encoding="utf-8"))
    return {spec.key: list(payload.get(spec.key, [])) for spec in DOCUMENTS}


def local_media_url(path: Path, root: Path) -> str:
    return f"file:///workspace/{path.relative_to(root).as_posix()}"


def request_completion(
    base_url: str,
    model: str,
    messages: list[dict[str, Any]],
    max_tokens: int,
    disable_thinking: bool,
) -> str:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0,
        "top_p": 1,
        "max_tokens": max_tokens,
    }
    if disable_thinking:
        payload["chat_template_kwargs"] = {"enable_thinking": False}
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": "Bearer EMPTY"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=1800) as response:
        result = json.loads(response.read().decode("utf-8"))
    return result["choices"][0]["message"]["content"]


def bounded_payload(payload: str, max_chars: int | None) -> str:
    """画像と併用する抽出payloadを指定文字数に収める。"""
    if max_chars is None or len(payload) <= max_chars:
        return payload
    return payload[:max_chars] + "\n\n[抽出payloadはコンテキスト上限のためここで省略]\n"


def messages_for(
    mode: str,
    page_number: int,
    payload: str,
    image_url: str,
    native_instruction: str | None = None,
) -> list[dict[str, Any]]:
    if mode == "hybrid":
        instruction = hybrid_prompt(page_number, payload)
    elif mode == "image_first":
        instruction = prompt("image_first", page_number, "ページ画像を参照する。")
    elif mode == "native_ocr":
        if not native_instruction:
            raise ValueError("native_ocrには--native-instructionが必要です")
        instruction = native_instruction
    else:
        raise ValueError(f"未対応のmodeです: {mode}")
    return [{"role": "user", "content": [
        {"type": "text", "text": instruction},
        {"type": "image_url", "image_url": {"url": image_url}},
    ]}]


def record_key(record: dict[str, Any]) -> tuple[str, str, int]:
    """再開時にモデル内のページ出力を一意に識別する。"""
    return (str(record["method"]), str(record["document"]), int(record["page"]))


def is_completed_record(record: dict[str, Any]) -> bool:
    """成功記録と非空の出力ファイルがそろう場合だけskip可能とする。"""
    output_path = record.get("output_path")
    return bool(
        record.get("status") == "success"
        and output_path
        and Path(output_path).is_file()
        and Path(output_path).stat().st_size > 0
    )


def result_payload(args: argparse.Namespace, root: Path, records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "experiment_id": root.name,
        "model": args.logical_name,
        "model_id": args.model_id,
        "backend": "local_vllm_openai",
        "base_url": args.base_url,
        "pilot": args.pilot,
        "modes": list(args.modes),
        "max_new_tokens": args.max_new_tokens,
        "records": records,
    }


def write_checkpoint(log_path: Path, args: argparse.Namespace, root: Path, records: list[dict[str, Any]]) -> None:
    """各ページ完了直後にログを更新し、途中終了でも成功分を残す。"""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(result_payload(args, root, records), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> dict[str, Any]:
    require_local_base_url(args.base_url)
    root = args.root.resolve()
    pdf_dir = args.pdf_dir.resolve() if args.pdf_dir else load_source_pdf_dir(root)
    pages_by_document = load_pages(root, args.pilot)
    output_root = root / "outputs" / args.logical_name
    log_path = root / "logs" / args.log_name
    records: list[dict[str, Any]] = []
    completed: dict[tuple[str, str, int], dict[str, Any]] = {}
    if args.resume and log_path.exists():
        previous = json.loads(log_path.read_text(encoding="utf-8"))
        for record in previous.get("records", []):
            if is_completed_record(record):
                completed[record_key(record)] = record

    for spec in DOCUMENTS:
        pdf_path = pdf_dir / spec.filename
        page_numbers = pages_by_document.get(spec.key, [])
        if not pdf_path.exists():
            records.append({"model": args.logical_name, "document": spec.key, "status": "not_run", "reason": "PDF not found"})
            continue
        with fitz.open(pdf_path) as document:
            if not page_numbers:
                page_numbers = list(range(1, len(document) + 1))
            for page_number in page_numbers:
                if not 1 <= page_number <= len(document):
                    records.append({"model": args.logical_name, "document": spec.key, "page": page_number, "status": "not_run", "reason": "page out of range"})
                    continue
                page = document[page_number - 1]
                payload = bounded_payload(parse_first_payload(page), args.max_payload_chars)
                for mode in args.modes:
                    key = (mode, spec.key, page_number)
                    if key in completed:
                        records.append(completed[key])
                        continue
                    page_dir = output_root / mode / spec.key
                    page_dir.mkdir(parents=True, exist_ok=True)
                    image_path = page_dir / f"page-{page_number:04d}.png"
                    input_path = page_dir / f"page-{page_number:04d}.input.json"
                    render_page(page, image_path)
                    input_path.write_text(payload + "\n", encoding="utf-8")
                    record: dict[str, Any] = {
                        "model": args.logical_name,
                        "model_id": args.model_id,
                        "served_model": args.served_model,
                        "model_revision": args.model_revision,
                        "backend": "local_vllm_openai",
                        "base_url": args.base_url,
                        "method": mode,
                        "document": spec.key,
                        "page": page_number,
                        "output_format": "markdown",
                        "input_modalities": ["page_image"] if mode in {"image_first", "native_ocr"} else ["page_image", "parse_payload"],
                        "input_text_length": len(page_text(page)),
                        "status": "failed",
                    }
                    started = time.perf_counter()
                    try:
                        output = request_completion(
                            args.base_url,
                            args.served_model,
                            messages_for(
                                mode,
                                page_number,
                                payload,
                                local_media_url(image_path, root),
                                args.native_instruction,
                            ),
                            args.max_new_tokens,
                            args.disable_thinking,
                        )
                        output_path = page_dir / f"page-{page_number:04d}.md"
                        output_path.write_text(normalize_markdown(output), encoding="utf-8")
                        record.update({"status": "success", "output_path": str(output_path)})
                    except urllib.error.HTTPError as exc:
                        record["reason"] = f"HTTPError: {exc.code} {exc.read().decode('utf-8', errors='replace')}"
                    except Exception as exc:  # noqa: BLE001 - ページ単位の失敗を残す
                        record["reason"] = f"{type(exc).__name__}: {exc}"
                    record["wall_time_seconds"] = round(time.perf_counter() - started, 6)
                    records.append(record)
                    write_checkpoint(log_path, args, root, records)

    write_checkpoint(log_path, args, root, records)
    return {"log": str(log_path), "records": len(records)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--logical-name", required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--served-model", required=True)
    parser.add_argument("--model-revision", default=None)
    parser.add_argument("--base-url", default="http://127.0.0.1:18021/v1")
    parser.add_argument("--pdf-dir", type=Path, default=None)
    parser.add_argument("--modes", nargs="+", choices=("image_first", "hybrid", "native_ocr"), default=("image_first", "hybrid"))
    parser.add_argument("--native-instruction", default=None, help="native_ocrで使用するモデル固有の指示文")
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--resume", action="store_true", help="既存logで成功済みかつ非空のページ出力をskipする")
    parser.add_argument("--max-payload-chars", type=int, default=None, help="hybridで渡すparse payloadの最大文字数")
    parser.add_argument("--disable-thinking", action="store_true", help="対応モデルではthinking出力を無効化する")
    parser.add_argument("--max-new-tokens", type=int, default=4096)
    parser.add_argument("--log-name", default="general-vlm-run.json")
    args = parser.parse_args()
    print(json.dumps(run(args), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
