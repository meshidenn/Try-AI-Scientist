import unittest

from render_confidence_colored_html import number_labels, render_markdown, text_label


class ConfidenceColoredHtmlTest(unittest.TestCase):
    def test_render_markdown_renders_table_and_numeric_label(self):
        rendered = render_markdown(
            "| 項目 | 100 |\n| --- | ---: |\n| 売上 | 200 |",
            [],
            "gemma4-26b-moe",
            {"100": "high", "200": "medium"},
        )
        self.assertIn("<table>", rendered)
        self.assertIn('class="confidence-high"', rendered)
        self.assertIn('class="confidence-medium"', rendered)

    def test_text_label_only_marks_supporting_model(self):
        candidates = [{"kind": "text_line", "value": "収益性を向上", "supporting_models": ["gemma4-26b-moe"], "label": "high"}]
        self.assertEqual(text_label("収益性を向上", "text_line", candidates, "gemma4-26b-moe"), "high")
        self.assertIsNone(text_label("収益性を向上", "text_line", candidates, "qwen3.6-27b"))

    def test_number_labels_excludes_other_model_candidates(self):
        candidates = [{"value": "1,000", "label": "high", "supporting_models": ["glm-4.6v-flash"]}]
        self.assertEqual(number_labels(candidates, "glm-4.6v-flash"), {"1000": "high"})
        self.assertEqual(number_labels(candidates, "gemma4-26b-moe"), {})
