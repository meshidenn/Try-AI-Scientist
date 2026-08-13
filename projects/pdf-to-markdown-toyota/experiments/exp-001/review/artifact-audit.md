# Artifact Audit

## 判定

選定ページ比較と32K context再試行のartifactは再現・追跡可能な状態で、条件付きで健全と判定する。

## 確認項目

- [x] 4資料の公式URL、SHA-256、ページ数を `workspace/input/documents.json` に保存
- [x] `parse_first` と `image_first` の選定11ページの対応出力を保存
- [x] vLLMモデル名、backend、実行URL、生成上限を `logs/vllm-run.json` に保存
- [x] 22件すべて `success`（本実行21件と32K再試行1件を統合） で、出力ファイルが存在
- [x] 評価結果と本実行・再試行ログをキー単位で統合済み
- [x] 既知の制限を `results/results.md` に明記

## 未完了

- 表中心ページの人手goldとセル単位評価は未実施
- 全ページ変換は未実施
- Dockerコンテナは最終検証後に停止する

## 検証コマンド

```bash
uv run python -m unittest discover -s projects/pdf-to-markdown-toyota/workspace -p 'test_*.py' -v
uv run python -m py_compile projects/pdf-to-markdown-toyota/workspace/*.py
```
