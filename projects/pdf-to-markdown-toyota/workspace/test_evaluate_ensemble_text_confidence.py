import unittest
from evaluate_ensemble_text_confidence import text_candidates

class TextConfidenceTest(unittest.TestCase):
    def test_heading_formatting_is_clustered(self):
        candidates = text_candidates({"gemma": "# 連結売上高", "qwen": "連結売上高", "glm": "## 連結売上高"}, "連結売上高\n")
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["supporting_models"], ["gemma", "glm", "qwen"])
        self.assertEqual(candidates[0]["label"], "high")
    def test_single_model_text_is_low(self):
        candidates = text_candidates({"gemma": "地域別販売台数", "qwen": "別の本文", "glm": "別の本文"}, "地域別販売台数\n別の本文\n")
        candidate = next(item for item in candidates if item["value"] == "地域別販売台数")
        self.assertEqual(candidate["label"], "low")

if __name__ == "__main__":
    unittest.main()
