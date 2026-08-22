"""実験の再現性と予算公平性を保つためのドメインモデル。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


class ManifestValidationError(ValueError):
    """再現に必要な corpus manifest の情報が欠けている場合の例外。"""


@dataclass(frozen=True)
class CorpusManifest:
    """比較条件が共有する corpus の来歴を表す。"""

    corpus_id: str
    corpus_version: str
    snapshot_date: str
    document_unit: str
    document_to_passage_mapping: str
    preprocessing: str
    splits: Mapping[str, str]

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "CorpusManifest":
        required_fields = (
            "corpus_id",
            "corpus_version",
            "snapshot_date",
            "document_unit",
            "document_to_passage_mapping",
            "preprocessing",
            "splits",
        )
        missing = [name for name in required_fields if not value.get(name)]
        if missing:
            raise ManifestValidationError(
                f"corpus manifest に必須項目がありません: {', '.join(missing)}"
            )

        splits = value["splits"]
        if not isinstance(splits, Mapping) or not all(
            isinstance(name, str) and isinstance(path, str) and path
            for name, path in splits.items()
        ):
            raise ManifestValidationError("splits は split 名から入力 path への対応である必要があります")

        return cls(
            corpus_id=str(value["corpus_id"]),
            corpus_version=str(value["corpus_version"]),
            snapshot_date=str(value["snapshot_date"]),
            document_unit=str(value["document_unit"]),
            document_to_passage_mapping=str(value["document_to_passage_mapping"]),
            preprocessing=str(value["preprocessing"]),
            splits=dict(splits),
        )

    def as_mapping(self) -> dict[str, Any]:
        return {
            "corpus_id": self.corpus_id,
            "corpus_version": self.corpus_version,
            "snapshot_date": self.snapshot_date,
            "document_unit": self.document_unit,
            "document_to_passage_mapping": self.document_to_passage_mapping,
            "preprocessing": self.preprocessing,
            "splits": dict(self.splits),
        }


@dataclass(frozen=True)
class RetrievalTurn:
    """一回の検索 API 呼び出しで返却された passage slot を保存する。"""

    turn: int
    query: str
    returned_passage_ids: tuple[str, ...]


@dataclass
class RetrievalBudgetLedger:
    """cumulative top-N と、重複を含む返却 slot 数を監査する。"""

    limit: int
    turns: list[RetrievalTurn] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.limit < 0:
            raise ValueError("cumulative top-N は 0 以上である必要があります")

    @property
    def returned_passage_slot_count(self) -> int:
        return sum(len(turn.returned_passage_ids) for turn in self.turns)

    @property
    def observed_unique_passage_count(self) -> int:
        return len({passage_id for turn in self.turns for passage_id in turn.returned_passage_ids})

    @property
    def duplicate_retrieval_rate(self) -> float:
        slots = self.returned_passage_slot_count
        if slots == 0:
            return 0.0
        return 1 - (self.observed_unique_passage_count / slots)

    def record(self, query: str, returned_passage_ids: Sequence[str]) -> RetrievalTurn:
        if not query.strip():
            raise ValueError("検索 query は空にできません")
        if any(not passage_id.strip() for passage_id in returned_passage_ids):
            raise ValueError("passage ID は空にできません")
        next_slots = self.returned_passage_slot_count + len(returned_passage_ids)
        if next_slots > self.limit:
            raise ValueError(
                f"cumulative top-N を超過します: {next_slots} > {self.limit}"
            )

        turn = RetrievalTurn(
            turn=len(self.turns) + 1,
            query=query,
            returned_passage_ids=tuple(returned_passage_ids),
        )
        self.turns.append(turn)
        return turn
