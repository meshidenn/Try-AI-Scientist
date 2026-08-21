import unittest

from pdf_to_markdown_toyota.interfaces.cli.evaluate_ensemble_confidence import numeric_candidates, page_summary


class EvaluateEnsembleConfidenceTest(unittest.TestCase):
    def test_three_models_and_pdf_evidence_are_high_confidence(self) -> None:
        candidates = numeric_candidates(
            {"gemma": "売上 1,000", "qwen": "売上1000", "glm": "1000"},
            {"1000"},
        )
        self.assertEqual(candidates[0]["supporting_models"], ["gemma", "glm", "qwen"])
        self.assertEqual(candidates[0]["label"], "high")
        self.assertEqual(candidates[0]["confidence"], 1.0)

    def test_single_model_value_without_pdf_evidence_is_low_confidence(self) -> None:
        candidates = numeric_candidates(
            {"gemma": "1000", "qwen": "2000", "glm": "2000"},
            {"2000"},
        )
        candidate = next(item for item in candidates if item["value"] == "1000")
        self.assertEqual(candidate["label"], "low")
        self.assertFalse(candidate["pdf_text_evidence"])

    def test_page_summary_penalizes_missing_reference_numbers(self) -> None:
        candidates = numeric_candidates({"a": "100", "b": "100"}, {"100", "200"})
        summary = page_summary(candidates, {"100", "200"})
        self.assertEqual(summary["pdf_numeric_coverage"], 0.5)
        self.assertEqual(summary["coverage_adjusted_confidence"], 0.5)


if __name__ == "__main__":
    unittest.main()
