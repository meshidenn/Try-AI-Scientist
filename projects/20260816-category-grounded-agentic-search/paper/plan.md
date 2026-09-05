# Paper Plan

## Mode And Status

- Mode: Proposal Mode
- Status: 計画中・未実装・未実行
- Canonical manuscript: `paper/draft.md`
- Canonical experiment design: `RESEARCH_PLAN.md` と `experiments/exp-001/spec.yaml`
- Results artifact: 未作成

Proposal Modeでは、未実行の数値、順位、改善率、成功を原稿へ入れない。仮説と予定する分析は、実験結果と明確に区別する。

## Research Question

multi-hop 検索に必要な情報は、語彙拡張、本文由来グラフ、専門家構造によってどこまで検索前に吸収でき、どの残りに対して取得証拠を観察する agentic search が必要になるのか。

## Central Hypotheses

- H1: 語彙ギャップが主因の設問では SIRA 型検索が agentic search に近づく。
- H2: 質問文から予測できる複数文書関係が主因の設問では LightRAG 型検索が agentic search に近づく。
- H3: MeSH 等の専門家構造は、専門用語の正規化・同義語・階層・型制約に依存する設問で one-shot 手法を改善し、agentic search の追加的優位を縮小する。
- H4: 先行証拠から初めて判明する bridge entity、制約、探索順序については、専門家構造を与えても agentic search の優位が残る可能性がある。H4は事後trajectory診断で検証する。

## Intended Contributions

実験後に支持される範囲で、以下を貢献候補とする。

1. multi-hop の困難を、語彙表現、本文由来関係、専門家構造、証拠条件付き探索という検索段階に分解する評価枠組み。
2. SIRA、LightRAG、agentic searchを同一 corpus、同一 reader、同一 cumulative top-N候補予算で比較する実験プロトコル。
3. retrieval depth `N` と agent turn `T`、latency、token costを分離した運用上の分析。
4. MeSH有無と方式の交互作用により、専門家構造がagentic searchの限界優位を代替する範囲を分析する設計。

## Section Outline

| Section | 目的 | 中心claim | 必要evidence | Proposal Mode制約 |
| --- | --- | --- | --- | --- |
| Title / Abstract | 問いと設計を短く示す | 実験前は問い・設計のみ | `RESEARCH_PLAN.md` | 結果数値を書かない |
| 1. Introduction | 背景、gap、問い、仮説、貢献を提示 | multi-hopを検索段階に分解する | 先行研究citation、research plan | 新規性を断定しない |
| 2. Related Work | multi-hop、SIRA、LightRAG、agentic search、MeSHを位置づける | 本研究の比較軸を明確化 | `survey/sources.md` | 先行研究の条件を混同しない |
| 3. Research Question and Hypotheses | 仮説と反証可能な差分を定義 | H1-H4 | `RESEARCH_PLAN.md` | 仮説を結果として書かない |
| 4. Method / Experimental Design | 条件、構造、one-shot/closed-loopを定義 | 同じ corpus と候補予算で比較する | `experiments/exp-001/spec.yaml` | 実行済み表現を使わない |
| 5. Evaluation Protocol | metric、N、T、K、latencyを定義 | 性能と運用費を分けて測る | spec、データ監査結果 | 未選定のPubMed datasetは候補と明記 |
| 6. Results | 実測値を提示する | TBD | results、scores、figures | Proposal Modeでは空の構造のみ |
| 7. Analysis and Limitations | 交互作用とtrajectoryを解釈する | TBD | artifact audit、result interpretation | 先に結論を決めない |
| 8. Conclusion | 計画上の意義をまとめる | 何を判定するか | research plan | 結果を暗示しない |

## Claim-Evidence Map

| claim_id | claim | status | citation | artifact | allowed_mode |
| --- | --- | --- | --- | --- | --- |
| C1 | multi-hop QAの複数証拠要求は、証拠条件付き検索の必要性を全設問で保証しない | citation-supported | HotpotQA、2WikiMultiHopQA、MuSiQue |  | Proposal / Data-Aware |
| C2 | SIRAは語彙拡張を主な検索前処理として扱う | citation-supported | SIRA |  | Proposal / Data-Aware |
| C3 | LightRAGは本文由来entity/relation graphでlocal/globalな文脈を取得する | citation-supported | LightRAG |  | Proposal / Data-Aware |
| C4 | 先行証拠に基づき次のqueryを更新するiterative retrievalは既知の研究系譜である | citation-supported | GoldEn、AISO、IRCoT、ReAct |  | Proposal / Data-Aware |
| C5 | SIRA、LightRAG、agentic searchを同一条件で比較する | planned |  | `RESEARCH_PLAN.md`, `experiments/exp-001/spec.yaml` | Proposal / Data-Aware |
| C6 | cumulative top-Nを固定し、agent turn Tをアブレーションする | planned |  | `experiments/exp-001/spec.yaml` | Proposal / Data-Aware |
| C7 | MeSHの有無は方式別に測定できる | planned | MeSH、研究計画 | PubMed/MeSH feasibility audit（未作成） | Proposal / Data-Aware |
| C8 | SIRAまたはLightRAGがagentic searchの限界優位を代替する条件 | not-yet-tested |  | 実験結果（未作成） | Data-Aware only |
| C9 | MeSH後も残るagent優位は、証拠依存のbridge discoveryと関係する | not-yet-tested | iterative retrieval先行研究 | trajectory artifact（未作成） | Data-Aware only |

## Citation Map

- multi-hop QA: HotpotQA、2WikiMultiHopQA、MuSiQue
- query/document expansion: SIRA
- corpus-derived graph: LightRAG
- evidence-conditioned retrieval: GoldEn Retriever、AISO、IRCoT、ReAct
- expert structure: MeSH
- research workflow context: Spark-to-Paper

詳細なtitle、authors、year、URL、projectへの関係は `survey/sources.md` を正本とする。

## Planned Tables And Figures

| ID | 内容 | 状態 | 必要artifact |
| --- | --- | --- | --- |
| Table 1 | 方式と事前構造化・closed-loopの対応 | 計画済み | research plan |
| Table 2 | `方式 × 構造 × N × T` の実験条件 | 計画済み | spec、data manifest |
| Table 3 | Retrieval / answer / costの結果 | TBD | results/scores、logs |
| Figure 1 | one-shotとclosed-loopの情報フロー | 計画済み | method description |
| Figure 2 | NとTに対する性能・latency曲線 | TBD | scores、logs |
| Figure 3 | MeSH有無による方式間交互作用 | TBD | PubMed/MeSH results |

## Unsupported Or Prohibited Claims

- Agentic searchがmulti-hop全般に必須である。
- 標準multi-hop datasetの全設問がevidence-dependentである。
- SIRA、LightRAG、agentic searchのいずれかが常に最良である。
- MeSHがagentic searchを一般に代替する。
- 実験前の仮説を実験結果として述べる。
- 原論文と異なるbackend、LLM、corpus、budgetで完全再現したと述べる。

## Open Inputs And Decisions

- MeSHを利用する主実験のPubMed datasetを確定する。
- MedHop、BioASQ等の候補についてdocument ID coverage、MeSH snapshot時点、evidence/qrelsを監査する。
- `N` と `T` のpilot条件およびagentのquery APIを実装前に固定する。
- graph construction、SIRA enrichment、MeSH mappingのoffline costを記録する形式を決める。
- Data-Aware Modeへの移行は、artifact audit後に行う。
