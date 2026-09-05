import unittest

from category_grounded_agentic_search.domain.experiment import (
    CorpusManifest,
    ManifestValidationError,
    RetrievalBudgetLedger,
)


class CorpusManifestTest(unittest.TestCase):
    def test_requires_reproducibility_fields(self) -> None:
        with self.assertRaises(ManifestValidationError):
            CorpusManifest.from_mapping({"corpus_id": "fixture"})


class RetrievalBudgetLedgerTest(unittest.TestCase):
    def test_counts_duplicate_slots_against_budget(self) -> None:
        ledger = RetrievalBudgetLedger(limit=4)
        ledger.record("first query", ["p-1", "p-2"])
        ledger.record("second query", ["p-2", "p-3"])

        self.assertEqual(ledger.returned_passage_slot_count, 4)
        self.assertEqual(ledger.observed_unique_passage_count, 3)
        self.assertEqual(ledger.duplicate_retrieval_rate, 0.25)

    def test_rejects_budget_overrun(self) -> None:
        ledger = RetrievalBudgetLedger(limit=2)
        ledger.record("first query", ["p-1", "p-2"])

        with self.assertRaises(ValueError):
            ledger.record("second query", ["p-3"])
