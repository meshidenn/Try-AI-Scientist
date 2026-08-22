# 研究計画: 事前構造化と Agentic Search の境界

## Status

**計画中。未実装・未実行。**

### Current Execution Scope (Issue #2, 2026-08-22)

この文書のうちHotpotQA、2WikiMultiHopQA、MeSHを含む将来計画はProposal Modeの設計案として残す。現在実行する正本はIssue #2と`experiments/exp-001/spec.yaml`であり、FanOutQA、FRAMES、MuSiQue、HDS-QAを対象に、`Qwen/Qwen3.6-35B-A3B-FP8`を固定してSIRA型・LightRAG型を比較する。

- datasetの採用は`data/dataset_manifest.json`で`accepted`になったものに限定する。
- LightRAGのQwen再評価は`experiments/exp-002/spec.yaml`で管理する。corpusを変更せず、LLM変更を伴う再評価と表現する。
- Sequential / Parallel agentはIssue #6 / #7で保留中であり、実装方針が決まるまで実行しない。

本書を研究全体の設計正本とする。`experiments/exp-001/spec.yaml` は、外部の人手構造を使わない基準線実験の仕様である。MeSH を含む主実験は、入力データ監査後に別 experiment として固定する。

## 中心となる問い

> multi-hop 検索に必要な情報は、検索前にどこまで語彙・本文由来グラフ・専門家構造として吸収できるか。吸収し切れない残りに対して、取得証拠を観察して次の検索を選ぶ agentic search はどの程度の限界優位を持つか。

ここでいう agentic search は、取得結果を観察して query または検索先を更新する **closed-loop** 検索である。RL による方策学習は本研究の対象に含めない。

## 背景と位置づけ

multi-hop QA が複数証拠の統合を要求することと、各設問が「先の証拠を読まなければ次の query を決められない」ことは同じではない。HotpotQA、2WikiMultiHopQA、MuSiQue は前者を評価する有用なベンチマークだが、後者を設問単位で保証するものではない。

既存研究は、異なる場所に multi-hop の困難を配置している。

| 困難を吸収する場所 | 代表方式 | 検索時の性質 |
| --- | --- | --- |
| 語彙・表記・予測可能な制約 | SIRA 型 query/document expansion | open-loop one-shot |
| corpus 内の entity/relation | LightRAG 型本文由来グラフ | open-loop one-shot |
| 専門概念、同義語、階層、型制約 | MeSH 等の専門家構造 | one-shot または closed-loop の双方で利用可能 |
| 先行証拠で初めて判明する bridge entity・制約・探索順序 | agentic search | closed-loop iterative |

本研究は agentic search の一般原理を新規に主張しない。共通 corpus・共通出力条件で、事前構造化が agentic search の**限界優位**をどの種類の困難で代替するかを分解する。

## 仮説

### H1: 語彙・関係の事前吸収

query と根拠の間の語彙ギャップが主因なら SIRA が、質問文から予測できる複数文書関係が主因なら LightRAG が、agentic search の性能に近づく。

### H2: 専門家構造の代替効果

MeSH を与えると、専門用語の正規化、同義語、上位・下位概念、型制約に依存する検索で one-shot 手法が改善し、agentic search の追加的優位は縮小する。

### H3: 証拠条件付きの残差

MeSH と本文由来グラフを与えても、最初の証拠が未知の bridge entity または次の探索制約を明らかにする設問では、agentic search の優位が残る。

H3 は事前ラベルとして仮定しない。agent trajectory と gold evidence の照合による事後診断で評価する。

## 方式

### 主比較

| ID | 方式 | 制御の形 |
| --- | --- | --- |
| B0 | BM25 / fixed dense retriever | one-shot の較正対照 |
| M1 | SIRA 型検索 | document/query expansion 後に一回だけ検索 |
| M2 | LightRAG 型検索 | 本文由来 entity/relation graph を元 query から一回だけ検索 |
| M3 | Agentic search | 観察結果に基づき query を更新して再検索 |

