import tempfile
import unittest
from pathlib import Path

import fitz

from pdf_to_markdown_toyota.interfaces.cli.run_experiment import normalize_markdown, page_text, parse_first_payload, select_pages


class RunExperimentTest(unittest.TestCase):
    def test_page_text_and_payload_keep_page_content(self) -> None:
        document = fitz.open()
        page = document.new_page()
        page.insert_text((72, 72), "Revenue 1,234")
        self.assertIn("Revenue", page_text(page))
        payload = parse_first_payload(page)
        self.assertIn("1,234", payload)
        self.assertIn("page_number", payload)

    def test_select_pages_is_bounded_and_sorted(self) -> None:
        document = fitz.open()
        for index in range(5):
            page = document.new_page()
            page.insert_text((72, 72), f"page {index} " + ("123 " * (index + 1)))
        selected = select_pages(document, 3)
        self.assertEqual(len(selected), 3)
        self.assertEqual(selected, sorted(selected))
        self.assertIn(0, selected)

    def test_normalize_markdown_removes_fence_only(self) -> None:
        self.assertEqual(normalize_markdown("```markdown\n# 見出し\n```"), "# 見出し\n")

    def test_normalize_markdown_removes_glm_box_tokens(self) -> None:
        self.assertEqual(normalize_markdown("<|begin_of_box|># 見出し<|end_of_box|>"), "# 見出し\n")


if __name__ == "__main__":
    unittest.main()
