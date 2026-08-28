"""UltraDomainを用いるLightRAG論文プロトコル準拠Qwen variantのCLI。"""

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
from pathlib import Path
from typing import Any

from dotenv import dotenv_values
from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc
from openai import AsyncOpenAI, OpenAI

from category_grounded_agentic_search.infrastructure.hashing_embedding import hash_embed
from category_grounded_agentic_search.infrastructure.bge_m3_embedding import (
    EMBEDDING_DIMENSION as BGE_M3_DIMENSION,
    MODEL_ID as BGE_M3_MODEL,
    bge_m3_embed,
    prewarm_bge_m3,
)
from category_grounded_agentic_search.interfaces.lightrag_pilot import (
    LIGHTRAG_REVISION,
    QWEN_ENDPOINT,
    QWEN_MODEL,
    QWEN_MODEL_ROOT,
    ULTRADOMAIN_FILE,
    ULTRADOMAIN_REVISION,
    ULTRADOMAIN_SHA256,
    ULTRADOMAIN_URL,
    LlmCall,
    RunMetrics,
    sha256_file,
)

JUDGE_MODEL = "gpt-4o-mini"
PROMETHEUS_ENDPOINT = "http://192.168.100.11:8001/v1"
PROMETHEUS_MODEL = "prometheus-2"
SERVER_FINGERPRINT = "vllm endpoint; max_model_len=262144 (user-reported 2026-08-26)"
DEFAULT_EXTRACT_MAX_TOKENS = 2048
QUERY_COUNT = 5
SUBSET_CONTEXT_COUNT = 3
EXTRACT_TIMEOUT_SECONDS = 900


def completion_timeout_seconds(max_tokens: int) -> float:
    """出力上限に比例したtimeoutを返す。"""
    return max(EXTRACT_TIMEOUT_SECONDS, max_tokens / 18)


def unique_contexts(rows: Iterable[dict[str, Any]]) -> list[dict[str, str]]:
    """UltraDomainの重複contextを内容SHA-256で除去して安定順序にする。"""
    by_hash: dict[str, str] = {}
    for row in rows:
        context = row.get("context")
        if not isinstance(context, str) or not context.strip():
            continue
        digest = hashlib.sha256(context.encode("utf-8")).hexdigest()
        by_hash.setdefault(digest, context)
    return [
        {"document_id": f"ultradomain-{digest[:16]}", "context_sha256": digest, "context": context}
        for digest, context in sorted(by_hash.items())
    ]


def context_description(context: str, *, maximum_characters: int = 6000) -> str:
    """論文のcontext descriptionに対応する、Qwenのcontext window内の説明を作る。"""
    if len(context) <= maximum_characters:
        return context
    half = maximum_characters // 2
    return f"{context[:half]}\n\n[...middle omitted...]\n\n{context[-half:]}"


def parse_questions(text: str, *, expected_count: int) -> list[str]:
    """Qwenが返した番号付き質問から固定数の非重複queryを抽出する。"""
    candidates = re.findall(r"(?:^|\n)\s*(?:[-*]|\d+[.)])\s*(?:Question\s*\d*[:.)-]*)?\s*(.+)", text)
    questions: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        question = candidate.strip().strip('"')
        if not question or question.lower().startswith(("user", "task")):
            continue
        if not question.endswith("?"):
            question = f"{question}?"
        normalized = re.sub(r"\s+", " ", question).lower()
        if normalized not in seen:
            seen.add(normalized)
            questions.append(question)
        if len(questions) == expected_count:
            return questions
    raise ValueError(f"Qwenが必要な{expected_count}件の質問を返しませんでした: {questions}")


def configure_logger(log_path: Path) -> logging.Logger:
    """実行ログをexperiment artifactへ保存する。"""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("lightrag_reproduction")
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger


