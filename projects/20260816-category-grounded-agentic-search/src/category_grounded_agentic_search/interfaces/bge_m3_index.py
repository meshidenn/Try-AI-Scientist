"""抽出済みtripletからBGE-M3 LightRAG indexを作るCLI。"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from category_grounded_agentic_search.application.bge_m3_index import build_bge_m3_index
from category_grounded_agentic_search.application.derived_artifacts import (
    DerivedArtifactPaths,
    sha256_file,
)
from category_grounded_agentic_search.infrastructure.bge_m3_embedding import (
    EMBEDDING_DIMENSION,
    MODEL_ID,
    bge_m3_embed,
    prewarm_bge_m3,
)


def build_parser() -> argparse.ArgumentParser:
    """CLI parserを作る。"""
    parser = argparse.ArgumentParser(description="BGE-M3によるLightRAG vector index構築")
    parser.add_argument("--derived-root", type=Path, required=True)
    parser.add_argument("--corpus-id", required=True)
    parser.add_argument("--corpus-revision", required=True)
    parser.add_argument("--extractor-model", required=True)
    parser.add_argument("--source-store", type=Path, required=True)
    parser.add_argument("--triplets-jsonl", type=Path, required=True)
    parser.add_argument("--batch-size", type=int, default=32)
    return parser


async def run(args: argparse.Namespace) -> dict[str, object]:
    """GPU上でBGE-M3 embeddingとLightRAG vector indexを確定する。"""
    paths = DerivedArtifactPaths(
        root=args.derived_root.resolve(),
        corpus_id=args.corpus_id,
        corpus_revision=args.corpus_revision,
        extractor_model=args.extractor_model,
        embedding_model=MODEL_ID,
    )
    paths.initialize()
    destination_store = paths.index_dir / "lightrag-store"
    await asyncio.to_thread(prewarm_bge_m3)
    summary = await asyncio.to_thread(
        build_bge_m3_index,
        args.source_store.resolve(),
        destination_store,
        lambda texts: asyncio.run(bge_m3_embed(texts)),
        embedding_dimension=EMBEDDING_DIMENSION,
        batch_size=args.batch_size,
    )
    output = {
        "embedding_model": MODEL_ID,
        "embedding_dimension": summary.embedding_dimension,
        "vector_counts": summary.vector_counts,
        "source_store": str(args.source_store.resolve()),
        "triplets_jsonl": str(args.triplets_jsonl.resolve()),
        "triplets_sha256": sha256_file(args.triplets_jsonl.resolve()),
        "lightrag_store": str(destination_store),
    }
    paths.write_manifest(
        "index",
        inputs={
            "source_lightrag_store": output["source_store"],
            "triplets_jsonl": output["triplets_jsonl"],
            "triplets_sha256": output["triplets_sha256"],
        },
        outputs=output,
    )
    return output


def main() -> None:
    """entry point。"""
    args = build_parser().parse_args()
    if args.batch_size <= 0:
        raise ValueError("--batch-sizeは1以上にしてください")
    print(json.dumps(asyncio.run(run(args)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
