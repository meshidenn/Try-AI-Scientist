# 実験1: Text-derived Retrieval Baseline Plan

## Status

**計画中。未実装・未実行。**

研究全体の最新の正本は [RESEARCH_PLAN.md](RESEARCH_PLAN.md) と `experiments/exp-001/spec.yaml` である。本書とそれらの間に条件の差がある場合は、後者を優先する。

この文書は、外部のcategory/taxonomy/ontology/knowledge graphを利用せず、文書本文から誘導した構造のみを許可する条件で、open-loop retrievalとclosed-loop iterative searchを共通条件で比較する実験計画である。本文からentity/relation graphを構築するLightRAGは対象に含める。A-MEMは対象に含めない。

本実験の目的は新規性を直接主張することではなく、既存研究で示されてきた傾向を共通の実行・評価環境で確認し、後続の category-aware 実験に必要な基準線を作ることである。

## 背景

複数証拠を必要とする質問では、先に取得した文書から中間entityや不足した制約を得て、次の検索を行う逐次検索が有効であることは既に知られている。GoldEn Retriever、AISO、IRCoT、ReActは、それぞれ異なる形で検索・推論・再検索を組み合わせている。

一方、SIRAは文書側・query側の語彙拡張とcorpus statisticsを用いて、複数ラウンドの探索を一つの検索行動へ圧縮する。LightRAGはentity/relation graphを索引化し、局所的なentityと大域的なテーマを併用して文脈を取得する。各論文はretriever、LLM、コーパス、検索予算、評価指標が異なるため、論文間の報告値だけから方式差を断定することはできない。

## 目的

1. text-only条件で、SIRA、LightRAG、iterative agentic search の検索品質・回答品質・コストを共通に測定する。
2. 方式ごとの平均性能ではなく、queryの情報構造ごとの傾向を記述する。
3. 後続のcategory-aware実験で利用する、再現可能なindex、評価器、検索予算、ログ形式を確立する。

## 本実験で主張しないこと

- agentic searchの一般原理を新規に発見したとは主張しない。
- category/taxonomyがagentic searchを代替する、または不要にすると主張しない。
- 一方式が常に最良であるとは主張しない。
- 原論文と異なるLLM、retriever、実装を用いた結果を、原論文の再現成功と見なさない。

## Research Questions

### RQ1: 共通条件での検索品質

同一コーパス、同一検索予算、同一reader条件の下で、各方式はRecall、順位品質、必要証拠の取得率にどのような差を示すか。

### RQ2: 情報構造との交互作用

各方式の性能差は、以下のqueryタイプでどのように変化するか。

- direct lexical: queryと根拠の語彙が直接対応する。
- vocabulary gap: 同義語、略語、専門用語、別表記が必要である。
- implicit attribute: 文書に明示されない属性制約を満たす根拠を探す。
- relation/multi-document: 複数文書のentity/relationを組み合わせる。

既存のmulti-hopデータセットは、最後の型を各設問について保証・注釈しているわけではない。したがって、これは事前のquery型ではなく、open-loopとclosed-loopの差およびtrajectoryから行う事後診断とする。

### RQ3: 検索予算と費用対効果

一回のcorpus-grounded retrievalと、複数ラウンドの検索・観察・再検索の差は、閲覧可能文書数と推論tokenの予算に対してどのように変化するか。

## 対象データ

主実験では、公開されているmulti-hop open-domain QAデータを使用する。

| データセット | 役割 | 使用目的 |
| --- | --- | --- |
| HotpotQA FullWiki | Wikipedia上の2-hop QA | SIRA、ReAct、AISO等との接続点 |
| 2WikiMultiHopQA | 複数種のrelationを含むmulti-hop QA | relation依存の検索を評価 |
| MuSiQue | 合成的なmulti-hop QA | composition chainを用いた診断 |

各データセットでは、配布済みのcorpus、query、gold supporting documentまたはqrelsの対応を固定し、文書IDを変更しない。Wikipedia dumpを再構成する場合は、snapshot日時、前処理、chunking、記事からpassageへの対応をmanifestに記録する。

通常IRへの外挿は本実験の必須範囲に含めない。BEIR NQ、ArguAna、SciDocs、SciFact等への追加は、基準線確立後の拡張候補とする。

## 比較手法

### 共通baseline

- BM25: text-only sparse retrieval。
- Dense retrieval: E5等の公開checkpointを用いる固定dense retriever。

### 主比較

- SIRA text-only: document/query vocabulary enrichmentとDF filteringを用いたone-shot BM25 retrieval。
- LightRAG: 本文から抽出したentity/relation graphによるretrieval。
- Controlled iterative agent: ReActまたはIRCoT形式で、共通の検索APIを呼び出すagent。

### AutoIndexの扱い

AutoIndexはvalidation qrelsを用いて索引表現を探索するため、他方式と異なるoffline最適化を含む。本実験では実装対象から外し、評価器とdev/test分離が安定した後の追加ablation候補とする。

## 実験条件

### 外部構造なし・本文由来構造のみの制約

- category、taxonomy、外部knowledge graph、Wikipedia category、外部web検索は利用しない。
- 文書本文、タイトル、データセットが明示的に提供する通常metadataのみを利用する。
- 文書本文から抽出したentity/relation graphは利用してよい。
- query、dev qrels、test qrelsをdocument-side LLM promptに混入させない。

### 共通化する要素

- corpus snapshotとdocument/passage ID
- query split、dev split、test split
- reader LLMと回答prompt
- readerへ渡す最大context token数
- 最終的に評価対象とするunique document数
- rerankerの有無
- queryあたりの最大推論token数

