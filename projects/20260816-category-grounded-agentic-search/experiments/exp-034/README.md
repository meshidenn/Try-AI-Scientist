# exp-034: BGE-M3 LightRAG vector index

## 目的

exp-033で確定した全量tripletとLightRAG graph/chunkを再利用し、Qwen抽出を再実行せずにBGE-M3 dense embeddingによるLightRAG vector indexを作成する。

## 再現

プロジェクト直下で、次の実行器を用いる。

```bash
uv run python -m category_grounded_agentic_search.interfaces.bge_m3_index --help
```

入力と出力の正確なpath、設定、結果は`spec.yaml`、`results/`、`logs/`に記録する。

## 結果

全45,525 vector（chunk 1,375、entity 20,281、relationship 23,869）をBGE-M3の1,024次元dense vectorとして作成した。indexは`data/derived/indexes/`を正本とする。
