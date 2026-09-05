"""Issue #4 のLightRAG + Qwen 小規模pilotを実行するCLI。"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import logging
import re
import time
import urllib.request
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc
from openai import AsyncOpenAI

from category_grounded_agentic_search.infrastructure.hashing_embedding import hash_embed


LIGHTRAG_REVISION = "5183dec553da29e123d45f663045e8efe24cbedf"
ULTRADOMAIN_REVISION = "aa8a51d523f8fc3c5a0ab90dd16b7f6b9dbb5d0d"
ULTRADOMAIN_FILE = "mix.jsonl"
ULTRADOMAIN_SHA256 = "3e438f40c91a183a246446dd8435a8c1f0de004533e9e90f97ddf862d5c39bc9"
ULTRADOMAIN_URL = (
    "https://huggingface.co/datasets/TommyChien/UltraDomain/resolve/"
    f"{ULTRADOMAIN_REVISION}/{ULTRADOMAIN_FILE}?download=true"
)
QWEN_ENDPOINT = "http://192.168.100.11:8000/v1"
QWEN_MODEL = "llm"
QWEN_MODEL_ROOT = "Qwen/Qwen3.6-35B-A3B-FP8"
SERVER_FINGERPRINT = "vllm-0.27.0-5fc4282d"
PILOT_RECORD_IDS = (
    "d49ae70e5e40feb7bb8566a03b12bcd5",
    "317eeefd1a88349abb7abb993c14c5ff",
    "31893da0e3a4d9b06a209d4c7124500c",
    "f6bb8573679380686f84c661a761e65a",
)


@dataclass
class LlmCall:
    """vLLMから返るusageと遅延を記録する。"""

    elapsed_seconds: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    finish_reason: str | None
    role: str


@dataclass
class RunMetrics:
    """生成呼出しの合計を保持する。"""

    calls: list[LlmCall] = field(default_factory=list)

    def record(self, elapsed_seconds: float, response: Any, role: str) -> None:
        usage = response.usage
        self.calls.append(
            LlmCall(
                elapsed_seconds=elapsed_seconds,
                prompt_tokens=int(getattr(usage, "prompt_tokens", 0) or 0),
                completion_tokens=int(getattr(usage, "completion_tokens", 0) or 0),
                total_tokens=int(getattr(usage, "total_tokens", 0) or 0),
                finish_reason=getattr(response.choices[0], "finish_reason", None),
                role=role,
            )
        )

    def as_mapping(self) -> dict[str, Any]:
        return {
            "llm_call_count": len(self.calls),
            "prompt_tokens": sum(call.prompt_tokens for call in self.calls),
            "completion_tokens": sum(call.completion_tokens for call in self.calls),
            "total_tokens": sum(call.total_tokens for call in self.calls),
            "llm_latency_seconds": sum(call.elapsed_seconds for call in self.calls),
            "non_stop_finish_reasons": sum(
                call.finish_reason != "stop" for call in self.calls
            ),
            "non_stop_query_finish_reasons": sum(
                call.role == "query" and call.finish_reason != "stop"
                for call in self.calls
            ),
            "per_call": [asdict(call) for call in self.calls],
            "cost": {
                "currency": "USD",
                "value": None,
                "note": "self-hosted vLLM endpoint; token-priced API cost is not applicable",
            },
        }


def sha256_file(path: Path) -> str:
    """ファイル全体のSHA-256を計算する。"""
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def selected_records(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """固定ID・単一contextの4問を選び、入力driftを検出する。"""
    records_by_id = {str(row.get("_id")): row for row in rows}
    selected = [records_by_id[record_id] for record_id in PILOT_RECORD_IDS if record_id in records_by_id]
    if len(selected) != len(PILOT_RECORD_IDS):
        missing = sorted(set(PILOT_RECORD_IDS) - set(records_by_id))
        raise ValueError(f"UltraDomain revisionにpilot recordがありません: {missing}")
    contexts = {str(record["context"]) for record in selected}
    if len(contexts) != 1:
        raise ValueError("pilot recordは同一contextを共有する必要があります")
    for record in selected:
        if not isinstance(record.get("input"), str) or not record["input"].strip():
            raise ValueError(f"質問が空です: {record['_id']}")
        if not isinstance(record.get("answers"), list) or not record["answers"]:
            raise ValueError(f"gold answerがありません: {record['_id']}")
    return selected


def prepare_inputs(root: Path) -> dict[str, Any]:
    """固定Hub revisionから必要な4問だけを入力snapshotとして保存する。"""
    inputs_dir = root / "inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)
    download_path = inputs_dir / "ultradomain-mix.source.jsonl"
    urllib.request.urlretrieve(ULTRADOMAIN_URL, download_path)
    source_sha256 = sha256_file(download_path)
    if source_sha256 != ULTRADOMAIN_SHA256:
        raise ValueError(
            "UltraDomain source checksumが一致しません: "
            f"expected={ULTRADOMAIN_SHA256}, actual={source_sha256}"
        )

    with download_path.open(encoding="utf-8") as source:
        rows = [json.loads(line) for line in source if line.strip()]
    records = selected_records(rows)
    pilot_path = inputs_dir / "pilot_inputs.jsonl"
    with pilot_path.open("w", encoding="utf-8") as destination:
        for record in records:
            destination.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    download_path.unlink()

    context = str(records[0]["context"])
    document_id = f"ultradomain-mix-{hashlib.sha256(context.encode('utf-8')).hexdigest()[:16]}"
    manifest = {
        "schema_version": 1,
        "experiment_id": root.name,
        "purpose": "Issue #4 LightRAG + Qwen smoke pilot",
        "source": {
            "dataset": "TommyChien/UltraDomain",
            "revision": ULTRADOMAIN_REVISION,
            "file": ULTRADOMAIN_FILE,
            "url": ULTRADOMAIN_URL,
            "license": "Apache-2.0",
            "full_file_sha256": source_sha256,
        },
        "selection": {
            "record_ids": list(PILOT_RECORD_IDS),
            "record_count": len(records),
            "unique_document_count": 1,
            "document_id": document_id,
            "document_sha256": hashlib.sha256(context.encode("utf-8")).hexdigest(),
            "question_to_gold_document": {str(record["_id"]): document_id for record in records},
            "note": "同一documentの4問によるindex/query疎通確認。retrieval品質比較の評価セットではない。",
        },
        "pilot_inputs_sha256": sha256_file(pilot_path),
    }
    manifest_path = inputs_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def load_inputs(root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """準備済みsnapshotとmanifestを読み、再実行前の整合性を検証する。"""
    inputs_dir = root / "inputs"
    pilot_path = inputs_dir / "pilot_inputs.jsonl"
    manifest_path = inputs_dir / "manifest.json"
    if not pilot_path.is_file() or not manifest_path.is_file():
        raise FileNotFoundError("先に --prepare-inputs を実行してください")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if sha256_file(pilot_path) != manifest["pilot_inputs_sha256"]:
        raise ValueError("pilot input snapshotのchecksumがmanifestと一致しません")
    records = [json.loads(line) for line in pilot_path.read_text(encoding="utf-8").splitlines() if line]
    if [str(record["_id"]) for record in records] != list(PILOT_RECORD_IDS):
        raise ValueError("pilot input record IDが固定設定と一致しません")
    selected_records(records)
    return records, manifest


def configure_logger(log_path: Path) -> logging.Logger:
    """実行ログをexperiment artifactへ保存する。"""
    logger = logging.getLogger("issue4_lightrag_pilot")
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger


def build_llm_function(
    metrics: RunMetrics,
    logger: logging.Logger,
    *,
    role: str,
    max_tokens: int,
    require_stop: bool,
):
    """vLLMのusageを計測しつつ、LightRAG互換のcompletion関数を作る。"""

    async def complete(
        prompt: str,
        system_prompt: str | None = None,
        history_messages: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> str:
        messages: list[dict[str, Any]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(history_messages or [])
        messages.append({"role": "user", "content": prompt})
        for key in (
            "hashing_kv",
            "keyword_extraction",
            "token_tracker",
            "stream",
            "timeout",
            "model",
            "messages",
        ):
            kwargs.pop(key, None)
        response_format = kwargs.pop("response_format", None)
        request: dict[str, Any] = {
            "model": QWEN_MODEL,
            "messages": messages,
            "temperature": 0,
            "max_tokens": max_tokens,
            "extra_body": {"chat_template_kwargs": {"enable_thinking": False}},
        }
        if response_format is not None:
            request["response_format"] = response_format
        started = time.perf_counter()
        client = AsyncOpenAI(api_key="not-needed", base_url=QWEN_ENDPOINT, timeout=180)
        try:
            response = await client.chat.completions.create(**request)
        finally:
            await client.close()
        elapsed = time.perf_counter() - started
        metrics.record(elapsed, response, role)
        finish_reason = response.choices[0].finish_reason
        if require_stop and finish_reason != "stop":
            raise RuntimeError(f"vLLM completion did not finish normally: {finish_reason}")
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("vLLM returned an empty completion")
        logger.info(
            "%s llm call: prompt_tokens=%s completion_tokens=%s elapsed_seconds=%.3f finish_reason=%s",
            role,
            getattr(response.usage, "prompt_tokens", 0),
            getattr(response.usage, "completion_tokens", 0),
            elapsed,
            finish_reason,
        )
        return content

    return complete


def build_summary(
    experiment_id: str,
    manifest: dict[str, Any],
    metrics: RunMetrics,
    duration_seconds: float,
    extract_max_tokens: int,
) -> dict[str, Any]:
    """実行済みartifactを指すrun summaryを組み立てる。"""
    return {
        "experiment_id": experiment_id,
        "status": "completed",
        "run_kind": "small-scale index/query smoke pilot",
        "duration_seconds": duration_seconds,
        "input_manifest": "inputs/manifest.json",
        "lightrag": {
            "repository": "https://github.com/HKUDS/LightRAG",
            "revision": LIGHTRAG_REVISION,
            "chunk_token_size": 512,
            "chunk_overlap_token_size": 64,
            "retrieval_mode": "hybrid",
            "candidate_budget": {"top_k": 5, "chunk_top_k": 5},
            "embedding": "deterministic-hash-128-v1",
        },
        "llm": {
            "model_id": QWEN_MODEL_ROOT,
            "served_model_name": QWEN_MODEL,
            "serving_api": QWEN_ENDPOINT,
            "server_fingerprint": SERVER_FINGERPRINT,
            "temperature": 0,
            "max_tokens": {"extract": extract_max_tokens, "keyword": 512, "query": 768},
            "chat_template_kwargs": {"enable_thinking": False},
        },
        "queries_completed": len(manifest["selection"]["record_ids"]),
        "metrics": metrics.as_mapping(),
        "artifacts": {
            "query_results": "outputs/query_results.json",
            "lightrag_store": "outputs/lightrag-store",
            "log": "logs/run.log",
        },
    }


async def run_pilot(root: Path, extract_max_tokens: int) -> dict[str, Any]:
    """LightRAGのindex構築と4問のhybrid queryを一回だけ実行する。"""
    if extract_max_tokens < 512:
        raise ValueError("extract_max_tokensは512以上にしてください")
    records, manifest = load_inputs(root)
    outputs_dir = root / "outputs"
    logs_dir = root / "logs"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    store_dir = outputs_dir / "lightrag-store"
    if store_dir.exists():
        raise FileExistsError(f"既存のrun outputを保護するため再利用しません: {store_dir}")
    logger = configure_logger(logs_dir / "run.log")
    metrics = RunMetrics()
    document_id = manifest["selection"]["document_id"]
    context = str(records[0]["context"])
    started = time.perf_counter()
    rag = LightRAG(
        working_dir=str(store_dir),
        llm_model_func=build_llm_function(
            metrics, logger, role="query", max_tokens=768, require_stop=True
        ),
        role_llm_configs={
            "extract": {
                "func": build_llm_function(
                    metrics,
                    logger,
                    role="extract",
                    max_tokens=extract_max_tokens,
                    require_stop=False,
                )
            },
            "keyword": {
                "func": build_llm_function(
                    metrics, logger, role="keyword", max_tokens=512, require_stop=True
                )
            },
            "query": {
                "func": build_llm_function(
                    metrics, logger, role="query", max_tokens=768, require_stop=True
                )
            },
        },
        llm_model_name=QWEN_MODEL,
        embedding_func=EmbeddingFunc(
            embedding_dim=128,
            max_token_size=8192,
            model_name="deterministic-hash-128-v1",
            func=hash_embed,
        ),
        chunk_token_size=512,
        chunk_overlap_token_size=64,
        top_k=5,
        chunk_top_k=5,
        entity_extract_max_gleaning=0,
        entity_extraction_use_json=False,
        llm_model_max_async=1,
        embedding_func_max_async=1,
        default_llm_timeout=180,
    )
    try:
        await rag.initialize_storages()
        logger.info("indexing document_id=%s characters=%s", document_id, len(context))
        await rag.ainsert(context, ids=document_id, file_paths="inputs/pilot_inputs.jsonl")
        query_results = []
        for record in records:
            query_started = time.perf_counter()
            answer = await rag.aquery(
                str(record["input"]),
                param=QueryParam(
                    mode="hybrid",
                    response_type="Single Paragraph",
                    top_k=5,
                    chunk_top_k=5,
                    stream=False,
                    include_references=True,
                    user_prompt="Answer concisely in one paragraph using only the provided context.",
                ),
            )
            query_results.append(
                {
                    "question_id": str(record["_id"]),
                    "question": record["input"],
                    "gold_document_id": document_id,
                    "gold_answers": record["answers"],
                    "response": answer,
                    "latency_seconds": time.perf_counter() - query_started,
                }
            )
        (outputs_dir / "query_results.json").write_text(
            json.dumps(query_results, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    finally:
        await rag.finalize_storages()
    summary = build_summary(
        root.name, manifest, metrics, time.perf_counter() - started, extract_max_tokens
    )
    (outputs_dir / "run_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary


def recover_summary(root: Path, extract_max_tokens: int) -> dict[str, Any]:
    """summary書込みだけが失敗した完走runから、保存済みlogを基にsummaryを復元する。"""
    records, manifest = load_inputs(root)
    outputs_dir = root / "outputs"
    store_status_path = outputs_dir / "lightrag-store" / "kv_store_doc_status.json"
    query_results_path = outputs_dir / "query_results.json"
    log_path = root / "logs" / "run.log"
    if not store_status_path.is_file() or not query_results_path.is_file() or not log_path.is_file():
        raise FileNotFoundError("復元に必要なstore、query results、logがありません")
    statuses = json.loads(store_status_path.read_text(encoding="utf-8"))
    document_id = manifest["selection"]["document_id"]
    if statuses.get(document_id, {}).get("status") != "processed":
        raise ValueError("document indexがprocessedではないためsummaryを復元できません")
    query_results = json.loads(query_results_path.read_text(encoding="utf-8"))
    if len(query_results) != len(records) or any(
        not str(result.get("response", "")).strip()
        or "[no-context]" in str(result.get("response", ""))
        for result in query_results
    ):
        raise ValueError("全queryが有効なcontext付きresponseを返していません")
    line_pattern = re.compile(
        r"(?P<role>extract|keyword|query) llm call: prompt_tokens=(?P<prompt>\d+) "
        r"completion_tokens=(?P<completion>\d+) elapsed_seconds=(?P<elapsed>[0-9.]+) "
        r"finish_reason=(?P<finish>\S+)"
    )
    metrics = RunMetrics()
    for line in log_path.read_text(encoding="utf-8").splitlines():
        match = line_pattern.search(line)
        if match:
            prompt_tokens = int(match["prompt"])
            completion_tokens = int(match["completion"])
            metrics.calls.append(
                LlmCall(
                    elapsed_seconds=float(match["elapsed"]),
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                    finish_reason=match["finish"],
                    role=match["role"],
                )
            )
    if not metrics.calls or metrics.as_mapping()["non_stop_query_finish_reasons"]:
        raise ValueError("query completionのfinish reasonを検証できません")
    summary = build_summary(
        root.name,
        manifest,
        metrics,
        sum(call.elapsed_seconds for call in metrics.calls),
        extract_max_tokens,
    )
    (outputs_dir / "run_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    """CLI parserを構築する。"""
    parser = argparse.ArgumentParser(description="Issue #4 LightRAG + Qwen pilot")
    parser.add_argument("--root", type=Path, required=True, help="experiment root path")
    parser.add_argument(
        "--extract-max-tokens",
        type=int,
        default=512,
        help="entity/relation extraction roleのmax_tokens（既定: 512）",
    )
    parser.add_argument("--prepare-inputs", action="store_true", help="入力snapshotを作成する")
    parser.add_argument("--run", action="store_true", help="index構築とqueryを実行する")
    parser.add_argument(
        "--recover-summary", action="store_true", help="完走済みoutputのsummaryをlogから復元する"
    )
    return parser


def main() -> None:
    """CLI entry point。"""
    args = build_parser().parse_args()
    if not args.prepare_inputs and not args.run and not args.recover_summary:
        raise SystemExit("--prepare-inputs、--run、--recover-summaryのいずれかを指定してください")
    root = args.root.resolve()
    if args.prepare_inputs:
        if (root / "inputs" / "pilot_inputs.jsonl").exists():
            raise SystemExit("既存input snapshotを保護するため再作成しません")
        manifest = prepare_inputs(root)
        print(f"prepared inputs: {manifest['pilot_inputs_sha256']}")
    if args.run:
        summary = asyncio.run(run_pilot(root, args.extract_max_tokens))
        print(f"completed {summary['queries_completed']} queries")
    if args.recover_summary:
        summary = recover_summary(root, args.extract_max_tokens)
        print(f"recovered summary for {summary['queries_completed']} queries")


if __name__ == "__main__":
    main()
