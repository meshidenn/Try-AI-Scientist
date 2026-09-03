# Results

## Summary

検証は失敗した。反復率は警告として扱われ、最初の4チャンクは `stop` 応答として
LightRAGへ渡された。しかし5チャンク目が8,192 tokensで `length` 終了し、文書statusは
`failed` となった。

## Setup

- Dataset split: UltraDomain unique contexts、対象1文書（11チャンク）
- Extractor: `Qwen/Qwen3.6-35B-A3B-FP8`
- JSON extraction、`max_tokens=8192`
- entity上限30、relation上限50、gleaning 0
- Repetition: 診断・警告のみ

## Metrics

| Metric | Value |
| --- | ---: |
| Documents | 1 |
| Chunks accepted | 4 / 11 |
| LLM calls | 5 |
| stop responses | 4 |
| length responses | 1 |
| Repetition warnings | 5 |
| Completion tokens | 27,004 |
| Total latency | 538.88 s |

受理した4応答の一意行率は0.400、0.387、0.328、0.355であり、反復傾向は一貫していた。

## Main Results

失敗の直接原因は一意率ではない。5チャンク目が `finish_reason=length` となり、JSON抽出を
完了できなかったことである。途中までのLLM cacheは保存されるが、document statusが
`failed` のためKG・embedding・indexの有効成果物として扱わない。

## Figures

なし。

## Failures And Negative Results

反復を許容しても、8,192 output tokensでは書誌一覧を含む5チャンク目が未完了となった。

## Reproduction

README記載の2コマンド。入力snapshotのchecksumは `inputs/manifest.json` を参照する。

## Notes For Reviewer

これは抽出実装の安全性・完了性検証であり、検索品質やLLM-as-a-judgeの評価ではない。
