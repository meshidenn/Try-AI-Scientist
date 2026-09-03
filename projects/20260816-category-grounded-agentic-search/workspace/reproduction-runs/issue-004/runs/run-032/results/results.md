# Results

## Summary

成功。対象36チャンクはすべて `finish_reason=stop` で完結し、document statusは `processed` となった。

## Setup

- Extractor: `Qwen/Qwen3.6-35B-A3B-FP8`
- JSON extraction、`max_tokens=32768`、`repetition_penalty=1.05`
- Target: `ultradomain-6a7cb621a5218266`（36 chunks）
- Embedding: deterministic-hash-128-v1（抽出完了性の検証用）

## Metrics

| Metric | Value |
| --- | ---: |
| Chunks completed | 36 / 36 |
| Non-stop extraction completions | 0 |
| Maximum completion tokens | 3,679 |
| LLM calls (including merge) | 37 |
| Completion tokens | 88,703 |
| Total latency | 1,686.87 s |
| Repetition warnings | 22 |
| KG entities | 575 |
| KG relations | 660 |

## Main Results

exp-029では11番目のチャンクが32,768 tokensに到達してlength終了した。今回、同じ出力上限に
`repetition_penalty=1.05`を加えると、最大completionは3,679 tokensで全36チャンクが完結した。

## Figures

なし。

## Failures And Negative Results

反復警告は22件記録されたが、診断値として保存し、抽出完了性の失敗とは扱わない。

## Reproduction

README記載の2コマンド。

## Notes For Reviewer

単一文書の再抽出比較であり、モデルの一般的品質や検索精度の結論には用いない。