SIRA は実行時の one-shot retrieval として扱う。LightRAG が内部で local/global retrieval を併用しても、取得結果を観察して次の検索意図を変更しない限り one-shot と定義する。

### 構造条件

| ID | 構造 | 内容 |
| --- | --- | --- |
| S0 | 構造なし | 文書本文、タイトル、通常 metadata のみ |
| S1 | MeSH | descriptor、entry term、broader/narrower hierarchy を利用可能にする |

MeSH は単に「人手作成」であることが LightRAG と異なるのではない。明示的な概念階層・正規化・型情報を持ち、corpus 抽出の coverage や関係抽出誤差に依存しない、という意味的な差を測る。

S1 では同じ MeSH snapshot を全方式に与える。SIRA は descriptor/entry term の展開、LightRAG は MeSH node と階層 edge の追加、agent は同じ descriptor/hierarchy lookup を観察後に利用できる。方式間で構造の情報源を変えない。

## 実験群

### 実験A: 本文由来構造のみの較正（exp-001）

HotpotQA FullWiki、2WikiMultiHopQA、MuSiQue を用い、S0 で M1/M2/M3 を比較する。目的は、標準 multi-hop データにおいて agentic search の差をどこまで語彙拡張・本文由来グラフで説明できるかを確認することにある。

これは既存主張の較正・再検証であり、単独では本研究の新規性を主張しない。

### 実験B: 専門家構造の因子実験（主実験、新規 spec を作成予定）

同一の PubMed snapshot と同一の multi-hop QA/evidence set に対し、`M1/M2/M3 × S0/S1` を実行する。MeSH の有無による差と、その差が方式によって異なるかを測る。

実行開始前に、以下を満たす corpus を固定する。

- QA の query と gold evidence が PubMed document ID に対応する。
- 各文書に、corpus snapshot 時点で利用可能だった MeSH annotation を対応付けられる。
- MeSH 更新時点が test answer・評価ラベルをリークしない。
- S0/S1 の全条件で、本文・文書ID・split・reader を完全に共有できる。

MedHop を第一候補、BioASQ 等を代替候補としてデータ監査する。候補名だけで採用を決めず、ID coverage、MeSH 時点整合性、qrels/evidence の品質を manifest に記録してから確定する。

実験Bの結論を実験Aの Wikipedia データへ直接一般化しない。MeSH の寄与と agentic search との交互作用は、必ず同一 PubMed corpus 内で解釈する。

## 予算設計とアブレーション

検索回数を方式間で揃えない。複数回の観察と query 更新は agentic search の処置そのものである。一方、query 全体で観察できる候補量と最終 reader 条件は揃える。

### 固定する量

- corpus snapshot、document/passage unit、query split、gold evidence mapping
- 最終 reader LLM と回答 prompt
- reader に渡す最終 passage 数 `K = 10` と context token 上限
- query 全体で返される passage slot の総上限 `N`
- LLM のモデル、temperature、最大 token と retry 方針

passage が重複して返っても、返却 slot は予算を消費する。unique passage 数は別指標として記録する。これにより、同じ文書を繰り返し取得して候補予算を実質的に増やすことを防ぐ。

### top-N と turn 数

`N` は検索候補の cumulative top-N、`T` は agent の最大 turn 数と定義する。

| 条件 | 候補取得 |
| --- | --- |
| SIRA / LightRAG | one-shot で top-N を取得し、最終 top-K を reader に渡す |
| Agentic search, T = 1 | 一回の query で top-N を観察する。適応はできない。 |
| Agentic search, T > 1 | `k_1 + ... + k_T <= N` を満たすよう各 turn で top-`k_t` を観察し、前 turn の観察後に次 query を選ぶ。 |

主アブレーションは `N ∈ {10, 25, 50, 100}`、`T ∈ {1, 2, 5, 10}` とする。`T > 1` では原則として `N` を turn 数で均等配分し、余りは最終 turn に配る。適応的な深さ配分は、均等配分の結果を解釈できてからの追加 ablation とする。

