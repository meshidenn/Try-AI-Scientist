"""再利用可能な派生データdirectoryを初期化するCLI。"""

from __future__ import annotations

import argparse
from pathlib import Path

from category_grounded_agentic_search.application.derived_artifacts import DerivedArtifactPaths


def build_parser() -> argparse.ArgumentParser:
    """CLI parserを作る。"""
    parser = argparse.ArgumentParser(description="derived artifact layout initializer")
    parser.add_argument("--root", type=Path, required=True, help="data/derived directory")
    parser.add_argument("--corpus-id", required=True)
    parser.add_argument("--corpus-revision", required=True)
    parser.add_argument("--extractor-model", required=True)
    parser.add_argument("--embedding-model", required=True)
    return parser


def main() -> None:
    """entry point。"""
    args = build_parser().parse_args()
    paths = DerivedArtifactPaths(
        root=args.root.resolve(),
        corpus_id=args.corpus_id,
        corpus_revision=args.corpus_revision,
        extractor_model=args.extractor_model,
        embedding_model=args.embedding_model,
    )
    paths.initialize()
    for stage in ("triplets", "embeddings", "index"):
        paths.write_manifest(stage, inputs={}, outputs={"status": "not_started"})
    print(paths.index_dir)


if __name__ == "__main__":
    main()
