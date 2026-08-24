# exp-002: LightRAGのQwen3.6-35B-A3B-FP8再評価

## Status

**Planned / 未実行。** `http://192.168.100.11:8000/v1` のvLLM endpointでQwen modelの一覧取得とchat completionを確認済みである。LightRAG codeとcorpus revisionの固定後にpilotを開始する。

## Scope

corpusを変更する実験ではない。LightRAGのcorpus、質問、gold evidence、chunking、retrieval設定を固定し、LLMを`Qwen/Qwen3.6-35B-A3B-FP8`へ置き換える。

## Preconditions

1. LightRAG code revisionと`TommyChien/UltraDomain` corpus revisionをpinし、checksumをinputs manifestへ書く。
2. vLLM endpointのserved model `llm` を使用し、`chat_template_kwargs.enable_thinking=false`を全条件で固定する。
3. server fingerprint、model revision、prompt、temperature、max tokens、retry policyを固定する。

## Interpretation

結果はLLM変更を伴う再評価としてだけ報告する。元論文または公式実装の完全再現とは表現しない。
