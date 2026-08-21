import unittest

from pdf_to_markdown_toyota.interfaces.cli.run_chunked_hybrid import split_vertical_regions


class ChunkedHybridTest(unittest.TestCase):
    def test_splits_on_large_vertical_gap_and_drops_footer(self) -> None:
        blocks = [
            {"bbox": [0, 10, 100, 20], "text": "a" * 30},
            {"bbox": [0, 25, 100, 35], "text": "b" * 30},
            {"bbox": [0, 70, 100, 80], "text": "c" * 60},
            {"bbox": [0, 200, 100, 210], "text": "footer"},
        ]
        regions = split_vertical_regions(blocks, min_gap=20, min_text_chars=50)
        self.assertEqual(len(regions), 2)
        self.assertEqual(regions[0][0]["text"], "a" * 30)
        self.assertEqual(regions[1][0]["text"], "c" * 60)


if __name__ == "__main__":
    unittest.main()
