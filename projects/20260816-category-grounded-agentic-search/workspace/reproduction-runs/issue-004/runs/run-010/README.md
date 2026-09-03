# exp-010: 8192 tokenでのLightRAG論文プロトコル準拠Qwen variant実装確認

exp-009で4096 token抽出がtruncationしたため、同じ短文subset・query protocolに対しextract roleのmax_tokensのみを8192へ増やす。
