# Results

## Summary

UltraDomain Mixの全61 unique contextから、公式LightRAG再現コードと同じ5ユーザー×5タスク×5質問の形式でQwen3.6-35B-A3B-FP8に125問を生成した。既存のQwen triplet / BGE-M3 indexに対してLightRAG hybridとnaiveを各125問実行した。

GPT-4o-miniのBatch judgeを回答順交互・参照回答なしで実行した。初回Batchでは6件がJSON出力完了前に`finish_reason=length`となったため、同じモデル・temperatureで出力上限を1,024へ固定して6件だけ再判定した。125件すべての判定を取得した。ローカルのgpt-oss-20b、Prometheus-7B-v2.0、gpt-oss-120bは補助的な比較として残す。

## Setup

- Corpus: `TommyChien/UltraDomain` Mix, revision `aa8a51d523f8fc3c5a0ab90dd16b7f6b9dbb5d0d`, 61 unique contexts
- Question set: Qwen生成125問、SHA-256 `a3f6360dde32c6f2fd575cf29b17d082fd20be5f91e6d5133ab6e6374579bf1a`
- Index: Qwen3.6-35B-A3B-FP8 triplets + `BAAI/bge-m3`, 1,375 chunks / 20,281 entities / 23,869 relations
- Retrieval: `hybrid` vs `naive`, `top_k=5`, `chunk_top_k=5`
- Answer model: Qwen3.6-35B-A3B-FP8, temperature 0, max tokens 768, retry 3回・5秒間隔
- Primary judge: OpenAI Batch APIの`gpt-4o-mini`（実行時model ID: `gpt-4o-mini-2024-07-18`）、temperature 0、JSON object、回答順交互
- 初回Batch `batch_6a9b8f12a69c81908801eed5086f9378`の6件だけを、同条件・max tokens 1,024でBatch `batch_6a9b920380ac81909023c68f21f677cc`へ再投入

## Metrics

主指標は、125組の回答比較におけるOverallのpairwise win rateである。参照回答・gold evidenceを用いないため、正解率やretrieval recallではない。

## Main Results

| Judge | Hybrid wins | Naive wins | Tie | Hybrid win rate | Naive win rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| GPT-4o-mini（主評価） | 50 / 125 | 58 / 125 | 17 / 125 | 40.0% | 46.4% |
| gpt-oss-20b（代替judge） | 60 / 125 | 65 / 125 | — | 48.0% | 52.0% |
| Prometheus-7B-v2.0（代替judge） | 65 / 125 | 60 / 125 | — | 52.0% | 48.0% |
| gpt-oss-120b（代替judge） | 52 / 125 | 73 / 125 | — | 41.6% | 58.4% |

GPT-4o-miniのTieを除いた108件では、hybridは50勝（46.3%）、naiveは58勝（53.7%）である。主指標を全125件で割るとhybrid 40.0%、naive 46.4%であり、naiveが8勝多い。

回答生成は250回答を完走し、実行時間は2,305.7秒だった。Qwen呼び出しは332回、合計1,185,928 tokensだった。

## 原論文との参考比較

原論文Table 1のOverallは、原著者のLLM・index・質問セット・大規模UltraDomain corpusで得た、NaiveRAG対LightRAGのpairwise win rateである。今回のQwen variantとは実験条件が異なるため、**参考値であり直接比較ではない**。特に今回のMixは61 unique contextであり、原論文のMixを含む各corpusは60万〜500万tokensで評価されている。

| UltraDomain dataset | 原論文 NaiveRAG | 原論文 LightRAG | 今回の対応値 |
| --- | ---: | ---: | ---: |
| Agriculture | 32.4% | 67.6% | 未実施 |
| CS | 38.8% | 61.2% | 未実施 |
| Legal | 15.2% | 84.8% | 未実施 |
| Mix | 40.0% | 60.0% | hybrid 40.0%、naive 46.4%、Tie 13.6% |

原論文のMixではLightRAGが20.0ポイント高いのに対し、今回の全125件比率ではnaiveが6.4ポイント高い。原論文の勝率はTieなしで二方式の合計が100%になる一方、今回の主評価には17 Tieがある点にも注意する。

出典: [Guo et al., *LightRAG: Simple and Fast Retrieval-Augmented Generation*, Table 1 (2025)](https://aclanthology.org/2025.findings-emnlp.568.pdf)

## Failures And Negative Results

- 初回GPT-4o-mini Batchの6件は`finish_reason=length`で、JSONを完結できなかった。6件を同じモデル・temperatureで再評価し、全125件を回収した。
- gpt-oss-20bの通常設定では内部reasoningが出力枠を消費して`[RESULT]`を返さなかった。`reasoning_effort: low`と2,048 tokensへ固定して125組を完走した。
- Prometheus-7B-v2.0は詳細比較を先に出すため、結果タグを返すには1,024 tokensが必要だった。
- Qwen回答生成では5回が`finish_reason=length`として診断ログに残った。runは完走しているが、これらが最終比較のどの回答へ影響したかは別途確認が必要である。

## Reproduction

```bash
uv run python -m category_grounded_agentic_search.interfaces.lightrag_reproduction \
  --root experiments/exp-007 \
  --query-existing-index data/derived/indexes/UltraDomain--aa8a51d523f8fc3c5a0ab90dd16b7f6b9dbb5d0d/Qwen--Qwen3.6-35B-A3B-FP8__BAAI--bge-m3/lightrag-store \
  --embedding-model bge-m3 --extract-max-tokens 32768 --repetition-penalty 1.05
```

## Notes For Reviewer

この結果はQwenへのLLM変更を伴う再評価であり、原論文の完全再現ではない。主評価のGPT-4o-miniではnaiveが8勝多かった。一方、代替judgeのhybrid勝率は41.6%から52.0%まで変動しているため、この一回の125問比較だけで方式一般の優劣を結論づけない。
