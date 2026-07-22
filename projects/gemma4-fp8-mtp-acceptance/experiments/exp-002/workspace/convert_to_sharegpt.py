#!/usr/bin/env python3
"""agent trace JSONL を vLLM ShareGPT loader 用JSONへ変換する。"""

from __future__ import annotations

import json
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parent
INPUT_PATH = WORKSPACE / "agent_trace.jsonl"
OUTPUT_PATH = WORKSPACE / "agent_trace_sharegpt.json"


def main() -> None:
    rows = [
        json.loads(line)
        for line in INPUT_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    conversations = [
        {
            "id": f"agent-trace-{index:03d}",
            "conversations": [
                {"from": "human", "value": row["prompt"]},
                {"from": "gpt", "value": "placeholder response"},
            ],
            "trace_kind": row["trace_kind"],
        }
        for index, row in enumerate(rows)
    ]
    OUTPUT_PATH.write_text(
        json.dumps(conversations, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"converted {len(conversations)} samples: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