def qwen_completion(
    metrics: RunMetrics,
    logger: logging.Logger,
    *,
    role: str,
    max_tokens: int,
):
    """usageを記録するLightRAG互換Qwen completion関数を作る。"""

    async def complete(
        prompt: str,
        system_prompt: str | None = None,
        history_messages: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> str:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(history_messages or [])
        messages.append({"role": "user", "content": prompt})
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
        client = AsyncOpenAI(
            api_key="not-needed",
            base_url=QWEN_ENDPOINT,
            timeout=completion_timeout_seconds(max_tokens),
        )
        started = time.perf_counter()
        try:
            response = await client.chat.completions.create(**request)
        finally:
            await client.close()
        elapsed = time.perf_counter() - started
        metrics.record(elapsed, response, role)
        finish_reason = response.choices[0].finish_reason
        content = response.choices[0].message.content
        if finish_reason != "stop" or not content:
            raise RuntimeError(f"Qwen {role} completionが正常終了しませんでした: {finish_reason}")
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


async def generate_questions(root: Path, query_count: int) -> list[str]:
    """固定context subsetから論文の高水準query生成を縮小して実行する。"""
    manifest = json.loads((root / "inputs" / "manifest.json").read_text(encoding="utf-8"))
    context_rows = [
        json.loads(line)
        for line in (root / "inputs" / "contexts.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    descriptions = "\n\n--- CONTEXT ---\n\n".join(
        context_description(str(row["context"])) for row in context_rows
    )
    prompt = (
        "Given the following description of a dataset, generate exactly "
        f"{query_count} high-level questions that require understanding across the dataset. "
        "Return only a numbered list of questions, one question per line.\n\n"
        f"Dataset description:\n{descriptions}"
    )
    logger = configure_logger(root / "logs" / "query-generation.log")
    metrics = RunMetrics()
    complete = qwen_completion(metrics, logger, role="query_generation", max_tokens=1024)
    response = await complete(prompt)
    questions = parse_questions(response, expected_count=query_count)
    output_path = root / "inputs" / "generated_queries.json"
    output_path.write_text(json.dumps(questions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    metadata = {
        "generator": {
            "model_id": QWEN_MODEL_ROOT,
            "served_model_name": QWEN_MODEL,
            "temperature": 0,
            "max_tokens": 1024,
            "chat_template_kwargs": {"enable_thinking": False},
        },
        "query_count": len(questions),
        "metrics": metrics.as_mapping(),
        "manifest_sha256": sha256_file(root / "inputs" / "manifest.json"),
    }
    (root / "inputs" / "query_generation.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    manifest["generated_queries_sha256"] = sha256_file(output_path)
    (root / "inputs" / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return questions


def prepare_inputs(
    root: Path, subset_context_count: int, excluded_document_ids: Iterable[str] = ()
) -> dict[str, Any]:
    """固定UltraDomain revisionから安定したunique context subsetを保存する。"""
    if subset_context_count <= 0:
        raise ValueError("subset_context_countは1以上にしてください")
    inputs = root / "inputs"
    inputs.mkdir(parents=True, exist_ok=True)
    source_path = inputs / "ultradomain-mix.source.jsonl"
    urllib.request.urlretrieve(ULTRADOMAIN_URL, source_path)
    source_sha256 = sha256_file(source_path)
    if source_sha256 != ULTRADOMAIN_SHA256:
        raise ValueError("UltraDomain source checksumが一致しません")
    with source_path.open(encoding="utf-8") as source:
        contexts = unique_contexts(json.loads(line) for line in source if line.strip())
    if len(contexts) < subset_context_count:
        raise ValueError("要求したsubsetよりunique contextが少なすぎます")
    excluded = set(excluded_document_ids)
    candidates = [row for row in contexts if row["document_id"] not in excluded]
    selected = sorted(candidates, key=lambda row: (len(row["context"]), row["context_sha256"]))[
        :subset_context_count
    ]
    if len(selected) != subset_context_count:
        raise ValueError("除外後に要求したsubsetよりunique contextが少なすぎます")
    contexts_path = inputs / "contexts.jsonl"
    with contexts_path.open("w", encoding="utf-8") as destination:
        for context in selected:
            destination.write(json.dumps(context, ensure_ascii=False, sort_keys=True) + "\n")
    source_path.unlink()
    manifest = {
        "schema_version": 1,
        "experiment_id": root.name,
        "purpose": "LightRAG paper-protocol Qwen variant small-subset implementation pilot",
        "source": {
            "dataset": "TommyChien/UltraDomain",
            "revision": ULTRADOMAIN_REVISION,
            "file": ULTRADOMAIN_FILE,
            "url": ULTRADOMAIN_URL,
            "license": "Apache-2.0",
            "full_file_sha256": source_sha256,
        },
        "selection": {
            "selection_rule": "unique contextを文字数昇順、同長ならSHA-256昇順で選ぶ",
            "source_unique_context_count": len(contexts),
            "selected_unique_context_count": len(selected),
            "documents": [
                {"document_id": row["document_id"], "context_sha256": row["context_sha256"]}
                for row in selected
            ],
            "limitation": "論文の全量評価ではなく、実装確認用の縮小subsetである。",
            "excluded_document_ids": sorted(excluded),
        },
        "context_snapshot_sha256": sha256_file(contexts_path),
        "protocol": {
            "query_generation": "Qwenによる高水準query生成。原論文のGPT-4o生成を置換したQwen variant。",
            "methods": ["lightrag_hybrid", "lightrag_naive"],
            "judge_model": JUDGE_MODEL,
            "judge": "GPT-4o-mini pairwise LLM-as-a-judge、回答順を交互にする。",
        },
    }
    (inputs / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def load_inputs(root: Path) -> tuple[list[dict[str, str]], list[str], dict[str, Any]]:
    """入力snapshot、query、manifestを照合して読み込む。"""
    inputs = root / "inputs"
    contexts_path = inputs / "contexts.jsonl"
    queries_path = inputs / "generated_queries.json"
    manifest_path = inputs / "manifest.json"
    if not contexts_path.is_file() or not queries_path.is_file() or not manifest_path.is_file():
        raise FileNotFoundError("--prepare-inputs と --generate-queries を先に実行してください")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if sha256_file(contexts_path) != manifest["context_snapshot_sha256"]:
        raise ValueError("context snapshotのchecksumがmanifestと一致しません")
    if sha256_file(queries_path) != manifest["generated_queries_sha256"]:
        raise ValueError("generated queryのchecksumがmanifestと一致しません")
    contexts = [json.loads(line) for line in contexts_path.read_text(encoding="utf-8").splitlines() if line]
    queries = json.loads(queries_path.read_text(encoding="utf-8"))
    if not contexts or not all(isinstance(row.get("context"), str) for row in contexts):
        raise ValueError("context snapshotが不正です")
    if not isinstance(queries, list) or not all(isinstance(query, str) and query.strip() for query in queries):
        raise ValueError("generated queryが不正です")
    return contexts, queries, manifest


def load_contexts_for_index(root: Path) -> tuple[list[dict[str, str]], dict[str, Any]]:
    """queryを必要としないindex-only用のcontext snapshotを検証して読む。"""
    inputs = root / "inputs"
    contexts_path = inputs / "contexts.jsonl"
    manifest_path = inputs / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if sha256_file(contexts_path) != manifest["context_snapshot_sha256"]:
        raise ValueError("context snapshotのchecksumがmanifestと一致しません")
    contexts = [json.loads(line) for line in contexts_path.read_text(encoding="utf-8").splitlines() if line]
    return contexts, manifest


def build_rag(
    store_dir: Path, metrics: RunMetrics, logger: logging.Logger, extract_max_tokens: int,
    embedding_model: str = "hash"
) -> LightRAG:
    """Qwenと指定した抽出上限を用いるLightRAG instanceを作る。"""
    embedding_dim, embedding_name, embedding_func = (
        (BGE_M3_DIMENSION, BGE_M3_MODEL, bge_m3_embed)
        if embedding_model == "bge-m3"
        else (128, "deterministic-hash-128-v1", hash_embed)
    )
    return LightRAG(
        working_dir=str(store_dir),
        llm_model_func=qwen_completion(metrics, logger, role="query", max_tokens=768),
        role_llm_configs={
            "extract": {
                "func": qwen_completion(
                    metrics, logger, role="extract", max_tokens=extract_max_tokens
                )
            },
            "keyword": {"func": qwen_completion(metrics, logger, role="keyword", max_tokens=512)},
            "query": {"func": qwen_completion(metrics, logger, role="query", max_tokens=768)},
        },
        llm_model_name=QWEN_MODEL,
        embedding_func=EmbeddingFunc(
            embedding_dim=embedding_dim,
            max_token_size=8192,
            model_name=embedding_name,
            func=embedding_func,
        ),
        chunk_token_size=512,
        chunk_overlap_token_size=64,
        top_k=5,
        chunk_top_k=5,
        entity_extract_max_gleaning=0,
        entity_extraction_use_json=False,
        llm_model_max_async=1,
        embedding_func_max_async=1,
        default_llm_timeout=completion_timeout_seconds(extract_max_tokens),
    )


def ensure_documents_processed(store: Path, document_ids: Iterable[str]) -> None:
    """LightRAGが抽出失敗を隠して完了扱いにしないよう検証する。"""
    status_path = store / "kv_store_doc_status.json"
    statuses = json.loads(status_path.read_text(encoding="utf-8"))
    incomplete = {
        document_id: statuses.get(document_id, {}).get("status", "missing")
        for document_id in document_ids
        if statuses.get(document_id, {}).get("status") != "processed"
    }
    if incomplete:
        raise RuntimeError(f"LightRAG indexに未処理documentがあります: {incomplete}")


async def run_methods(root: Path, extract_max_tokens: int) -> dict[str, Any]:
    """同一indexに対しhybridとnaive query modeを実行する。"""
    contexts, queries, manifest = load_inputs(root)
    outputs = root / "outputs"
    logs = root / "logs"
    outputs.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    store = outputs / "lightrag-store"
    if store.exists():
        raise FileExistsError(f"既存run outputを保護するため再利用しません: {store}")
    logger = configure_logger(logs / "run.log")
    metrics = RunMetrics()
    if extract_max_tokens < DEFAULT_EXTRACT_MAX_TOKENS:
        raise ValueError(f"extract_max_tokensは{DEFAULT_EXTRACT_MAX_TOKENS}以上にしてください")
    rag = build_rag(store, metrics, logger, extract_max_tokens)
    started = time.perf_counter()
    try:
        await rag.initialize_storages()
        await rag.ainsert(
            [row["context"] for row in contexts],
            ids=[row["document_id"] for row in contexts],
            file_paths=[f"inputs/{row['document_id']}.txt" for row in contexts],
        )
        ensure_documents_processed(store, (row["document_id"] for row in contexts))
        results_by_method: dict[str, list[dict[str, Any]]] = {}
        for method, mode in (("lightrag_hybrid", "hybrid"), ("lightrag_naive", "naive")):
            method_results = []
            for query_index, query in enumerate(queries):
                query_started = time.perf_counter()
                response = await rag.aquery(
                    query,
                    param=QueryParam(
                        mode=mode,
                        response_type="Multiple Paragraphs",
                        top_k=5,
                        chunk_top_k=5,
                        stream=False,
                        include_references=True,
                        user_prompt="Answer using only the retrieved context. State uncertainty when context is insufficient.",
                    ),
                )
                method_results.append(
                    {
                        "query_id": query_index,
                        "query": query,
                        "response": response,
                        "latency_seconds": time.perf_counter() - query_started,
                    }
                )
            results_by_method[method] = method_results
            (outputs / f"{method}_results.json").write_text(
                json.dumps(method_results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
    finally:
        await rag.finalize_storages()
    summary = {
        "experiment_id": root.name,
        "status": "completed",
        "run_kind": "LightRAG paper-protocol Qwen variant",
        "duration_seconds": time.perf_counter() - started,
        "input_manifest": "inputs/manifest.json",
        "lightrag": {
            "repository": "https://github.com/HKUDS/LightRAG",
            "revision": LIGHTRAG_REVISION,
            "retrieval_modes": ["hybrid", "naive"],
            "chunk_token_size": 512,
            "chunk_overlap_token_size": 64,
            "embedding": "deterministic-hash-128-v1",
        },
        "generation_llm": {
            "model_id": QWEN_MODEL_ROOT,
            "served_model_name": QWEN_MODEL,
            "serving_api": QWEN_ENDPOINT,
            "server_fingerprint": SERVER_FINGERPRINT,
            "temperature": 0,
            "max_tokens": {"extract": extract_max_tokens, "keyword": 512, "query": 768},
            "chat_template_kwargs": {"enable_thinking": False},
        },
        "query_count": len(queries),
        "indexed_context_count": len(contexts),
        "metrics": metrics.as_mapping(),
        "artifacts": {
            "lightrag_results": "outputs/lightrag_hybrid_results.json",
            "naive_results": "outputs/lightrag_naive_results.json",
            "lightrag_store": "outputs/lightrag-store",
            "log": "logs/run.log",
        },
    }
    (outputs / "run_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return summary


async def index_only(root: Path, extract_max_tokens: int, embedding_model: str = "hash") -> dict[str, Any]:
    """全量corpusをquery生成・検索なしでindex化する。"""
    contexts, _ = load_contexts_for_index(root)
    outputs = root / "outputs"
    store = outputs / "lightrag-store"
    if store.exists():
        raise FileExistsError(f"既存run outputを保護するため再利用しません: {store}")
    logger = configure_logger(root / "logs" / "index.log")
    metrics = RunMetrics()
    if embedding_model == "bge-m3":
        logger.info("BGE-M3をLightRAG worker開始前にprewarmします")
        await asyncio.to_thread(prewarm_bge_m3)
    rag = build_rag(store, metrics, logger, extract_max_tokens, embedding_model)
    try:
        await rag.initialize_storages()
        await rag.ainsert([row["context"] for row in contexts], ids=[row["document_id"] for row in contexts], file_paths=[f"inputs/{row['document_id']}.txt" for row in contexts])
        statuses = json.loads((store / "kv_store_doc_status.json").read_text(encoding="utf-8"))
    finally:
        await rag.finalize_storages()
    summary = {"experiment_id": root.name, "status": "completed", "run_kind": "index-only", "embedding_model": BGE_M3_MODEL if embedding_model == "bge-m3" else "deterministic-hash-128-v1", "indexed_context_count": len(contexts), "document_statuses": {key: value.get("status") for key, value in statuses.items()}, "metrics": metrics.as_mapping()}
    (outputs / "index_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def judge_token() -> str:
    """repo rootの.envからjudge用secretをプロセス内だけで取得する。"""
    token = dotenv_values(Path.cwd().parents[1] / ".env").get("OPENAI_API_TOKEN")
    if not token:
        raise RuntimeError("repo rootの.envにOPENAI_API_TOKENを設定してください")
    return token


def build_judge_requests(
    hybrid_results: list[dict[str, Any]], naive_results: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, dict[str, str]]]:
    """回答順を交互にして論文のpairwise judge batch requestを作る。"""
    if len(hybrid_results) != len(naive_results):
        raise ValueError("比較する回答数が一致しません")
    requests: list[dict[str, Any]] = []
    mappings: dict[str, dict[str, str]] = {}
    for index, (hybrid, naive) in enumerate(zip(hybrid_results, naive_results, strict=True)):
        custom_id = f"judge-{index:03d}"
        ordered = (
            ("lightrag_hybrid", hybrid["response"], "lightrag_naive", naive["response"])
            if index % 2 == 0
            else ("lightrag_naive", naive["response"], "lightrag_hybrid", hybrid["response"])
        )
        first_method, first_answer, second_method, second_answer = ordered
        mappings[custom_id] = {"answer_1": first_method, "answer_2": second_method}
        prompt = f"""You will evaluate two answers to the same question based on three criteria.

Question:
{hybrid["query"]}

Answer 1:
{first_answer}

Answer 2:
{second_answer}

Criteria:
- Comprehensiveness: coverage of relevant aspects and details.
- Diversity: variety and richness of useful perspectives and insights.
- Empowerment: usefulness for understanding the topic and making informed judgments.

Choose Answer 1, Answer 2, or Tie for each criterion and Overall. Return strict JSON only with this exact shape:
{{"Comprehensiveness": {{"Winner": "Answer 1|Answer 2|Tie", "Explanation": "..."}}, "Diversity": {{"Winner": "Answer 1|Answer 2|Tie", "Explanation": "..."}}, "Empowerment": {{"Winner": "Answer 1|Answer 2|Tie", "Explanation": "..."}}, "Overall Winner": {{"Winner": "Answer 1|Answer 2|Tie", "Explanation": "..."}}}}"""
        requests.append(
            {
                "custom_id": custom_id,
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": JUDGE_MODEL,
                    "temperature": 0,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an impartial expert evaluator. Evaluate only the supplied answers.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                },
            }
        )
    return requests, mappings


def submit_judge_batch(root: Path) -> str:
    """論文再現コードと同じOpenAI Batch APIでjudgeを投入する。"""
    outputs = root / "outputs"
    hybrid_results = json.loads((outputs / "lightrag_hybrid_results.json").read_text(encoding="utf-8"))
    naive_results = json.loads((outputs / "lightrag_naive_results.json").read_text(encoding="utf-8"))
    requests, mappings = build_judge_requests(hybrid_results, naive_results)
    input_path = outputs / "judge_batch_input.jsonl"
    input_path.write_text(
        "".join(json.dumps(request, ensure_ascii=False) + "\n" for request in requests), encoding="utf-8"
    )
    (outputs / "judge_answer_order.json").write_text(
        json.dumps(mappings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    client = OpenAI(api_key=judge_token())
    with input_path.open("rb") as source:
        input_file = client.files.create(file=source, purpose="batch")
    batch = client.batches.create(
        input_file_id=input_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"experiment_id": root.name, "purpose": "lightrag-paper-protocol-judge"},
    )
    metadata = {
        "judge_model": JUDGE_MODEL,
        "input_file_id": input_file.id,
        "batch_id": batch.id,
        "status": batch.status,
        "completion_window": "24h",
        "request_count": len(requests),
    }
    (outputs / "judge_batch.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return batch.id


def judge_with_prometheus(root: Path) -> dict[str, Any]:
    """Prometheus 2でpairwise judgeを実行し、LightRAG方式別勝率を集計する。"""
    outputs = root / "outputs"
    hybrid = json.loads((outputs / "lightrag_hybrid_results.json").read_text(encoding="utf-8"))
    naive = json.loads((outputs / "lightrag_naive_results.json").read_text(encoding="utf-8"))
    client = OpenAI(api_key="not-needed", base_url=PROMETHEUS_ENDPOINT, timeout=300)
    records: list[dict[str, Any]] = []
    for index, (left, right) in enumerate(zip(hybrid, naive, strict=True)):
        first, second = (left, right) if index % 2 == 0 else (right, left)
        prompt = f'''###Task Description:
An instruction, two responses, no reference answer, and an evaluation criteria are given.
Write detailed feedback comparing the responses, then output exactly [RESULT] A or [RESULT] B.

###Instruction:
{left["query"]}

###Response A:
{first["response"]}

###Response B:
{second["response"]}

###Reference Answer:
No reference answer is available. Judge only the supplied answers.

###Score Rubric:
Choose the answer that is more comprehensive, diverse, and empowering while remaining faithful to the retrieved context.

###Feedback:
'''
        response = client.chat.completions.create(
            model=PROMETHEUS_MODEL,
            temperature=0,
            max_tokens=1024,
            messages=[
                {"role": "system", "content": "You are a fair judge assistant assigned to compare two responses objectively."},
                {"role": "user", "content": prompt},
            ],
        )
        text = response.choices[0].message.content or ""
        match = re.search(r"\[RESULT\]\s*([AB])\b", text)
        if not match:
            raise RuntimeError(f"Prometheus 2の判定を解析できません: {text[-200:]}")
        selected = first if match.group(1) == "A" else second
        records.append({"query_id": index, "winner": "lightrag_hybrid" if selected is left else "lightrag_naive", "raw": text})
    wins = {method: sum(row["winner"] == method for row in records) for method in ("lightrag_hybrid", "lightrag_naive")}
    summary = {"experiment_id": root.name, "judge": {"model": PROMETHEUS_MODEL, "endpoint": PROMETHEUS_ENDPOINT, "pairwise_order": "alternating", "reference_answer": "unavailable"}, "query_count": len(records), "wins": wins, "win_rates": {key: value / len(records) for key, value in wins.items()}, "records": records}
    (outputs / "prometheus_judge_results.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def build_parser() -> argparse.ArgumentParser:
    """CLI parserを構築する。"""
    parser = argparse.ArgumentParser(description="LightRAG paper-protocol Qwen variant")
    parser.add_argument("--root", type=Path, required=True, help="experiment root path")
    parser.add_argument("--prepare-inputs", action="store_true", help="unique context subsetを保存する")
    parser.add_argument("--generate-queries", action="store_true", help="Qwenで高水準queryを生成する")
    parser.add_argument("--run", action="store_true", help="LightRAG hybrid/naiveを実行する")
    parser.add_argument("--index-only", action="store_true", help="query生成なしでLightRAG index化だけを実行する")
    parser.add_argument("--embedding-model", choices=("hash", "bge-m3"), default="hash")
    parser.add_argument("--submit-judge", action="store_true", help="GPT-4o-mini judge batchを投入する")
    parser.add_argument("--judge-prometheus", action="store_true", help="Prometheus 2でpairwise judgeを実行する")
    parser.add_argument(
        "--extract-max-tokens",
        type=int,
        default=DEFAULT_EXTRACT_MAX_TOKENS,
        help=f"entity/relation extraction roleのmax_tokens（既定: {DEFAULT_EXTRACT_MAX_TOKENS}）",
    )
    parser.add_argument(
        "--exclude-document-id",
        action="append",
        default=[],
        help="実装確認で除外するdocument ID（複数指定可）",
    )
    parser.add_argument(
        "--subset-context-count",
        type=int,
        default=SUBSET_CONTEXT_COUNT,
        help=f"実装確認用unique context数（既定: {SUBSET_CONTEXT_COUNT}）",
    )
    parser.add_argument(
        "--query-count", type=int, default=QUERY_COUNT, help=f"生成query数（既定: {QUERY_COUNT}）"
    )
    return parser


def main() -> None:
    """CLI entry point。"""
    args = build_parser().parse_args()
    if not any((args.prepare_inputs, args.generate_queries, args.run, args.index_only, args.submit_judge, args.judge_prometheus)):
        raise SystemExit("少なくとも1つの操作を指定してください")
    root = args.root.resolve()
    if args.prepare_inputs:
        if (root / "inputs" / "manifest.json").exists():
            raise SystemExit("既存input snapshotを保護するため再作成しません")
        manifest = prepare_inputs(root, args.subset_context_count, args.exclude_document_id)
        print(f"prepared {manifest['selection']['selected_unique_context_count']} contexts")
    if args.generate_queries:
        if (root / "inputs" / "generated_queries.json").exists():
            raise SystemExit("既存generated queryを保護するため再生成しません")
        questions = asyncio.run(generate_questions(root, args.query_count))
        print(f"generated {len(questions)} queries")
    if args.run:
        summary = asyncio.run(run_methods(root, args.extract_max_tokens))
        print(f"completed {summary['query_count']} queries per method")
    if args.index_only:
        summary = asyncio.run(index_only(root, args.extract_max_tokens, args.embedding_model))
        print(f"indexed {summary['indexed_context_count']} contexts")
    if args.submit_judge:
        print(f"submitted judge batch: {submit_judge_batch(root)}")
    if args.judge_prometheus:
        summary = judge_with_prometheus(root)
        print(json.dumps(summary["win_rates"], ensure_ascii=False))


if __name__ == "__main__":
    main()
