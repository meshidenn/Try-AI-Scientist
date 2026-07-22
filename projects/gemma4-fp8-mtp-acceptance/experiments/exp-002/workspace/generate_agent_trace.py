#!/usr/bin/env python3
"""agent trace に近い deterministic benchmark dataset を生成する。"""

from __future__ import annotations

import json
from pathlib import Path


OUTPUT_PATH = Path(__file__).with_name("agent_trace.jsonl")

SYSTEM_INSTRUCTIONS = """あなたは社内 coding agent です。正確性を優先し、変更前に repository を調査してください。
利用可能な tool から必要最小限のものを選び、tool call が必要なら JSON だけを返してください。
既存の変更を戻さず、秘密情報を表示せず、テスト結果と推測を区別してください。
複数の独立した読み取りは並列化し、編集後は lint と対象 test を実行してください。
最終回答は、結果、変更ファイル、検証、残るリスクを簡潔に記載してください。"""

TOOL_SCHEMA = """利用可能な tools:
1. exec_command
{"type":"object","properties":{"cmd":{"type":"string"},"workdir":{"type":"string"},"yield_time_ms":{"type":"integer"}},"required":["cmd","workdir"]}
2. apply_patch
{"type":"object","properties":{"patch":{"type":"string"}},"required":["patch"]}
3. search_code
{"type":"object","properties":{"query":{"type":"string"},"path":{"type":"string"}},"required":["query","path"]}
4. read_file
{"type":"object","properties":{"path":{"type":"string"},"start_line":{"type":"integer"},"end_line":{"type":"integer"}},"required":["path"]}
5. run_tests
{"type":"object","properties":{"targets":{"type":"array","items":{"type":"string"}},"timeout_sec":{"type":"integer"}},"required":["targets"]}
返却形式は {"tool":"tool_name","arguments":{...}} とする。"""

REPO_CONTEXT = """Repository overview:
- src/agent/runtime.py: agent loop と state transition
- src/agent/tools.py: tool registry と validation
- src/server/api.py: OpenAI-compatible HTTP endpoint
- src/server/scheduler.py: concurrency と queue policy
- tests/test_runtime.py: agent loop unit tests
- tests/test_tools.py: schema validation tests
- tests/test_api.py: streaming integration tests
- pyproject.toml: Python dependency と lint configuration
Current branch has unrelated local edits in docs/notes.md. These edits must remain untouched.
Observed incident: FP8 target with MTP was slower for agent requests, while a random-token benchmark was faster.
Candidate causes include short structured output, EOS behavior, batching, prefix-cache interaction, and draft acceptance."""


def repeated_history(blocks: int) -> str:
    """長い agent history を、意味を保ったまま一定量追加する。"""
    entries = []
    for index in range(1, blocks + 1):
        entries.append(
            f"Step {index}: searched src/module_{index % 7}.py for scheduler state. "
            f"Tool result: found {3 + index % 5} references; no secret values. "
            f"Test shard {index % 4} reported {18 + index} passed and 0 failed. "
            "Decision: preserve unrelated edits and continue with the smallest scoped check."
        )
    return "\n".join(entries)


def make_prompt(task: str, phase: str, history_blocks: int, tool_result: str = "") -> str:
    sections = [
        "SYSTEM INSTRUCTIONS\n" + SYSTEM_INSTRUCTIONS,
        "TOOL SCHEMA\n" + TOOL_SCHEMA,
        "REPOSITORY CONTEXT\n" + REPO_CONTEXT,
        "AGENT HISTORY\n" + repeated_history(history_blocks),
        "CURRENT TASK\n" + task,
        "CURRENT PHASE\n" + phase,
    ]
    if tool_result:
        sections.append("LATEST TOOL RESULT\n" + tool_result)
    return "\n\n".join(sections)


def build_samples() -> list[dict[str, object]]:
    tasks = [
        "Find the source of a latency regression and choose the first repository inspection command.",
        "Inspect scheduler batching and prefix-cache configuration without changing files.",
        "Return a valid tool call to run the narrow runtime tests.",
        "Review the failing test output and select the next file to inspect.",
        "Prepare a minimal patch for tool schema validation while preserving current behavior.",
        "After the patch, decide which lint and unit tests should run in parallel.",
        "Summarize benchmark evidence and separate measurements from hypotheses.",
        "Analyze whether EOS-heavy JSON output can reduce speculative decoding benefit.",
    ]
    samples: list[dict[str, object]] = []
    for index, task in enumerate(tasks):
        # tool-call 相当: 短く構造化された出力を期待する。
        samples.append(
            {
                "prompt": make_prompt(task, "Return exactly one tool-call JSON object.", 8 + index),
                "output_tokens": 96,
                "trace_kind": "tool_call",
            }
        )
        # synthesis 相当: tool result を受けた自然終了の回答を期待する。
        samples.append(
            {
                "prompt": make_prompt(
                    task,
                    "Produce the final engineering response. Do not call another tool.",
                    42 + index * 5,
                    tool_result=(
                        "Command completed successfully. 47 tests passed in 12.8s. "
                        "Median TPOT increased only at concurrency 2; concurrency 1 and 4 improved. "
                        "Speculative acceptance was lower for FP8 in the affected run."
                    ),
                ),
                "output_tokens": 512 if index >= 4 else 256,
                "trace_kind": "synthesis_long" if index >= 4 else "synthesis",
            }
        )
    return samples


def main() -> None:
    samples = build_samples()
    with OUTPUT_PATH.open("w", encoding="utf-8") as output:
        for sample in samples:
            output.write(json.dumps(sample, ensure_ascii=False) + "\n")
    print(f"generated {len(samples)} samples: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
