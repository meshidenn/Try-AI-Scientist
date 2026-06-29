# search

研究候補を探索する層。

AI Scientist v2のagentic tree searchとAlphaEvolve系のprogram databaseを参考に、候補、score、差分、失敗理由を保存しながら次の実験を選ぶ。

想定する責務:

- ideaやcandidate runの登録
- exploitation/explorationの選択
- 過去runから次promptへ渡すcontextの生成
- best candidateと未探索candidateの管理
- `review/next-plan.md` を読み、次に試すcandidateを選ぶ
