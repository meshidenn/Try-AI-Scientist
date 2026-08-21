import unittest

from pdf_to_markdown_toyota.interfaces.cli.evaluate_model_comparison import aggregate


class EvaluateModelComparisonTest(unittest.TestCase):
    def test_aggregate_keeps_models_separate(self) -> None:
        records = [
            {"model": "model-a", "method": "hybrid", "wall_time_seconds": 1.0, "metrics": {"status": "success", "numeric_token_recall": 0.5, "numeric_token_precision": 1.0, "numeric_token_f1": 0.667, "text_normalized_similarity_proxy": 0.8, "table_row_width_consistent": True}},
            {"model": "model-b", "method": "hybrid", "wall_time_seconds": 2.0, "metrics": {"status": "success", "numeric_token_recall": 1.0, "numeric_token_precision": 0.5, "numeric_token_f1": 0.667, "text_normalized_similarity_proxy": 0.7, "table_row_width_consistent": False}},
        ]
        rows = aggregate(records)
        self.assertEqual([row["model"] for row in rows], ["model-a", "model-b"])
        self.assertEqual(rows[0]["numeric_token_recall"], 0.5)
        self.assertEqual(rows[1]["consistent_table_pages"], 0)


if __name__ == "__main__":
    unittest.main()
