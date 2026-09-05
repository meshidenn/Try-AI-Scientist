"""gold evidence に対する retrieval 評価を行う。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class RetrievalMetrics:
    """query 単位で記録する最小の retrieval 指標群。"""

    recall_at_k: float
    all_evidence_recall_at_k: float
    reciprocal_rank: float


def evaluate_retrieval(
    ranked_passage_ids: Sequence[str], gold_evidence_ids: set[str], k: int
) -> RetrievalMetrics:
    """順位付き passage と gold evidence の一致を評価する。"""
    if k <= 0:
        raise ValueError("k は 1 以上である必要があります")
    if not gold_evidence_ids:
        raise ValueError("gold evidence は少なくとも一件必要です")

    top_k = ranked_passage_ids[:k]
    found = set(top_k) & gold_evidence_ids
    recall = len(found) / len(gold_evidence_ids)
    all_evidence_recall = float(gold_evidence_ids.issubset(set(top_k)))
    reciprocal_rank = 0.0
    for rank, passage_id in enumerate(ranked_passage_ids, start=1):
        if passage_id in gold_evidence_ids:
            reciprocal_rank = 1 / rank
            break

    return RetrievalMetrics(
        recall_at_k=recall,
        all_evidence_recall_at_k=all_evidence_recall,
        reciprocal_rank=reciprocal_rank,
    )
