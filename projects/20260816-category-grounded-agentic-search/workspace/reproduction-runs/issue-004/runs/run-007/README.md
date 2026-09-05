# exp-007: LightRAG論文プロトコル準拠Qwen variantの実装確認

UltraDomainの固定revisionから少数のunique contextを選び、Qwenで高水準queryと回答を生成する。`hybrid`と`naive`をGPT-4o-miniのpairwise LLM-as-a-judgeで比較し、全unique context index化の前に再現実装を確認する。
