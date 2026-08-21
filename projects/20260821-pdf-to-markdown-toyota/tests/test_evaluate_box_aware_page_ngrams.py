import unittest

from pdf_to_markdown_toyota.interfaces.cli.evaluate_box_aware_page_ngrams import ngrams_from_units, score_page


class BoxAwareNgramTest(unittest.TestCase):
    def test_ngram_does_not_cross_text_units(self):
        self.assertEqual(ngrams_from_units(["abc", "def"], 2), {"ab", "bc", "de", "ef"})

    def test_numeric_token_and_cross_numeric_ngrams_are_excluded(self):
        self.assertEqual(ngrams_from_units(["ab12cd"], 2), {"ab", "cd"})

    def test_score_uses_block_aware_sets(self):
        result = score_page(["abc", "def"], ["abc", "xyz"])
        self.assertEqual(result["metrics"][1]["matched_ngram_count"], 2)
        self.assertAlmostEqual(result["metrics"][1]["output_page_ngram_match_rate"], 0.5, places=6)
        self.assertEqual(result["reference_numeric_token_count_excluded"], 0)


if __name__ == "__main__":
    unittest.main()
