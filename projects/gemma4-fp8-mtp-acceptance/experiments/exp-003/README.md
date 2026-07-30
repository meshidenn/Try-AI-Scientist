# exp-003: Long-IO Concurrency x Spec-Depth Sweep

3つのlong-IO random workloadについて、target、concurrency、MTP
`num_speculative_tokens`のfactorial matrixを同一条件で測定する。

```bash
bash projects/gemma4-fp8-mtp-acceptance/experiments/exp-003/workspace/run_factorial_matrix.sh
uv run python projects/gemma4-fp8-mtp-acceptance/experiments/exp-003/workspace/summarize_results.py
uv run python projects/gemma4-fp8-mtp-acceptance/experiments/exp-003/workspace/analyze_factorial.py
```

runnerは`completed=16`かつ`failed=0`の既存resultをskipする。中断後は同じコマンドで再開できる。

個別variantだけ再開する場合:

```bash
VARIANTS=fp8_s8,fp8_s16 bash projects/gemma4-fp8-mtp-acceptance/experiments/exp-003/workspace/run_factorial_matrix.sh
```

## Results

- [詳細結果](results/results.md)
- [構造化結果](results/scores.json)
- [要因分析](results/factorial-analysis.json)
- [artifact audit](review/artifact-audit.md)
- [結果解釈](review/result-interpretation.md)
