"""抽出済みstoreを再利用するBGE-M3 index builderのテスト。"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from category_grounded_agentic_search.application.bge_m3_index import build_bge_m3_index


class BgeM3IndexTest(unittest.TestCase):
    """Qwen抽出を再実行せずにvector storeを再構築できることを確認する。"""

    def test_rebuilds_all_vector_stores_and_copies_graph_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "source"
            source.mkdir()
            for filename in (
                "graph_chunk_entity_relation.graphml",
                "kv_store_doc_status.json",
                "kv_store_entity_chunks.json",
                "kv_store_full_docs.json",
                "kv_store_full_entities.json",
                "kv_store_full_relations.json",
                "kv_store_llm_response_cache.json",
                "kv_store_relation_chunks.json",
                "kv_store_text_chunks.json",
            ):
                (source / filename).write_text("{}", encoding="utf-8")
            for filename in ("vdb_chunks.json", "vdb_entities.json", "vdb_relationships.json"):
                (source / filename).write_text(
                    json.dumps(
                        {
                            "embedding_dim": 2,
                            "data": [
                                {
                                    "__id__": f"{filename}-id",
                                    "content": f"{filename} content",
                                    "vector": "old-vector",
                                    "__created_at__": 1,
                                }
                            ],
                            "matrix": "old-matrix",
                        }
                    ),
                    encoding="utf-8",
                )

            summary = build_bge_m3_index(
                source,
                root / "destination",
                lambda texts: np.asarray([[0.6, 0.8] for _ in texts], dtype=np.float32),
                embedding_dimension=2,
                batch_size=1,
            )

            self.assertEqual(summary.embedding_dimension, 2)
            self.assertEqual(summary.vector_counts, {"chunks": 1, "entities": 1, "relationships": 1})
            self.assertEqual((root / "destination" / "graph_chunk_entity_relation.graphml").read_text(), "{}")
            chunks = json.loads((root / "destination" / "vdb_chunks.json").read_text(encoding="utf-8"))
            self.assertEqual(chunks["embedding_dim"], 2)
            self.assertEqual(len(chunks["data"]), 1)
            self.assertNotEqual(chunks["data"][0].get("vector"), "old-vector")

    def test_protects_existing_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            destination = root / "destination"
            destination.mkdir()
            with self.assertRaises(FileExistsError):
                build_bge_m3_index(
                    root / "source",
                    destination,
                    lambda texts: np.zeros((len(texts), 2), dtype=np.float32),
                    embedding_dimension=2,
                    batch_size=1,
                )