LightRAGのgraph構築、SIRAのdocument-side enrichment、agentの検索ラウンドは方式固有の処理として許可するが、すべてのLLM呼出数、入力・出力token、実行時間、index sizeを記録する。

### Open-loop / closed-loop と検索予算

以下のdocument budgetを基本とする。

| Budget | 解釈 |
| --- | --- |
| 1 | first-rank evidenceの品質 |
| 10 | 小さなreader contextに収まるevidence取得 |
| 100 | 広めの探索・再ランキング余地 |

open-loop条件では、すべてのqueryとgraph lookup要求を取得結果の観察前に確定する。複数queryの事前生成は許可するが、closed-loop条件と同じ最大tool call数・unique document budgetに置く。closed-loop条件では、観察済みの結果を読んだ後に次のtool callを選べる。いずれも観察したunique documentがbudgetを消費し、無制限のquery reformulationは認めない。

## 評価

### Retrieval評価

- Recall@1、Recall@10、Recall@100
- nDCG@10
- MRR
- all-evidence recall: 一問に必要なgold evidenceがすべて取得できた割合
- evidence coverage by turn: agentが各turnでgold evidenceへ到達した割合

### 回答評価

全方式で固定readerを用い、取得結果のみから回答を生成する。

- Exact Match
- Answer F1
- 根拠付き回答率
- unsupported claim rate

### 効率・trajectory評価

- queryあたりのLLM input/output token
- index構築tokenと時間
- query latencyのp50/p95
- unique document数
- 検索turn数
- 重複文書取得率
- query drift率

offline index構築費は、query件数で償却した費用と、償却しない総費用の両方を報告する。

## 分析計画

平均スコアのみで結論を出さず、以下の交互作用を報告する。

```text
method × query type × retrieval budget
```

queryタイプは、既存データセットのannotationを優先して利用し、不足する場合はgold evidence chainを用いた規則ベースの候補抽出と、人手監査サンプルで定義する。evidence-dependent multi-hopは、事前の正解ラベルではなく、元queryにないbridge entityまたは制約が先行観察に現れ、後続queryで使われたかをtrajectoryとgold evidenceで照合する事後診断として扱う。人手監査標本で定義の妥当性を確認する。

各方式は複数seedで実行し、query単位のpaired bootstrap confidence intervalを算出する。差の有無だけでなく、精度・token・latencyのPareto frontierを示す。

## 再現性とリーク対策

- dev/testは厳密に分離する。
- AutoIndexを将来追加する場合、program searchはdev qrelsに限定する。
- SIRAのdocument enrichmentにはqueryやqrelsを渡さない。
- LightRAGのentity/relation抽出のprompt、モデル、temperature、再試行条件を固定する。
- agentが取得済み文書を利用してqueryを更新した場合は、各turnのprompt、tool call、観察文書IDを保存する。
- query生成や人手分類にtest answerを利用した場合は、その使用範囲を明記し、評価用testと分離する。

## 成功判定

本実験の成功は、特定手法の勝利ではなく、次を満たすことで判定する。

1. 全方式を同一のcorpus・budget・評価器で実行できる。
2. 各runでretrieval結果、費用、trajectoryを追跡できる。
3. 少なくとも一つのデータセットで、原論文の報告と大きく矛盾しない傾向を確認できる。
4. category-aware実験の対照として使える、固定されたtext-only基準線を保存できる。

結果が既存報告と異なる場合も失敗とは見なさず、corpus snapshot、retriever、LLM、検索予算、評価定義の差を切り分けて記録する。

## 実施フェーズ

1. データ取得・corpus manifest・split確認。
2. BM25とdense baselineの再現。
3. SIRA text-onlyとcontrolled iterative agentの実装・小規模pilot。
4. LightRAG追加と共通評価器の検証。
5. 3データセットの本実験、queryタイプ別分析、cost分析。

初期pilotはHotpotQAの小規模固定subsetで行い、評価器、budget会計、trajectory保存が正しいことを確認してから全量実験へ進む。

## 将来検討（本実験の範囲外）

category/taxonomyを利用する研究案は、text-only基準線の確立後に別計画として検討する。候補は、同一のcategory APIをone-shot方式とiterative agentの双方へ与え、category accessの有無と検索方式の交互作用を測る設計である。この案の新規性、データセット、評価プロトコルは未確定であり、本実験の結論として扱わない。

## 主要参考文献

- Sam O'Nuallain et al. [AutoIndex: Learning Representation Programs for Retrieval](https://arxiv.org/abs/2607.18603), 2026.
- Zeyu Yang et al. [Superintelligent Retrieval Agent: The Next Frontier of Agentic Retrieval](https://arxiv.org/abs/2605.06647), 2026.
- Zirui Guo et al. [LightRAG: Simple and Fast Retrieval-Augmented Generation](https://aclanthology.org/2025.findings-emnlp.568/), 2025.
- Peng Qi et al. [Answering Complex Open-domain Questions Through Iterative Query Generation](https://arxiv.org/abs/1910.07000), 2019.
- Yunchang Zhu et al. [Adaptive Information Seeking for Open-Domain Question Answering](https://aclanthology.org/2021.emnlp-main.293/), 2021.
- Harsh Trivedi et al. [Interleaving Retrieval with Chain-of-Thought Reasoning for Knowledge-Intensive Multi-Step Questions](https://arxiv.org/abs/2212.10509), 2023.
- Shunyu Yao et al. [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629), 2023.
