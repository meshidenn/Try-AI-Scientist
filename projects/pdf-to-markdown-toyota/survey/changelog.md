# Survey Changelog

## 2026-07-30

- Toyota公式の4資料カテゴリと対象候補を追加。
- Parse-first、Image-first、表構造評価、Gemma 4 26B A4Bの一次資料を整理。
- 初回はPyMuPDFベースの軽量な直接パースを実装し、Docling/MinerU/olmOCRは後続候補として位置づけた。
- 推論基盤をTransformers直接実行からvLLM OpenAI互換サーバーへ変更し、Gemma 4 26B A4Bで初回スモークを実測した。
- 同一ページ・同一モデルでHTML fragment出力も比較し、要素契約と表構造の評価上の注意点を追加した。
