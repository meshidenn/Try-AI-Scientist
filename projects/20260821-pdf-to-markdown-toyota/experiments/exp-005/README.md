# Experiment exp-005

## Objective

PaddleOCR-VL-1.6、MinerU2.5-Pro、DeepSeek-OCR-2、Unlimited-OCRを、Toyota PDFの4ページpilotでローカル実行する。各モデルのnative出力をMarkdownへ正規化し、既存VLM pilotと同じ軽量自動指標で確認する。

## Status

`planned`。重み取得と公式runtimeの起動可否を確認後、候補ごとに実行済み・失敗・未実行を分けて記録する。

## Input

入力PDFは[`inputs/source-manifest.json`](inputs/source-manifest.json)で参照する既存snapshotを使用する。対象ページは[`inputs/pilot-pages.json`](inputs/pilot-pages.json)の4ページである。

## Constraints

- 外部OCR APIおよびSaaSは使わない。
- 新規の実装はproject packageの`src/pdf_to_markdown_toyota/`にのみ置く。
- モデルの制御token・検出bboxなどはraw outputとして残し、Markdown評価用の後処理と区別する。

詳細な条件は[`spec.yaml`](spec.yaml)を正本とする。
