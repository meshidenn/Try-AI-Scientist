"""JSON で保存された corpus manifest を読み込む adapter。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from category_grounded_agentic_search.domain.experiment import CorpusManifest


def load_corpus_manifest(path: Path) -> CorpusManifest:
    """JSON manifest を読み、必須項目を検証した値オブジェクトを返す。"""
    with path.open(encoding="utf-8") as file:
        value: Any = json.load(file)
    if not isinstance(value, dict):
        raise ValueError("corpus manifest の最上位要素は object である必要があります")
    return CorpusManifest.from_mapping(value)
