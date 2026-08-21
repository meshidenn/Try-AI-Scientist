# exp-001: BF16 versus NVFP4 W4A4 serving benchmark

Gemma 4、Qwen3.5、Qwen3-30B-A3B MoEについて、同一GPU・同一vLLM imageでBF16とNVFP4 W4A4を比較する。

Qwen3.5-4BのNVFP4 artifactだけはこのexperimentの実行時に量子化して生成する。その他のモデルはローカルHF cacheのsnapshotを入力とする。

## Reproduction

```bash
uv run python projects/fp4-tensorcore-benchmark/workspace/quantize_qwen35_nvfp4.py \
  --model /home/hiroki/.cache/huggingface/hub/models--Qwen--Qwen3.5-4B/snapshots/851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a \
  --output projects/fp4-tensorcore-benchmark/experiments/exp-001/outputs/models/qwen35-4b-nvfp4
uv run python projects/fp4-tensorcore-benchmark/workspace/run_benchmark.py \
  --root projects/fp4-tensorcore-benchmark/experiments/exp-001
```

## Scope

結果はserving性能の比較であり、品質・accuracyの比較は含めない。FP4利用判定はvLLM起動ログのkernel選択と実行成功に基づき、命令単位のTensor Core counter測定は別タスクとする。
