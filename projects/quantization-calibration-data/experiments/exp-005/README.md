# exp-005: LLM-jp Japanese Data Language Calibration

This experiment re-runs the NVFP4 W4A4 Japanese-vs-English calibration-language comparison with an LLM-jp Japanese instruction dataset.

The motivation is to avoid relying on the previous Japanese Dolly variant as the main Japanese source. The Japanese calibration and evaluation text are drawn from `llm-jp/llm-jp-instructions` (`v1.0/train`) through its converted parquet shard because the normal `datasets.load_dataset` path currently exposes a split-name mismatch in this environment.

The metric is held-out next-token NLL. This is an accuracy/degradation comparison, not a speed benchmark.
