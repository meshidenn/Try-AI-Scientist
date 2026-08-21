# Experiment exp-002

## Objective

exp-001と同じPDFページをHTML fragmentとして出力し、`parse_first`と`image_first`を比較する。

## Status

`completed`。選定11ページを2方式でHTML fragment化し、22件すべて成功した。

## Reproduction

```bash
WORKSPACE_DIR="/projects/pdf-to-markdown-toyota/experiments/exp-002/workspace" LOG_DIR="/projects/pdf-to-markdown-toyota/experiments/exp-002/logs" ./projects/pdf-to-markdown-toyota/workspace/start_vllm.sh
uv run --project projects/pdf-to-markdown-toyota python -m pdf_to_markdown_toyota.interfaces.cli.run_vllm_experiment --root projects/pdf-to-markdown-toyota/experiments/exp-002 --pdf-dir projects/pdf-to-markdown-toyota/experiments/exp-001/workspace/input/pdfs --max-pages 3 --max-new-tokens 1024 --output-format html --log-name vllm-html-run.json
```
