import json
import tempfile
import unittest
from pathlib import Path

from pdf_to_markdown_toyota.interfaces.cli.run_general_vlm import bounded_payload, is_completed_record, load_pages, load_source_pdf_dir, messages_for, require_local_base_url


class RunGeneralVlmTest(unittest.TestCase):
    def test_local_endpoint_only(self) -> None:
        require_local_base_url("http://127.0.0.1:18021/v1")
        with self.assertRaises(ValueError):
            require_local_base_url("https://api.example.com/v1")

    def test_source_directory_is_resolved_from_input_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "exp-004"
            source = Path(temporary) / "pdfs"
            (root / "inputs").mkdir(parents=True)
            source.mkdir()
            (root / "inputs" / "source-manifest.json").write_text(
                json.dumps({"source_pdf_directory": "../../pdfs"}), encoding="utf-8"
            )
            self.assertEqual(load_source_pdf_dir(root), source.resolve())

    def test_pilot_pages_are_loaded_per_document(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "inputs").mkdir()
            (root / "inputs" / "pilot-pages.json").write_text(
                json.dumps({"securities_report": [135], "integrated_report": [11]}), encoding="utf-8"
            )
            pages = load_pages(root, pilot=True)
            self.assertEqual(pages["securities_report"], [135])
            self.assertEqual(pages["integrated_report"], [11])
            self.assertEqual(pages["earnings_presentation"], [])

    def test_completed_record_requires_nonempty_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output_path = Path(temporary) / "page.md"
            output_path.write_text("# output\n", encoding="utf-8")
            self.assertTrue(is_completed_record({"status": "success", "output_path": str(output_path)}))
            output_path.write_text("", encoding="utf-8")
            self.assertFalse(is_completed_record({"status": "success", "output_path": str(output_path)}))

    def test_payload_is_truncated_with_a_marker(self) -> None:
        self.assertEqual(bounded_payload("abc", 3), "abc")
        self.assertIn("コンテキスト上限", bounded_payload("abcdef", 3))

    def test_native_ocr_uses_model_specific_instruction(self) -> None:
        messages = messages_for("native_ocr", 1, "", "file:///tmp/page.png", "Document parsing.")
        self.assertEqual(messages[0]["content"][0]["text"], "Document parsing.")
        with self.assertRaises(ValueError):
            messages_for("native_ocr", 1, "", "file:///tmp/page.png")


if __name__ == "__main__":
    unittest.main()
