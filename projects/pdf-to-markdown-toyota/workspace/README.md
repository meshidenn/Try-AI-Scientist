# Shared Workspace

このディレクトリには全実験で使い回すPDF変換・評価・vLLM起動コードを置く。実験固有のspec、ログ、出力、結果は `experiments/exp-xxx/` に保存する。

すべての実行器は `--root projects/pdf-to-markdown-toyota/experiments/exp-xxx` を明示し、結果保存先を指定する。

## Local VLM Comparison

`run_general_vlm.py` は外部APIを拒否し、localhostのvLLM OpenAI互換serverだけへリクエストする共有実行器である。モデル名をoutput pathと評価キーに含めるため、同じページを複数モデルで比較できる。

```bash
WORKSPACE_DIR="$PWD/projects/pdf-to-markdown-toyota/experiments/exp-004" \
MODEL="Qwen/Qwen3.6-27B" \
SERVED_MODEL_NAME="qwen3.6-27b" \
CONTAINER="toyota-pdf-qwen36-vllm" \
PORT=18022 \
./projects/pdf-to-markdown-toyota/workspace/start_vllm.sh

uv run python projects/pdf-to-markdown-toyota/workspace/run_general_vlm.py \
  --root projects/pdf-to-markdown-toyota/experiments/exp-004 \
  --logical-name qwen3.6-27b --model-id Qwen/Qwen3.6-27B \
  --served-model qwen3.6-27b --pilot --log-name qwen3.6-27b-pilot.json


## Ensemble Evidence Confidence

`evaluate_ensemble_confidence.py` は、複数モデルの既存Markdownを再推論せずに比較する。数値token単位で、モデル支持率、PDF text layerでの存在、支持モデルの表構造を根拠としてreview用confidenceを出す。これは正答確率ではなく、表のセル位置・列対応を評価しない。

```bash
uv run python projects/pdf-to-markdown-toyota/workspace/evaluate_ensemble_confidence.py \
  --root projects/pdf-to-markdown-toyota/experiments/exp-006 \
  --model-log gemma4-26b-moe=projects/pdf-to-markdown-toyota/experiments/exp-003/logs/hybrid-run-v2.json \
  --model-log qwen3.6-27b=projects/pdf-to-markdown-toyota/experiments/exp-004/logs/qwen3.6-27b-hybrid-pilot.json \
  --model-log glm-4.6v-flash=projects/pdf-to-markdown-toyota/experiments/exp-004/logs/glm-4.6v-flash-pilot.json
```
