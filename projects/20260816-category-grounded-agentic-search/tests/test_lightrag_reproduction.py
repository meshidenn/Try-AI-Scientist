import json
import tempfile
import unittest
from pathlib import Path

from category_grounded_agentic_search.interfaces.lightrag_reproduction import (
    build_parser,
    build_judge_requests,
    completion_failure_reason,
    completion_timeout_seconds,
    ensure_documents_processed,
    official_context_description,
    official_question_prompt,
    parse_pairwise_winner,
    parse_questions,
    repetition_analysis,
    unique_contexts,
)


class InputPreparationTest(unittest.TestCase):
    def test_deduplicates_contexts_in_sha_order(self) -> None:
        contexts = unique_contexts(
            [{"context": "same"}, {"context": "other"}, {"context": "same"}, {"context": ""}]
        )

        self.assertEqual(len(contexts), 2)
        self.assertEqual([row["context"] for row in contexts], ["same", "other"])

    def test_parses_numbered_questions(self) -> None:
        questions = parse_questions("1. What is A?\n2. What is B?", expected_count=2)

        self.assertEqual(questions, ["What is A?", "What is B?"])

    def test_builds_official_question_prompt(self) -> None:
        prompt = official_question_prompt("dataset description")

        self.assertIn("identify 5 potential users", prompt)
        self.assertIn("generate 5 questions", prompt)

    def test_official_context_description_uses_official_slice(self) -> None:
        class Tokenizer:
            def tokenize(self, _: str) -> list[str]:
                return [str(index) for index in range(2_500)]

            def convert_tokens_to_string(self, tokens: list[str]) -> str:
                return ",".join(tokens)

        description = official_context_description("context", Tokenizer())

        self.assertTrue(description.startswith("1000,1001"))
        self.assertTrue(description.endswith("998,999"))


class JudgeRequestTest(unittest.TestCase):
    def test_alternates_answer_order(self) -> None:
        hybrid = [
            {"query": "q1", "response": "hybrid 1"},
            {"query": "q2", "response": "hybrid 2"},
        ]
        naive = [
            {"query": "q1", "response": "naive 1"},
            {"query": "q2", "response": "naive 2"},
        ]

        requests, mappings = build_judge_requests(hybrid, naive)

        self.assertEqual(len(requests), 2)
        self.assertEqual(mappings["judge-000"]["answer_1"], "lightrag_hybrid")
        self.assertEqual(mappings["judge-001"]["answer_1"], "lightrag_naive")

    def test_parses_local_judge_result_tag(self) -> None:
        self.assertEqual(parse_pairwise_winner("reasoning\n[RESULT] B"), "B")
        self.assertIsNone(parse_pairwise_winner("reasoning without a result"))


class ReproductionCliTest(unittest.TestCase):
    def test_accepts_extract_token_override(self) -> None:
        args = build_parser().parse_args(
            [
                "--root", "workspace/reproduction-runs/issue-004/runs/run-009", "--run", "--extract-max-tokens", "4096",
                "--repetition-penalty", "1.05",
            ]
        )

        self.assertEqual(args.extract_max_tokens, 4096)
        self.assertEqual(args.repetition_penalty, 1.05)

    def test_accepts_existing_index_query_path(self) -> None:
        args = build_parser().parse_args(
            ["--root", "workspace/reproduction-runs/issue-004/runs/run-035", "--query-existing-index", "data/derived/index"]
        )

        self.assertEqual(args.query_existing_index, Path("data/derived/index"))

    def test_accepts_openai_compatible_judge_settings(self) -> None:
        args = build_parser().parse_args(
            [
                "--root", "workspace/reproduction-runs/issue-004/runs/run-035", "--judge-openai-compatible",
                "--judge-endpoint", "http://localhost:8001/v1",
                "--judge-model", "gpt-oss-20b",
                "--judge-output-filename", "gpt_oss_20b_judge_results.json",
                "--judge-max-tokens", "128",
                "--judge-report-model", "prometheus-eval/prometheus-7b-v2.0",
            ]
        )

        self.assertTrue(args.judge_openai_compatible)
        self.assertEqual(args.judge_model, "gpt-oss-20b")
        self.assertEqual(args.judge_max_tokens, 128)
        self.assertEqual(args.judge_report_model, "prometheus-eval/prometheus-7b-v2.0")

    def test_accepts_official_query_protocol(self) -> None:
        args = build_parser().parse_args(
            ["--root", "experiments/exp-007", "--generate-queries", "--query-protocol", "official", "--query-count", "125"]
        )

        self.assertEqual(args.query_protocol, "official")


class RunValidationTest(unittest.TestCase):
    def test_extends_timeout_for_large_output_limit(self) -> None:
        self.assertGreater(completion_timeout_seconds(32768), 900)

    def test_rejects_non_processed_document(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            store = Path(temporary_directory)
            (store / "kv_store_doc_status.json").write_text(
                json.dumps({"document-a": {"status": "failed"}}), encoding="utf-8"
            )

            with self.assertRaisesRegex(RuntimeError, "未処理document"):
                ensure_documents_processed(store, ["document-a"])

    def test_detects_repetitive_completion(self) -> None:
        analysis = repetition_analysis("\n".join(["same row"] * 30))

        self.assertTrue(analysis["truncated_by_repetition"])

    def test_accepts_stop_completion_despite_repetition(self) -> None:
        self.assertIsNone(completion_failure_reason("stop", "repeated but complete"))
        self.assertEqual(completion_failure_reason("length", "partial"), "finish_reason=length")
