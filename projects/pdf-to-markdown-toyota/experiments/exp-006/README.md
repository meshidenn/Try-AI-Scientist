# exp-006: Three-VLM ensemble evidence confidence pilot

Gemma 4 26B MoE、Qwen 3.6 27B、GLM-4.6V-Flashの既存 `hybrid` Markdownを再利用し、数値tokenごとの根拠付きconfidenceを試す。追加推論は行わない。

confidenceは校正済みの正答確率ではない。モデル間の支持、PDF text layerでの存在確認、支持モデルが出したMarkdown表の列数一貫性を加重した、人手レビュー優先順位付け用のevidence scoreである。

実装は共有の `workspace/evaluate_ensemble_confidence.py` に置く。実験ディレクトリには条件、入力manifest、生成artifactだけを置く。

## Reproduction

```bash
uv run python projects/pdf-to-markdown-toyota/workspace/evaluate_ensemble_confidence.py \
  --root projects/pdf-to-markdown-toyota/experiments/exp-006 \
  --model-log gemma4-26b-moe=projects/pdf-to-markdown-toyota/experiments/exp-003/logs/hybrid-run-v2.json \
  --model-log qwen3.6-27b=projects/pdf-to-markdown-toyota/experiments/exp-004/logs/qwen3.6-27b-hybrid-pilot.json \
  --model-log glm-4.6v-flash=projects/pdf-to-markdown-toyota/experiments/exp-004/logs/glm-4.6v-flash-pilot.json
```
