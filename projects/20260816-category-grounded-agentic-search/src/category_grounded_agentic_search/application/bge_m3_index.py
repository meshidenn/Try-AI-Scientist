"""抽出済みLightRAG storeからBGE-M3 vector indexを作る。"""

from __future__ import annotations

import json
import shutil
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from nano_vectordb import NanoVectorDB

VECTOR_STORE_FILENAMES = (
    "vdb_chunks.json",
    "vdb_entities.json",
    "vdb_relationships.json",
)
STATIC_STORE_FILENAMES = (
    "graph_chunk_entity_relation.graphml",
    "kv_store_doc_status.json",
    "kv_store_entity_chunks.json",
    "kv_store_full_docs.json",
    "kv_store_full_entities.json",
    "kv_store_full_relations.json",
    "kv_store_llm_response_cache.json",
    "kv_store_relation_chunks.json",
    "kv_store_text_chunks.json",
)
VECTOR_METADATA_EXCLUSIONS = {"vector", "__created_at__", "__write_seq__"}

EmbeddingFunction = Callable[[Sequence[str]], np.ndarray]


@dataclass(frozen=True)
class BgeM3IndexSummary:
    """構築済みindexの件数を表す。"""

    embedding_dimension: int
    vector_counts: dict[str, int]


def _read_vector_records(path: Path) -> list[dict[str, Any]]:
    """既存vector storeから、再embeddingに必要なmetadataを読む。"""
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload.get("data")
    if not isinstance(records, list):
        raise ValueError(f"vector storeのdataが不正です: {path}")
    for record in records:
        if not isinstance(record, dict) or not record.get("__id__") or not record.get("content"):
            raise ValueError(f"vector store recordが不正です: {path}")
    return records


def _write_vector_store(
    source: Path,
    destination: Path,
    embedding: EmbeddingFunction,
    embedding_dimension: int,
    batch_size: int,
) -> int:
    """一つのNanoVectorDBをBGE-M3 dense vectorで再構築する。"""
    records = _read_vector_records(source)
    database = NanoVectorDB(embedding_dim=embedding_dimension, storage_file=str(destination))
    for offset in range(0, len(records), batch_size):
        batch = records[offset : offset + batch_size]
        vectors = np.asarray(embedding([str(record["content"]) for record in batch]), dtype=np.float32)
        if vectors.shape != (len(batch), embedding_dimension):
            raise ValueError(
                "embeddingのshapeが不正です: "
                f"expected={(len(batch), embedding_dimension)}, actual={vectors.shape}"
            )
        database.upsert(
            [
                {
                    key: value
                    for key, value in record.items()
                    if key not in VECTOR_METADATA_EXCLUSIONS
                }
                | {"__vector__": vector}
                for record, vector in zip(batch, vectors, strict=True)
            ]
        )
    database.save()
    return len(records)


def build_bge_m3_index(
    source_store: Path,
    destination_store: Path,
    embedding: EmbeddingFunction,
    *,
    embedding_dimension: int,
    batch_size: int,
) -> BgeM3IndexSummary:
    """Qwenを再実行せず、抽出済みstoreのvector部分だけを置き換える。"""
    if destination_store.exists():
        raise FileExistsError(f"既存indexを保護するため再利用しません: {destination_store}")
    if batch_size <= 0:
        raise ValueError("batch_sizeは1以上にしてください")
    for filename in STATIC_STORE_FILENAMES + VECTOR_STORE_FILENAMES:
        if not (source_store / filename).is_file():
            raise FileNotFoundError(f"LightRAG storeの必須artifactがありません: {source_store / filename}")

    destination_store.mkdir(parents=True)
    for filename in STATIC_STORE_FILENAMES:
        shutil.copy2(source_store / filename, destination_store / filename)

    vector_counts = {
        filename.removeprefix("vdb_").removesuffix(".json"): _write_vector_store(
            source_store / filename,
            destination_store / filename,
            embedding,
            embedding_dimension,
            batch_size,
        )
        for filename in VECTOR_STORE_FILENAMES
    }
    return BgeM3IndexSummary(
        embedding_dimension=embedding_dimension,
        vector_counts=vector_counts,
    )
