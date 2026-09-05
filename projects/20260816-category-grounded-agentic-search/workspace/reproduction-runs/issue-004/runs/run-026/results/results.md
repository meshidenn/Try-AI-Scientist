# Results

## Summary

検証は失敗した。Gemma 4は最初の11チャンク中1チャンク目で `finish_reason=stop` を返したが、
反復検出により失敗扱いとなった。不完全なtriplet、embedding、indexは作成していない。

## Setup

- Dataset split: UltraDomain unique contexts、対象1文書
- Extractor: `RedHatAI/gemma-4-26B-A4B-it-FP8-dynamic`
- JSON extraction、`max_tokens=8192`
- entity上限30、relation上限50、gleaning 0
- Embedding: deterministic-hash-128-v1（抽出検証用）

## Metrics

| Metric | Value |
| --- | ---: |
| Documents | 1 |
| Chunks attempted | 1 / 11 |
| finish_reason | stop |
| Completion tokens | 2,739 |
| Latency | 73.84 s |
| Nonempty lines | 246 |
| Unique lines | 79 |
| Unique-line ratio | 0.321 |

## Main Results

文書statusは `failed`。一意行率0.321は反復閾値0.5未満であり、KG投入前に停止した。

## Figures

なし。

## Failures And Negative Results

Gemma 4でも、重複禁止promptと30/50件上限の併用後に反復生成が発生した。
Qwen（exp-025）の一意行率0.388より低いが、異なるモデル間の品質比較を目的とした十分な
標本数ではない。

## Reproduction

README記載の2コマンド。入力snapshotのchecksumは `inputs/manifest.json` を参照する。

## Notes For Reviewer

これは抽出実装の安全性検証であり、検索品質やLLM-as-a-judgeの評価ではない。
