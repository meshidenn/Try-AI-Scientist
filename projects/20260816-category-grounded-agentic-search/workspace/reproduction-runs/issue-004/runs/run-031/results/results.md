# Results

## Summary

未実測。最初のchunkへのリクエストでQwenサーバーとの接続が切れたため、
`repetition_penalty=1.05` の抽出停止性への効果は判定できない。

## Setup

- Extractor: `Qwen/Qwen3.6-35B-A3B-FP8`
- JSON extraction、`max_tokens=32768`、`repetition_penalty=1.05`
- Target: `ultradomain-6a7cb621a5218266`（36 chunks）

## Metrics

| Metric | Value |
| --- | ---: |
| Chunks completed | 0 / 36 |
| Successful LLM calls | 0 |

## Main Results

なし。

## Figures

なし。

## Failures And Negative Results

Qwen endpoint `192.168.100.11:8000` への接続失敗。実験条件の効果とは区別する。

## Reproduction

README記載のコマンド。

## Notes For Reviewer

サーバー復帰後に同じ条件で新規runを作成して再実行する。
