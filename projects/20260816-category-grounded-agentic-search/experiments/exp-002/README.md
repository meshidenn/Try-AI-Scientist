# exp-002: LightRAGのQwen3.6-35B-A3B-FP8再評価

## Status

**Blocked / 未実行。** この環境ではNVIDIA driverが利用できず、Qwen FP8 modelを提供するOpenAI互換endpointも未設定である。

## Scope

corpusを変更する実験ではない。LightRAGのcorpus、質問、gold evidence、chunking、retrieval設定を固定し、LLMを`Qwen/Qwen3.6-35B-A3B-FP8`へ置き換える。

## Preconditions

1. LightRAG code revisionと`TommyChien/UltraDomain` corpus revisionをpinし、checksumをinputs manifestへ書く。
2. 42GB以上のVRAMを持つ対応GPU、または同modelを提供するOpenAI互換endpointを用意する。
3. server version、model revision、prompt、temperature、max tokens、retry policyを固定する。

## Interpretation

結果はLLM変更を伴う再評価としてだけ報告する。元論文または公式実装の完全再現とは表現しない。
