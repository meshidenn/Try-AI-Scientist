# Results

## Summary

成功。32,768 tokensでは対象1文書の全11チャンクが `finish_reason=stop` で完結し、
LightRAGのdocument statusは `processed` となった。8,192 tokensで発生した5チャンク目の
未完了は、出力上限の拡張により解消された。

## Setup

- Dataset split: UltraDomain unique contexts、対象1文書（11チャンク）
- Extractor: `Qwen/Qwen3.6-35B-A3B-FP8`
- JSON extraction、`max_tokens=32768`
- entity上限30、relation上限50、gleaning 0
- Repetition: 診断・警告のみ
- Embedding: deterministic-hash-128-v1（抽出完了性の確認用）

## Metrics

| Metric | Value |
| --- | ---: |
| Documents processed | 1 / 1 |
| Chunks completed | 11 / 11 |
| Extraction completions with `stop` | 11 / 11 |
| Non-stop extraction completions | 0 |
| Repetition warnings | 11 |
| LLM calls (including merge) | 12 |
| Completion tokens | 66,632 |
| Total latency | 1,332.40 s |
| KG entities | 326 |
| KG relations | 602 |

## Main Results

5チャンク目は10,468 completion tokens、8チャンク目は12,300 completion tokensで完結した。
したがって、8,192 tokensでの失敗は少なくともこの文書では出力長不足が直接原因だった。

## Figures

なし。

## Failures And Negative Results

反復警告は11件すべてで記録された。一意行率は0.257から0.430の範囲だが、JSON completionは
すべて完結しており、重複率だけを失敗判定にしない方針と整合する。

## Reproduction

README記載の2コマンド。入力snapshotのchecksumは `inputs/manifest.json` を参照する。

## Notes For Reviewer

この検証は抽出完了性に限る。embeddingはhashであり、BGE-M3を用いる正式index・検索精度・
LLM-as-a-judge評価は対象外である。
