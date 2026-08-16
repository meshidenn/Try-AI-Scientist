# 事前構造化と Agentic Search の境界

## Draft status

計画中の研究論文ドラフト。実験結果はまだ得られていないため、本稿の主張は研究課題、仮説、評価設計に限定する。

## 1. はじめに

大規模言語モデル（LLM）を検索システムと組み合わせる Retrieval-Augmented Generation（RAG）では、質問に対する回答を得るために単一の文書ではなく複数の証拠を組み合わせる必要がある。このような multi-hop の質問では、検索対象となる文書が存在していても、質問文と文書の語彙が一致しない、複数文書の関係を明示的に辿る必要がある、あるいは最初に取得した証拠を読まなければ次の探索先が分からない、といった異なる困難が生じる。

これらの困難に対して、既存手法は multi-hop の処理を異なる段階へ移している。SIRA は document-side と query-side の語彙拡張を行い、同義語、略語、専門用語などの語彙ギャップを検索前に吸収する。LightRAG は文書本文から entity と relation を抽出してグラフを構築し、複数文書にまたがる関係を検索時に利用する。一方、agentic search は検索結果を観察し、その結果に応じて次の query や検索先を決定する。この方式では、最初の質問から事前に予測しにくい bridge entity や制約を、逐次的な検索行動の中で発見できる。

しかし、multi-hop QA が複数証拠を要求することは、必ずしも証拠を取得するまで次の検索要求が確定しないことを意味しない。質問文に必要な実体がすでに含まれている場合や、語彙拡張・文書由来グラフによって必要な候補を一度に取得できる場合、multi-hop の回答であっても検索は one-shot で完了しうる。したがって、agentic search の優位を単に multi-hop という問題分類から推定することはできない。

本研究では、multi-hop 検索の困難を「検索前にどこまで構造として吸収できるか」という観点から分解する。具体的には、語彙拡張を行う SIRA 型検索、本文から entity/relation graph を誘導する LightRAG 型検索、取得結果を観察して再検索する agentic search を、同一 corpus と同一の候補 passage 予算の下で比較する。さらに、専門家が整備した概念階層・同義語・型情報の寄与を調べるため、MeSH を利用できる条件を追加する。ここで MeSH は単に人手で作成されたグラフではなく、明示的な概念の正規化と階層を持つ構造として扱う。

本稿の中心的な問いは次である。

> multi-hop 検索に必要な情報は、語彙拡張、本文由来グラフ、専門家構造によってどこまで事前に吸収でき、どの残りに対して agentic search の閉ループ探索が必要になるのか。

この問いに答えるため、one-shot 手法と agentic search の検索回数を単純に同一化しない。複数回の観察と query 更新は agentic search の処置そのものだからである。その代わり、query 全体で観察できる cumulative top-(N) passage 数と、最終 reader に渡す top-(K) passage 数を固定し、agent の最大 turn 数 (T) と retrieval depth (N) を独立にアブレーションする。これにより、agent の性能向上を、より多くの文書を読む効果と、検索結果に応じて探索を配分する効果に分けて評価する。

本研究では、まず HotpotQA、2WikiMultiHopQA、MuSiQue を用いた本文由来構造のみの較正実験を行う。この実験は、標準 multi-hop ベンチマークにおける既存の傾向を共通条件で確認するためのものであり、agentic search の一般原理を新規に主張するものではない。続いて、同一の PubMed snapshot に MeSH annotation を対応付けられる multi-hop QA/evidence set を選定し、`方式 × MeSH の有無` の因子実験を行う。MeSH の有無による agentic search の限界優位の変化は、同一 PubMed corpus 内でのみ解釈する。

本研究で検証する仮説は三つである。第一に、語彙ギャップが主因の設問では SIRA が agentic search に近づき、質問文から予測できる文書間関係が主因の設問では LightRAG が近づくと予測する。第二に、MeSH を与えることで、専門用語の正規化、同義語、上位・下位概念、型制約を必要とする設問において one-shot 手法が改善し、agentic search の追加的優位が縮小すると予測する。第三に、最初の証拠が未知の bridge entity や次の探索制約を明らかにする設問では、MeSH と本文由来グラフを与えても agentic search の優位が残ると予測する。第三の仮説は設問に事前ラベルを付与して検証するのではなく、agent trajectory と gold evidence の事後照合によって診断する。

