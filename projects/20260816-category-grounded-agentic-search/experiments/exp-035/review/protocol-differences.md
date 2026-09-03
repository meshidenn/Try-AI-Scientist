# LightRAG公式条件との差分

## 判定

本実験は、QwenへのLLM変更を含むLightRAG-style再評価であり、原論文または公式実装の完全再現ではない。

| 項目 | 公式プロトコルでの位置づけ | 本pilot | 解釈への影響 |
| --- | --- | --- | --- |
| Corpus | UltraDomainを評価corpusとして用いる | `mix.jsonl` revisionをhash固定し、61 unique contextを全量index化 | 固定revision内でのみ再現可能。公式の全評価設定との同一性は主張しない。 |
| Query | 高水準queryを生成して比較する | Qwenで事前生成した5 queryを固定・再利用 | Qwenのquery分布に依存する。 |
| Entity/relation extraction | LightRAGのKG抽出 | Qwen JSON抽出、32,768 token、`repetition_penalty=1.05` | 抽出モデル・出力制御が異なるため、公式スコアとの直接比較はできない。 |
| Embedding | 公式設定と独立に管理される検索要素 | BGE-M3 1,024次元 | vector model差がretrieval結果に影響する。 |
| Answer generation | 評価用LLMで回答を生成する | Qwen、temperature 0、max tokens 768 | 生成能力差を含む再評価である。 |
| Judge | LLM-as-a-judgeによる回答比較 | Prometheus-2、reference answerなし、回答順交互 | 相対的な回答品質の判定であり、gold-based accuracyではない。 |
| Gold evidence | 評価定義に必要な場合は対応を固定する | このpilotでは未提供・未使用 | Recall、EM、F1、evidence coverageは算出しない。 |

## 固定した実行条件

- Qwen: `Qwen/Qwen3.6-35B-A3B-FP8`、served name `llm`、temperature 0、thinking無効
- Chunking: 512 tokens、overlap 64 tokens
- Retrieval: `hybrid` / `naive`、`top_k=5`、`chunk_top_k=5`
- Corpus revision: `aa8a51d523f8fc3c5a0ab90dd16b7f6b9dbb5d0d`

## 参照

- Issue #4の再評価定義
- `experiments/exp-002/spec.yaml` の公式repository/corpus revision pin
- `experiments/exp-033/` と `experiments/exp-034/` の全量index artifact
