# Experiment exp-002

Gemma 4 の BF16 target と FP8 Dynamic target に、同じ agent trace 風 workload を replay する。

workload は実際の職場 trace そのものではなく、次の特徴を再現した deterministic synthetic trace である。

- 長い共通 instruction と tool schema
- repository 調査、検索、テスト、集計を想定した tool-call JSON
- tool result を含む後段の synthesis
- 短い structured output と長い最終回答の混在
- prefix がさらに長い compaction 後の再計画

実行条件は BF16/FP8、MTP off/1/2/4/8/16、concurrency 1/2/4。EOS は有効にし、モデルが自然に終了した実出力 token 数を集計する。

## Reproduction

```bash
bash projects/gemma4-fp8-mtp-acceptance/experiments/exp-002/workspace/run_agent_replay.sh
```

特定条件だけ実行する場合:

```bash
VARIANTS=bf16_s4 CONCURRENCIES=1,2,4 \
  bash projects/gemma4-fp8-mtp-acceptance/experiments/exp-002/workspace/run_agent_replay.sh
```

集計:

```bash
uv run python projects/gemma4-fp8-mtp-acceptance/experiments/exp-002/workspace/summarize_results.py
```
