# exp-009: 4096 tokenでのLightRAG論文プロトコル準拠Qwen variant実装確認

exp-008で2048 token抽出が別documentでtruncationしたため、同じ短文subset・query protocolに対しextract roleのmax_tokensのみを4096へ増やす。
