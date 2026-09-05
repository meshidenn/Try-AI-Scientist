import unittest

from category_grounded_agentic_search.application.evaluation import evaluate_retrieval


class EvaluateRetrievalTest(unittest.TestCase):
    def test_records_partial_and_complete_evidence_coverage(self) -> None:
        metrics = evaluate_retrieval(
            ranked_passage_ids=["p-2", "p-1", "p-3"],
            gold_evidence_ids={"p-1", "p-3"},
            k=2,
        )

        self.assertEqual(metrics.recall_at_k, 0.5)
        self.assertEqual(metrics.all_evidence_recall_at_k, 0.0)
        self.assertEqual(metrics.reciprocal_rank, 0.5)

    def test_rejects_empty_gold_evidence(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_retrieval(["p-1"], set(), k=1)
