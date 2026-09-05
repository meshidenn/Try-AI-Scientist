"""BAAI/bge-m3を用いるLightRAG用embedding adapter。"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence

import numpy as np

MODEL_ID = "BAAI/bge-m3"
EMBEDDING_DIMENSION = 1024
_model = None


def _load_model():
    """初回呼出し時だけmodel weightを取得・ロードする。"""
    global _model
    if _model is None:
        import torch
        from sentence_transformers import SentenceTransformer

        device = "cuda" if torch.cuda.is_available() else "cpu"
        _model = SentenceTransformer(MODEL_ID, device=device)
    return _model


def _encode(texts: Sequence[str]) -> np.ndarray:
    """正規化済みdense embeddingを同期的に生成する。"""
    return np.asarray(_load_model().encode(list(texts), normalize_embeddings=True), dtype=np.float32)


async def bge_m3_embed(texts: Sequence[str]) -> np.ndarray:
    """LightRAGが要求する非同期embedding interfaceを提供する。"""
    return await asyncio.to_thread(_encode, texts)


def prewarm_bge_m3() -> None:
    """LightRAG worker開始前にweightをloadし、初回timeoutを避ける。"""
    _load_model()
