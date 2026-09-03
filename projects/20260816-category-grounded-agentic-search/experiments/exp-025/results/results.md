# Results

## Summary

検証は失敗した。Qwenは最初の11チャンク中1チャンク目で `finish_reason=stop` を返したが、
反復検出により失敗扱いとなった。したがって、不完全なtriplet、embedding、indexは作成していない。

## Setup

- Dataset split: UltraDomain unique contexts、対象1文書
- Extractor: `Qwen/Qwen3.6-35B-A3B-FP8`
- JSON extraction、`max_tokens=8192`
- entity上限30、relation上限50、gleaning 0
- Embedding: deterministic-hash-128-v1（抽出検証用。KG成功後のみ利用予定）

## Metrics

| Metric | Value |
| --- | ---: |
| Documents | 1 |
| Chunks attempted | 1 / 11 |
| finish_reason | stop |
| Completion tokens | 3,974 |
| Latency | 79.80 s |
| Nonempty lines | 374 |
| Unique lines | 145 |
| Unique-line ratio | 0.388 |

## Main Results

文書statusは `failed`。失敗理由は `unique_line_ratio=0.388` で、設定した0.5未満の
反復閾値に該当したためである。

## Figures

なし。

## Failures And Negative Results

重複禁止promptと30/50件上限を併用しても、Qwenは停止応答内で反復を発生させた。
実装側検出により、この出力はLightRAGのKGとして取り込まれなかった。

## Reproduction

README記載の2コマンド。入力snapshotのchecksumは `inputs/manifest.json` を参照する。

## Notes For Reviewer

これは抽出実装の安全性検証であり、検索精度やLLM-as-a-judgeの評価ではない。
