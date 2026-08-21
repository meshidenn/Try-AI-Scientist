#!/usr/bin/env python3
"""PaddleOCR-VLの公式パイプラインをローカルvLLMに接続して実行する。"""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--vllm-url", required=True)
    args = parser.parse_args()

    from paddleocr import PaddleOCRVL

    pipeline = PaddleOCRVL(
        pipeline_version="v1.6",
        vl_rec_backend="vllm-server",
        vl_rec_server_url=args.vllm_url,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for result in pipeline.predict(str(args.input)):
        result.save_to_json(save_path=str(args.output_dir))
        result.save_to_markdown(save_path=str(args.output_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
