"""外部embedding endpointを使わない、再現可能なpilot用embedding。"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence

import numpy as np


TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+")


async def hash_embed(texts: Sequence[str], dimensions: int = 128) -> np.ndarray:
    """固定hashing trickで正規化済みのdense vectorを返す。

    Qwen endpointはchat completionだけを提供しembedding endpointを持たない。
    この関数は小規模な疎通pilotのindex/queryを可能にするための固定adapterであり、
    研究上のembedding model比較には使用しない。
    """
    vectors = np.zeros((len(texts), dimensions), dtype=np.float32)
    for row, text in enumerate(texts):
        for token in TOKEN_PATTERN.findall(text.lower()):
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            value = int.from_bytes(digest, byteorder="big")
            column = value % dimensions
            vectors[row, column] += 1.0 if (value >> 63) == 0 else -1.0
        norm = np.linalg.norm(vectors[row])
        if norm:
            vectors[row] /= norm
    return vectors
