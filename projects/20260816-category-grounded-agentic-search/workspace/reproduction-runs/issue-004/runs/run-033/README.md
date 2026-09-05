# exp-033: UltraDomain全量トリプル再抽出

## 目的

UltraDomainの61 unique contextを対象に、Qwenの停止しない反復を抑制する設定でLightRAGのentity/relation抽出を全量実行し、後続のBGE-M3 embedding/index作成に渡す正本のtriplet artifactを確定する。

## 結果

61文書すべてが`processed`で完了し、失敗文書は0件だった。61行の`triplets.jsonl`を`data/derived/`へexportした。

## 再現

プロジェクト直下で次を実行する。

```bash
uv run python -m category_grounded_agentic_search.interfaces.lightrag_reproduction \
  --root workspace/reproduction-runs/issue-004/runs/run-033 --index-only --extract-json \
  --extract-max-tokens 32768 --repetition-penalty 1.05 --embedding-model hash
```

実行後、`category_grounded_agentic_search.interfaces.derived_artifacts`でLightRAG storeからtriplet artifactをexportする。

## 設定上の判断

重複禁止プロンプト、entity 30 / relation 50の抽出上限、`repetition_penalty=1.05`、および停止済み応答の反復検出を警告扱いにする判断は、共有の[DECISION.md](../../data/derived/triplets/UltraDomain--aa8a51d523f8fc3c5a0ab90dd16b7f6b9dbb5d0d/Qwen--Qwen3.6-35B-A3B-FP8/DECISION.md)に記録している。
