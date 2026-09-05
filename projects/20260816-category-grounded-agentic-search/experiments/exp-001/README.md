# exp-001: Open-loop と Closed-loop の Text-derived Retrieval 比較

## Status

設計済み。Phase 1 では実データを取得・実行せず、入力manifest、候補予算、評価器の形式だけを固定する。

## Inputs

- `inputs/pilot_corpus_manifest.json`: evaluator と loader の動作を検証する合成fixture。実験結果や公開ベンチマークのsnapshotではない。
- `inputs/pilot_queries.jsonl`: 同じく unit/integration test 用の最小query・gold evidence対応。

実データの corpus manifest は、HotpotQA、2WikiMultiHopQA、MuSiQue の配布版・split・document/passage ID mapping を監査後に追加する。

## Reproduction

project直下で次を実行する。

```bash
uv run python -m category_grounded_agentic_search.interfaces.cli validate-manifest \
  experiments/exp-001/inputs/pilot_corpus_manifest.json
uv run python -m unittest discover -s tests -v
```

## Artifact policy

実行ごとの出力は `outputs/`、評価結果は `results/`、run log は `logs/` に保存する。実装コードとtestはproject直下の `src/` と `tests/` にのみ置く。