本研究の貢献は、以下の三点を予定している。

1. multi-hop の困難を、語彙拡張、本文由来関係グラフ、専門家構造、証拠条件付き探索という検索段階の違いとして整理する。
2. SIRA、LightRAG、agentic search を、同一 corpus、同一 reader、同一 cumulative top-(N) 予算の下で比較し、agent の turn 数と retrieval depth の効果を分解する。
3. MeSH の有無を方式ごとに操作し、専門家構造が agentic search の限界優位をどの種類の検索困難で代替するかを、方式と構造の交互作用として分析する。

## 2. 関連研究

### 2.1 Multi-hop open-domain question answering

HotpotQA は Wikipedia を対象とし、複数の supporting facts を組み合わせる質問を提供する。2WikiMultiHopQA は Wikipedia と Wikidata に由来する関係を含む質問を、MuSiQue は複数の単一段階質問を composition して作られた質問を扱う。これらは複数証拠の取得・統合を評価する基盤として有用であり、本研究の本文由来構造のみの較正実験で利用する。

ただし、これらのデータセットが保証するのは主に複数証拠の必要性である。各質問について、最初の検索結果を読まなければ次の query を決められないことが明示的にラベル付けされているわけではない。したがって、本研究では multi-hop というデータセット分類だけから agentic search の必要性を推論せず、one-shot 条件と closed-loop 条件の差、および取得 trajectory の事後分析を用いる。

### 2.2 Query expansion と document expansion

Query expansion は、質問に含まれない同義語、関連語、専門語などを追加することで、query と文書の語彙不一致を緩和する。Document expansion は、索引時に文書へ別表記や関連語を付加し、検索時の lexical mismatch を減らす。これらは検索を実行する前に検索可能な表現を増やすため、本研究では open-loop の事前吸収に位置づける。

SIRA（Superintelligent Retrieval Agent）は document-side expansion と query-side expansion を組み合わせ、corpus statistics に基づく DF filtering で生成語を制御する。主な retrieval 操作を一回の weighted BM25 に圧縮する点が特徴である。SIRA は検索 query の語彙ギャップや rare discriminative term に対して直接的な手段を提供する一方、取得結果を読んだ後に次の query を変更する closed-loop 検索とは異なる。本研究では、SIRA を「multi-hop を語彙表現の段階で事前に吸収する」代表として扱う。

### 2.3 GraphRAG と LightRAG

GraphRAG 系手法は、文書断片を直接検索するだけでなく、entity、relation、community、theme などの構造を利用して複数文書を集約する。これにより、質問文と各根拠文書が直接 lexical に一致しない場合でも、文書内に現れる関係を介して証拠を取得できる。

LightRAG は、文書 chunk から entity と relation を LLM で抽出し、node と edge の profile を持つ graph を構築する。query 時には低レベルの entity detail と高レベルの概念・theme を併用し、関連 entity、relation、text chunk を生成器へ渡す。SIRA が主に語彙の展開を行うのに対し、LightRAG は本文から誘導した関係構造により複数文書の集約を行う。

本研究では、LightRAG の graph retrieval を open-loop として扱う。LightRAG が一つの query に対して複数の graph channel を使うこと自体は、取得結果を観察して次の検索意図を変更することとは異なるためである。また、後続実験では MeSH node と hierarchy edge を LightRAG 型 graph に追加する条件を設け、本文由来 graph と専門家構造の寄与を分離する。

### 2.4 Iterative retrieval と Agentic Search

取得した証拠を用いて次の query を生成する iterative retrieval は、agentic search に先行する重要な系譜である。GoldEn Retriever は利用可能な文脈から不足した entity を検索し、AISO は情報取得と推論の行動を適応的に選択する。IRCoT は reasoning と retrieval を交互に実行し、ReAct は reasoning trace と search action を組み合わせる。これらの研究は、次の query が先行証拠から生成されるという設定を明示している。

これらの先行研究から、証拠条件付きの検索が有効になりうることは既に知られている。本研究の目的はこの原理を再発見することではない。SIRA の語彙拡張や LightRAG の本文由来 graph、さらに MeSH の専門家構造を同じ corpus に与えたとき、agentic search の追加的な価値がどのように変化するかを測る点にある。

