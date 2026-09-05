import unittest

from category_grounded_agentic_search.interfaces.lightrag_pilot import (
    LlmCall,
    PILOT_RECORD_IDS,
    RunMetrics,
    build_parser,
    selected_records,
)


def make_record(record_id: str) -> dict[str, object]:
    return {
        "_id": record_id,
        "context": "shared document",
        "input": "question",
        "answers": ["answer"],
    }


class PilotSelectionTest(unittest.TestCase):
    def test_selects_all_fixed_records_in_fixed_order(self) -> None:
        rows = [make_record(record_id) for record_id in reversed(PILOT_RECORD_IDS)]

        selected = selected_records(rows)

        self.assertEqual([record["_id"] for record in selected], list(PILOT_RECORD_IDS))

    def test_rejects_context_drift(self) -> None:
        rows = [make_record(record_id) for record_id in PILOT_RECORD_IDS]
        rows[-1]["context"] = "different document"

        with self.assertRaises(ValueError):
            selected_records(rows)


class RunMetricsTest(unittest.TestCase):
    def test_counts_non_stop_query_completions_separately(self) -> None:
        metrics = RunMetrics(
            calls=[
                LlmCall(1.0, 10, 20, 30, "length", "extract"),
                LlmCall(2.0, 20, 30, 50, "stop", "query"),
            ]
        )

        summary = metrics.as_mapping()

        self.assertEqual(summary["non_stop_finish_reasons"], 1)
        self.assertEqual(summary["non_stop_query_finish_reasons"], 0)


class PilotCliTest(unittest.TestCase):
    def test_accepts_extract_token_override(self) -> None:
        args = build_parser().parse_args(
            ["--root", "experiments/exp-003", "--run", "--extract-max-tokens", "1024"]
        )

        self.assertEqual(args.extract_max_tokens, 1024)
