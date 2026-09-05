# exp-007: LightRAG論文準拠 Qwen 再評価

Issue #4 の正式評価。UltraDomain Mix の全61 unique contextから、LightRAG公式再現コードの質問生成形式で125問を生成する。既存の全量 Qwen triplet / BGE-M3 indexを再利用し、LightRAG hybrid と naive の回答を比較する。

評価は参照回答・gold evidenceを用いない。論文と同じく、同一質問への二回答を回答順交互で GPT-4o-mini に与える pairwise LLM-as-a-judge とし、Overall Winner の勝率を主指標とする。

実行器は `category_grounded_agentic_search.interfaces.lightrag_reproduction` であり、出力先は本directoryを `--root` に指定する。raw answer、judge応答、vector/indexは再生成可能なためGit管理しない。
