# Results

## Summary

全61文書のQwen tripletとBGE-M3 LightRAG indexを用い、固定済みの5 queryに対してhybrid/naiveの回答を生成した。reference-answerなしpairwise judgeでは、Prometheus-2、gpt-oss-20bともにhybridを3/5、naiveを2/5選んだ。両judgeの各問の勝者は一致した。

## Setup

- Corpus: `TommyChien/UltraDomain` `mix.jsonl` revision `aa8a51d523f8fc3c5a0ab90dd16b7f6b9dbb5d0d`
- Index: exp-033 Qwen triplet、exp-034 BGE-M3 1,024次元 index
- Indexed documents: 61
- Evaluation queries: exp-016でQwen生成した5 query（1 context由来）
- Answer model: `Qwen/Qwen3.6-35B-A3B-FP8`、temperature 0、max tokens 768
- Retrieval: LightRAG `hybrid` / `naive`、`top_k=5`、`chunk_top_k=5`
- Judges: `prometheus-2`、`gpt-oss-20b`、回答順交互、reference answerなし

## Metrics

- Hybrid responses: 5 / 5 nonempty
- Naive responses: 5 / 5 nonempty
- Qwen calls: 15
- Qwen total tokens: 47,372
- Qwen non-stop finishes: 0
- Prometheus-2 comparisons: 5、hybrid 3勝（60%）、naive 2勝（40%）
- gpt-oss-20b comparisons: 5、hybrid 3勝（60%）、naive 2勝（40%）
- Judge winner agreement: 5 / 5（100%）

## Main Results

全量BGE-M3 indexのload、hybrid/naive retrieval、Qwen回答生成、2種類のjudgeによる判定を完了した。gpt-oss-20bは既存の回答JSONのみを入力としたため、Qwen回答・index・retrieval結果は変更していない。query時に使用したstoreは`outputs/lightrag-store/`の評価用snapshotであり、`data/derived/indexes/`の正本indexは変更していない。

## Figures

図は作成していない。

## Failures And Negative Results

最初の実行はinput manifestの必須hash項目不足で、回答生成前に停止した。hashを追加した再実行は完了した。独立したtest query/gold evidence対応はUltraDomain入力に存在しないため、Recall、EM、F1、evidence coverageは算出していない。

gpt-oss-20bは5件すべてに有効な`[RESULT]`を返したが、query 2の出力は勝者タグだけで詳細な比較理由を含まなかった。勝率集計には使用できる一方、judge rationaleの質的分析には用いない。

## Reproduction

`category_grounded_agentic_search.interfaces.lightrag_reproduction`へ`--query-existing-index`、`--embedding-model bge-m3`、評価用rootを指定して回答を生成し、`--judge-prometheus`で判定する。

## Notes For Reviewer

この勝率はreference answerなしの相対的な回答品質比較であり、原論文の再現スコアやgold-based accuracyではない。5問しかないため、両judgeの一致は判定器間の頑健性を示す予備的な観察にとどまる。公式条件との差分は`review/protocol-differences.md`を参照する。queryログにはchunk vectorが閾値を超えずentity-related chunkへのfallbackが起きた記録、およびreranker未設定の警告がある。