従って、例えば `N=100, T=5` の agent は各 turn で top-20 を観察し、one-shot 手法は一回で top-100 を取得する。いずれも reader は統合・deduplicate・rerank 後の top-10 のみを見る。

### 効率評価

候補量を固定しても、agent は観察を読むぶん query-time token と latency を消費する。この費用は消去せず、次を方式別・`N/T` 別に報告する。

- query latency の p50 / p95
- retrieval call 数と各 turn の latency
- LLM input/output token
- 返却 passage slot 数と unique passage 数
- SIRA enrichment / LightRAG graph construction の token、時間、index size

offline index 構築費は query 時費用と混ぜず、総費用と想定 query 件数での償却費を併記する。

## 評価と分析

### 指標

- Retrieval: Recall@K、nDCG@10、MRR、all-evidence recall、turn ごとの evidence coverage
- Answer: Exact Match、F1、grounded answer rate、unsupported claim rate
- Efficiency: 上記の token、latency、index cost、候補数

### 主な比較

1. 各 `N` において、SIRA・LightRAG と agent `T=1,2,5,10` を比較する。
2. 実験Bでは各方式について `S1 - S0` を測る。
3. MeSH が agent の限界優位を代替するかを、以下の差分の差で評価する。

```text
{Agent(S1) - Static(S1)} - {Agent(S0) - Static(S0)}
```

`Static` は SIRA と LightRAG のそれぞれに対して個別に計算する。最大値を一つの比較対象に固定して統計検定を不安定にしない。

4. agent の優位が大きい query について、後続 query に元 query に無い bridge entity・制約が現れたか、その語がどの観察 turn に由来するかを監査する。

query 単位の paired bootstrap confidence interval を基本とし、データセット、`N`、`T`、gold evidence 数、語彙重なり、relation/composition 型で層別する。

## リーク対策

- dev/test を厳密に分離する。
- SIRA enrichment と LightRAG graph construction に test query、answer、qrels を渡さない。
- MeSH は corpus snapshot 以前に利用可能だった版だけを使い、文書ID・descriptor・付与時点を保存する。
- test answer を query 拡張、prompt 調整、query 型分類に用いない。
- agent の prompt、tool call、観察 passage ID、返却順位を query 単位で保存する。

## 成功判定

本計画の成功は手法の勝利ではなく、次を満たすことである。

1. 同一 corpus 内で one-shot と agentic search を `N` と `K` を固定して比較できる。
2. `N` と `T` に対する性能・latency 曲線を再現可能な artifact として保存できる。
3. MeSH の有無について、方式別の主効果と `方式 × 構造` の交互作用を報告できる。
4. agent の優位を、trajectory evidence を伴わずに「証拠依存探索」と断定しない。

## 実施順序

1. 実験Aの小規模 pilot: corpus manifest、top-N 会計、trajectory log、reader 評価器を検証する。
2. 実験Aの `N × T` sweep: SIRA、LightRAG、agentic search の本文由来構造のみの曲線を得る。
3. PubMed/MeSH feasibility audit: benchmark と MeSH snapshot の ID・時点・evidence 対応を検証する。
4. 実験Bの spec 固定: S0/S1 の統一 representation、MeSH API、リーク対策を明文化する。
5. 実験Bの小規模 pilot と全量実験: `方式 × 構造 × N × T` を実行する。
6. artifact audit、結果解釈、claim audit を行う。

## 主要一次資料

- [SIRA](https://arxiv.org/abs/2605.06647)
- [LightRAG](https://aclanthology.org/2025.findings-emnlp.568/)
- [GoldEn Retriever](https://arxiv.org/abs/1910.07000)
- [AISO](https://aclanthology.org/2021.emnlp-main.293/)
- [IRCoT](https://arxiv.org/abs/2212.10509)
- [ReAct](https://arxiv.org/abs/2210.03629)
- [HotpotQA](https://aclanthology.org/D18-1259/)
- [2WikiMultiHopQA](https://aclanthology.org/2020.coling-main.580/)
- [MuSiQue](https://aclanthology.org/2022.tacl-1.31/)
