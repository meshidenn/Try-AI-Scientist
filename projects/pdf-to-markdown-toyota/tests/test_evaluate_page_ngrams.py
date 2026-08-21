import unittest

from pdf_to_markdown_toyota.interfaces.cli.evaluate_page_ngrams import character_ngrams, normalize_for_ngrams, score_page


class PageNgramTest(unittest.TestCase):
    def test_markdown_syntax_is_not_compared_as_text(self):
        self.assertEqual(normalize_for_ngrams("# 売上高\n| A | B |\n| --- | --- |\n| 10 | 20 |"), "売上高AB1020")

    def test_character_ngrams_are_unique(self):
        self.assertEqual(character_ngrams("あああ", 2), {"ああ"})

    def test_page_match_and_reference_coverage(self):
        result = score_page("abcdef", "abcXYZ")
        n3 = result["metrics"][2]
        self.assertEqual(n3["matched_ngram_count"], 1)
        self.assertAlmostEqual(n3["output_page_ngram_match_rate"], 1 / 4, places=6)
        self.assertAlmostEqual(n3["reference_page_ngram_coverage"], 1 / 4, places=6)


if __name__ == "__main__":
    unittest.main()
