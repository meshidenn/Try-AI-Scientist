#!/usr/bin/env python3
"""MinerU2.5-Proの公式2段階抽出をローカルvLLMで実行する。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--model", default="opendatalab/MinerU2.5-Pro-2604-1.2B")
    parser.add_argument("--image-analysis", action="store_true")
    args = parser.parse_args()

    from PIL import Image
    from mineru_vl_utils import MinerUClient, MinerULogitsProcessor
    from mineru_vl_utils.post_process import json2md
    from vllm import LLM

    llm = LLM(model=args.model, logits_processors=[MinerULogitsProcessor])
    client = MinerUClient(
        backend="vllm-engine",
        vllm_llm=llm,
        image_analysis=args.image_analysis,
    )
    content = client.two_step_extract(Image.open(args.input).convert("RGB"))
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.output_markdown.write_text(json2md(content), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
