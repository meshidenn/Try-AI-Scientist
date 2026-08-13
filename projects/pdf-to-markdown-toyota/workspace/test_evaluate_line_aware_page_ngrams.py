import unittest

import fitz

from evaluate_line_aware_page_ngrams import pdf_text_lines


class LineAwareNgramTest(unittest.TestCase):
    def test_pdf_lines_are_kept_as_separate_units(self):
        document = fitz.open()
        page = document.new_page()
        page.insert_text((50, 50), "Japan")
        page.insert_text((150, 50), "NorthAmerica")
        lines = pdf_text_lines(page)
        self.assertEqual(lines, ["Japan", "NorthAmerica"])


if __name__ == "__main__":
    unittest.main()
