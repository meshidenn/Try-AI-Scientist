# Artifact Audit

## Verdict

PASS with warnings.

## Checked Artifacts

- `spec.yaml`, `README.md`, runner、集約・分析script
- 72 benchmark JSON、72 benchmark log
- 6 target/spec variantのserver logとcontainer ID
- `results/scores.json`, `results/factorial-analysis.json`, `results/results.md`

## Integrity Checks

- benchmark JSONは72/72、一意なlabelも72。
- 全1,152 requestが成功し、各cellは`completed=16`, `failed=0`。
- output tokenはworkloadごとに16,384、24,576、32,768で、指定output長 x 16 requestと一致。
- `scores.json`は`status=completed`、36/36のBF16/FP8対応比較を保持。
- server logでvLLM v0.24.0、BF16/FP8 model、MTP assistant、spec tokens 4/8/16を確認。

## Warnings For Interpretation

- 各cellは1 runのみで、cell間のrun-to-run varianceは未測定。
- random promptの内容によってacceptanceとtail latencyが大きく変動する。
- 個別のmetrics snapshotファイルは保存されていない。acceptance集計値はbenchmark JSONに埋め込まれ、variant単位の時系列はserver logに残る。
- 実職場のagent trace、tool-call API、arrival processは再現していない。

## Blocking Issues

なし。
