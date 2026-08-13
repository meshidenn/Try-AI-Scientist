# Experiment exp-004

## Objective

外部APIを使わず、ローカルGPU上の文書パーサ専用モデルと汎用VLMを、Toyotaの4種の企業PDFで比較する。

## Status

`partial_completed`。Qwen3.6-27B、InternVL3.5-8B、GLM-4.6V-Flash の4ページpilot（image-first / hybrid）は実行済みである。InternVLは技術的には応答したが、意味を成さない出力のため比較対象から除外した。専用文書パーサ候補は未実行である。pilotを通過したモデルだけ、既存の11ページsampleへ拡張する。

## Input

入力PDFは [`inputs/source-manifest.json`](inputs/source-manifest.json) の既存snapshotを参照する。exp-001のhistorical inputを移動・変更しない。

## Comparison Rules

- 外部推論API、クラウドOCR、SaaSは使わない。
- Qwen、InternVL、GLMなどvLLM対応の汎用VLMはローカルvLLMだけで実行する。localhostのOpenAI互換HTTPは外部APIではない。
- PaddleOCR、MinerU、dotsなどは、公式のローカル実装がvLLMを前提にしない場合、その公式ローカル経路を使う。
- 比較のprimary outputはMarkdownとする。HTMLはpilot後に上位2モデルへ限定して別条件で評価する。
- `not_run` は失敗ではなく、ローカル互換性・モデル取得・GPU制約の根拠をlogへ残した状態を表す。

詳細な仮説、候補、指標は [`spec.yaml`](spec.yaml) を正本とする。
