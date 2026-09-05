# exp-002: LightRAGのQwen3.6-35B-A3B-FP8再評価

## Status

**Completed with warnings / 小規模pilot完了。** 固定したLightRAG revisionとUltraDomain `mix.jsonl`の4問でindex構築とhybrid queryを完走した。entity extractionは6 chunkすべてでtoken上限に達してrelationが0件のため、比較性能の再評価は主張しない。

## Scope

corpusを変更する実験ではない。LightRAGのcorpus、質問、gold evidence、chunking、retrieval設定を固定し、LLMを`Qwen/Qwen3.6-35B-A3B-FP8`へ置き換える。

## Preconditions

1. LightRAG revision `5183dec553da29e123d45f663045e8efe24cbedf`とUltraDomain revision `aa8a51d523f8fc3c5a0ab90dd16b7f6b9dbb5d0d`を`inputs/manifest.json`へ固定した。
2. vLLM endpointのserved model `llm` と`chat_template_kwargs.enable_thinking=false`を全条件で固定した。
3. 実行設定、token使用量、回答、store、ログを`outputs/`と`logs/`に保存した。

## Interpretation

このrunはQwen endpointによるLightRAGのindex/query疎通を示すだけであり、embedding modelの妥当性、relation extractionの品質、baselineとの性能差は示さない。詳細は`results/results.md`と`review/artifact-audit.md`を参照する。
