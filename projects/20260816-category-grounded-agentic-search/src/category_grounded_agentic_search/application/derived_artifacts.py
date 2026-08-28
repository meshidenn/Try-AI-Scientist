"""Corpus由来の再利用可能なtriplet・embedding・index artifactを管理する。"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


def safe_identifier(value: str) -> str:
    """model IDやrevisionをfilesystemで安全な識別子へ変換する。"""
    return value.replace("/", "--").replace("@", "--").replace(" ", "-")


def sha256_file(path: Path) -> str:
    """artifactの内容hashを計算する。"""
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


@dataclass(frozen=True)
class DerivedArtifactPaths:
    """一つのcorpus revisionに対する派生artifactの正規path。"""

    root: Path
    corpus_id: str
    corpus_revision: str
    extractor_model: str
    embedding_model: str

    @property
    def corpus_key(self) -> str:
        return f"{safe_identifier(self.corpus_id)}--{safe_identifier(self.corpus_revision)}"

    @property
    def triplet_dir(self) -> Path:
        return self.root / "triplets" / self.corpus_key / safe_identifier(self.extractor_model)

    @property
    def embedding_dir(self) -> Path:
        return self.root / "embeddings" / self.corpus_key / safe_identifier(self.embedding_model)

    @property
    def index_dir(self) -> Path:
        pair = f"{safe_identifier(self.extractor_model)}__{safe_identifier(self.embedding_model)}"
        return self.root / "indexes" / self.corpus_key / pair

    def initialize(self) -> None:
        """派生データ用directoryを作成する。"""
        for path in (self.triplet_dir, self.embedding_dir, self.index_dir):
            path.mkdir(parents=True, exist_ok=True)

    def write_manifest(self, stage: str, *, inputs: dict[str, Any], outputs: dict[str, Any]) -> Path:
        """段階ごとの入出力・依存関係をmanifestとして保存する。"""
        directories = {"triplets": self.triplet_dir, "embeddings": self.embedding_dir, "index": self.index_dir}
        if stage not in directories:
            raise ValueError(f"未知のstageです: {stage}")
        manifest = {
            "schema_version": 1,
            "stage": stage,
            "artifact_paths": {key: str(value) for key, value in asdict(self).items()},
            "corpus": {"id": self.corpus_id, "revision": self.corpus_revision},
            "models": {"extractor": self.extractor_model, "embedding": self.embedding_model},
            "inputs": inputs,
            "outputs": outputs,
        }
        path = directories[stage] / "manifest.json"
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path
