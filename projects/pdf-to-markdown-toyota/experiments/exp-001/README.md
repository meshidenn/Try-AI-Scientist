# Experiment exp-001

## Objective

トヨタ自動車の4種類の企業資料を、表を含むMarkdownへ変換する初回比較実験。PDFを先に構造化する `parse-first` と、ページを画像化する `image-first` を、同一モデル・同一ページ・同一Markdown制約で比較する。

## Status

`completed_selected_pages_vllm`。PDF取得後、vLLM OpenAI互換サーバーで4資料の選定ページを2方式で実行した。22件すべてが成功し、表を含む出力を保存した。

## Documents

対象候補、公式URL、資料種別の仮定は [`../../survey/README.md`](../../survey/README.md) と [`spec.yaml`](spec.yaml) を参照。

## Reproduction

依存同期:

```bash
uv sync
```

vLLMサーバー起動と初回スモーク実行:

```bash
WORKSPACE_DIR="/projects/pdf-to-markdown-toyota/experiments/exp-001/workspace" LOG_DIR="/projects/pdf-to-markdown-toyota/experiments/exp-001/logs" ./projects/pdf-to-markdown-toyota/workspace/start_vllm.sh
uv run python projects/pdf-to-markdown-toyota/workspace/run_vllm_experiment.py --root projects/pdf-to-markdown-toyota/experiments/exp-001 --max-pages 3 --max-new-tokens 1024
uv run python projects/pdf-to-markdown-toyota/workspace/evaluate_outputs.py --root projects/pdf-to-markdown-toyota/experiments/exp-001 --log projects/pdf-to-markdown-toyota/experiments/exp-001/logs/vllm-run.json --log projects/pdf-to-markdown-toyota/experiments/exp-001/logs/vllm-retry-integrated-p11-32k.json
```

## Notes

GitHub issue作成は `gh auth` 未設定によるHTTP 401で失敗した。作業branchは `exp/0-pdf-to-markdown-toyota`。