また、本研究は RL による検索方策の学習を扱わない。agentic search の最大 turn 数 (T) を操作し、同じ cumulative top-(N) 候補予算で、観察後の query 更新がもたらす品質・latency・token cost の変化を測定する。これにより、学習済み方策の差ではなく、検索時の closed-loop 制御そのものを分析する。

### 2.5 専門家構造、Ontology、Knowledge Graph

MeSH（Medical Subject Headings）は、医学文献に付与される descriptor と entry term、さらに概念階層を提供する専門家整備の語彙体系である。MeSH は文書本文から抽出した関係 graph と同じ意味ではない。前者は概念の正規化、同義語、上位・下位関係、分類上の意味を明示するのに対し、後者は corpus 内の文章から entity と relation を誘導し、抽出誤差や未観測関係の影響を受ける。

一般に、category は実体や文書の所属集合、ontology は概念・属性・関係・制約のスキーマ、knowledge graph は実体間の個別事実を表す。これらは相互排他的ではなく、ontology を用いて knowledge graph を記述したり、category を graph の node と edge として表現したりできる。本研究で測定したいのは名称の違いではなく、構造の情報源と意味の明示性が検索に与える寄与である。

MeSH 条件では、SIRA に descriptor と entry term を展開し、LightRAG に MeSH node と hierarchy edge を追加し、agentic search に同じ descriptor/hierarchy lookup を提供する。したがって、専門家構造の有無を方式間で共有しながら、one-shot と closed-loop の利用タイミングを比較できる。

### 2.6 本研究の位置づけ

既存研究は、語彙拡張、文書由来 graph、iterative retrieval、専門家 ontology をそれぞれ異なる corpus・検索 backend・LLM・評価予算で評価している。そのため、報告されたスコアの差だけから「どの方式が multi-hop を解消したか」を判断することは難しい。

本研究は、これらの方式を一つの万能なランキングに並べるのではなく、検索制御と構造情報を因子として分ける。本文由来構造のみの実験では、SIRA、LightRAG、agentic search の共通基準線を作る。MeSH を含む実験では、同一 PubMed snapshot 内で `方式 × 構造の有無` を操作する。さらに cumulative top-(N) と agent turn 数 (T) を記録し、性能だけでなく latency・token cost・trajectory を分析する。

この設計により、次の三つの結果を区別できる。第一に、SIRA または LightRAG が agentic search に近づくなら、該当する multi-hop の困難は検索前の語彙・関係構造によって吸収可能である。第二に、MeSH により one-shot 手法が改善し agent の追加的優位が縮小するなら、専門家構造が事前探索の代替になる。第三に、それらの構造を与えても agent の優位が残るなら、証拠を観察して初めて決まる探索順序や bridge discovery が残差として存在することを示唆する。ただし、これらは実験結果に基づいて初めて判断されるものであり、本稿の計画段階では結論として主張しない。

## 参考文献候補

本節の詳細な出典とデータセット情報は、[survey/sources.md](../../../survey/sources.md) に管理する。

- SIRA: [Superintelligent Retrieval Agent](https://arxiv.org/abs/2605.06647)
- LightRAG: [Simple and Fast Retrieval-Augmented Generation](https://aclanthology.org/2025.findings-emnlp.568/)
- GoldEn Retriever: [Answering Complex Open-domain Questions Through Iterative Query Generation](https://arxiv.org/abs/1910.07000)
- AISO: [Adaptive Information Seeking for Open-Domain Question Answering](https://aclanthology.org/2021.emnlp-main.293/)
- IRCoT: [Interleaving Retrieval with Chain-of-Thought Reasoning for Knowledge-Intensive Multi-Step Questions](https://arxiv.org/abs/2212.10509)
- ReAct: [Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- HotpotQA: [A Dataset for Diverse, Explainable Multi-hop Question Answering](https://aclanthology.org/D18-1259/)
- 2WikiMultiHopQA: [A Multi-hop Question Answering Dataset for Comprehensive Evaluation of Natural Language Inference](https://aclanthology.org/2020.coling-main.580/)
- MuSiQue: [Multi-hop Questions via Single-hop Question Composition](https://aclanthology.org/2022.tacl-1.31/)
- MeSH: [Medical Subject Headings](https://www.nlm.nih.gov/mesh/meshhome.html)
