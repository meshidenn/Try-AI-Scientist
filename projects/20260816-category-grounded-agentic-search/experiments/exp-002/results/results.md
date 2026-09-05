# Results

## Summary

固定したLightRAG revision、UltraDomain `mix.jsonl` revision、Qwen vLLM endpointで、小規模なindex/query smoke pilotを完走した。1件のdocument（10,443文字、6 chunk）をindex化し、同一documentをgold documentとする4問へ`hybrid` queryを実行した。4件ともcontext付きの応答を返し、query completionのfinish reasonはすべて`stop`だった。

これはQwen条件の比較性能や原論文の再現を示す結果ではない。Qwen entity extractionは6/6 chunkで`max_tokens=512`に達し、graphには69 entity・0 relationしか保存されなかった。

## Setup

- LightRAG: `HKUDS/LightRAG` revision `5183dec553da29e123d45f663045e8efe24cbedf`
- Corpus: `TommyChien/UltraDomain` revision `aa8a51d523f8fc3c5a0ab90dd16b7f6b9dbb5d0d` の`mix.jsonl`。全source SHA-256は`3e438f40c91a183a246446dd8435a8c1f0de004533e9e90f97ddf862d5c39bc9`。
- Input: 同一documentを共有する4問。selectionとinput checksumは`inputs/manifest.json`に保存。
- LLM: `Qwen/Qwen3.6-35B-A3B-FP8`、served name `llm`、vLLM fingerprint `vllm-0.27.0-5fc4282d`、temperature `0`、thinking無効。
- Retrieval: `hybrid`、`top_k=5`、`chunk_top_k=5`、chunk size/overlapは`512/64`。
- Embedding: endpointにembedding APIがないため、`deterministic-hash-128-v1`。これはpilot専用である。

## Metrics

| Metric | Value |
| --- | ---: |
| Indexed document / chunks | 1 / 6 |
| Queries completed | 4 / 4 |
| Query non-`stop` finishes | 0 |
| LLM calls | 14 |
| Prompt / completion / total tokens | 26,397 / 4,216 / 30,613 |
| Recorded LLM latency | 87.305 s |
| Token-priced API cost | not applicable (self-hosted vLLM) |
| Extract calls at token limit | 6 / 6 |
| Extracted graph entities / relations | 69 / 0 |

## Main Results

`outputs/query_results.json`に4問のquestion、gold answer、response、query latencyを保存した。すべてのresponseは`[no-context]`ではなく、`pilot_inputs.jsonl`をreferenceとして返した。

## Figures

図は作成していない。

## Failures And Negative Results

- 初回runは実行セッションの中断により2/6 chunkで停止した。partial storeは`outputs/failed-interrupted-20260825T0044/`へ退避した。
- token上限を全roleで厳格に扱う試行はextract callの`length`を失敗とし、graphを構築できなかった。artifactは`outputs/failed-strict-truncation-20260825T0048/`へ退避した。
- 最終runではextract roleのtruncationを明示的に許容したためindex/queryは完走したが、relationが抽出されなかった。このrunからrelation-aware retrievalの有効性は結論できない。

## Reproduction

project rootで次を実行する。

```bash
uv run python -m category_grounded_agentic_search.interfaces.lightrag_pilot \
  --root experiments/exp-002 --prepare-inputs
uv run python -m category_grounded_agentic_search.interfaces.lightrag_pilot \
  --root experiments/exp-002 --run
```

runがsummary書込み直前に中断した場合だけ、保存済みoutputを検証して次でsummaryを復元する。

```bash
uv run python -m category_grounded_agentic_search.interfaces.lightrag_pilot \
  --root experiments/exp-002 --recover-summary
```

## Notes For Reviewer

このartifactはendpoint・固定revision・input snapshot・index/queryの接続確認のevidenceである。semantic embedding、relation extraction、baseline、複数documentでのgold-evidence retrieval評価が未実施のため、性能比較のevidenceにはならない。
