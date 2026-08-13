import unittest

from render_box_aware_ngram_html import missing_ngrams, render_unit


class BoxAwareNgramHtmlTest(unittest.TestCase):
    def test_missing_ngrams_do_not_cross_units(self):
        self.assertEqual(missing_ngrams(["abc", "def"], ["abc"], 2), ["de", "ef"])

    def test_numbers_are_shown_as_excluded(self):
        rendered = render_unit("売上12百万円", 2, {"売上", "百万円"}, "match", "unmatched")
        self.assertIn("excluded-number", rendered)
        self.assertIn("12", rendered)


if __name__ == "__main__":
    unittest.main()
