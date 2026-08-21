# 主要論文とデータセット

## このサーベイの使い方

本ファイルは `exp-001` の設計判断に直接用いる一次資料の索引である。報告値は原論文の条件に依存するため、方式間の数値比較には使わない。各手法は同一 corpus・同一予算で再評価する。

## 検索表現・索引の比較対象

| 資料 | 方式と位置づけ | 本研究への含意 |
| --- | --- | --- |
| [AutoIndex: Learning Representation Programs for Retrieval](https://arxiv.org/abs/2607.18603) (2026) | dev qrels を使い、文書をどの索引単位・表現に変換するかを offline で探索する。 | 実行時の反復検索とは異なる最適化である。`exp-001` には含めず、dev/test 分離が固まった後の追加 ablation とする。 |
| [Superintelligent Retrieval Agent (SIRA)](https://arxiv.org/abs/2605.06647) (2026) | document-side と query-side の語彙拡張を DF filtering で制御し、主に一回の BM25 検索へ圧縮する。BEIR と BrowseComp-Wikipedia を評価する。 | 語彙ギャップを open-loop に吸収する主比較手法。BrowseComp-Wikipedia では Wikipedia category を使うが、これは後続の category 実験の論点であり `exp-001` では除外する。 |
| [LightRAG: Simple and Fast Retrieval-Augmented Generation](https://aclanthology.org/2025.findings-emnlp.568/) (2025) | corpus 本文から entity/relation graph を抽出し、局所・大域の graph retrieval を組み合わせる。 | 人手 taxonomy ではなく、本文由来の構造が multi-document 集約をどこまで代替できるかを測る手法として採用する。 |

## 証拠条件付き・反復検索

| 資料 | 方式と位置づけ | 本研究への含意 |
| --- | --- | --- |
| [GoldEn Retriever](https://arxiv.org/abs/1910.07000) (2019) | 既取得文書の entity を用いて次の query を生成する iterative retrieval。 | 「次の query が先行証拠から生じる」設定は既知であり、本研究の新規主張にはしない。 |
| [AISO](https://aclanthology.org/2021.emnlp-main.293/) (2021) | 現在の証拠状態を基に retrieve / reason 行動を選ぶ adaptive information seeking。 | 取得結果への条件付けという closed-loop 比較の概念的先行研究。 |
| [IRCoT](https://arxiv.org/abs/2212.10509) (2023) | reasoning と retrieval を交互に行い、途中推論を次 query に反映する。 | RL を伴わない closed-loop agent の実装・比較の参照点。 |
| [ReAct](https://arxiv.org/abs/2210.03629) (2023) | reasoning trace と action を交互に出力し、検索・観察・再検索を行う。 | controlled iterative agent の action/observation log 形式の参照点。 |
| [Search-R1](https://arxiv.org/abs/2503.09516) (2025) | RL で search tool の使用を学習する agentic retrieval。 | 背景資料として参照するが、本研究は RL 方策を比較・実装しない。 |

## データセット

| 資料 | 含むもの | `exp-001` での役割と限界 |
| --- | --- | --- |
| [HotpotQA](https://aclanthology.org/D18-1259/) (2018) | Wikipedia を用いる multi-hop QA と supporting facts。 | 2-hop QA の代表的な診断対象。ただし、各設問で次の検索語が途中で初めて判明することは保証しない。 |
| [2WikiMultiHopQA](https://aclanthology.org/2020.coling-main.580/) (2020) | Wikipedia と Wikidata に由来する relation を含む multi-hop QA。 | relation 型ごとの分析に用いる。適応的検索の必要性を設問単位でラベル付けしてはいない。 |
| [MuSiQue](https://aclanthology.org/2022.tacl-1.31/) (2022) | compositional な multi-hop QA と supporting paragraphs。 | chain を用いた診断に適するが、open-loop では解けないことを全設問について意味しない。 |

## AI Scientist / Research Workflow

| 資料 | 方式と位置づけ | 本研究への含意 |
| --- | --- | --- |
| [Spark-to-Paper: End-to-End Research Paper Generation as a Composable Skill](https://arxiv.org/abs/2608.11924) (Qian et al., 2026; access: 2026-08-17) | 既存 coding assistant 内で13個の composable skill を実行し、文献検索、実験、claim revision、図生成、review を共有 artifact で接続する。計画と報告を分離し、deterministic integrity check と self-critique を組み合わせる。 | 本 project の `survey`、`spec`、実験結果、paper、review を分離する設計の近接先。検索方式のbaselineではなく、AI Scientist workflow と artifact-grounded claim 管理の関連研究として扱う。 |

## 設計上の結論

- multi-hop QA は「複数証拠が必要」を示すが、「証拠を見てからしか次の query を選べない」を保証しない。
- したがって `exp-001` は、事前ラベルだけで agent の必要性を断定しない。検索結果を見ずに query 群を確定する **open-loop** と、観察後に次行動を選べる **closed-loop** を同一予算で比較する。
- SIRA と LightRAG が強いなら、語彙・関係表現で吸収可能な multi-hop が多いことを示す。agentic search の優位は、turn 数と cumulative top-N を変えた closed-loop 条件で測る。
