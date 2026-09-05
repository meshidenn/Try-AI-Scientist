"""実験開始前の manifest 検証用 CLI。"""

from __future__ import annotations

import argparse
from pathlib import Path

from category_grounded_agentic_search.infrastructure.json_manifest import load_corpus_manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Category-Grounded Agentic Search の補助 CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate-manifest", help="corpus manifest を検証する")
    validate.add_argument("path", type=Path)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "validate-manifest":
        manifest = load_corpus_manifest(args.path)
        print(
            "manifest is valid: "
            f"{manifest.corpus_id} ({manifest.corpus_version}, {manifest.snapshot_date})"
        )


if __name__ == "__main__":
    main()
