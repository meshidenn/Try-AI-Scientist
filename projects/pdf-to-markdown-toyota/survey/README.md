# Survey

## Research Question

トヨタ自動車の有価証券報告書、決算説明会資料、統合報告書、中期経営計画書相当資料を、本文・表・脚注・ページ順をできるだけ保ったMarkdownへ変換するには、どの入力表現と後処理が適切か。

比較する主方式は次の2つである。

1. **Parse-first**: PDFのテキスト、座標、ページ番号を取得し、ブロック順と表らしい領域を整理してからGemmaへ渡す。
2. **Image-first**: PDFページを高解像度画像へレンダリングし、画像とページ単位の指示をGemmaへ渡す。

## Current Understanding

PDFは見た目の配置と論理構造が分離している。単純なテキスト抽出は二段組み、表、脚注、ページ跨ぎで読み順を壊しやすい。一方、画像入力は視覚的な表構造や図表を直接利用できるが、小さい文字、長い文書、ページ内の情報量、出力の再現性が課題になる。

初回実験では、両方式の入力をページ単位で記録し、モデル出力をページ対応Markdownとして保存する。全資料の完全変換をいきなり単一プロンプトで行わず、まず代表ページを対象に、方式比較と失敗パターンの可視化を行う。

## Relevant Prior Work

- **Docling**: layout analysis、table structure recognition、OCRを統合し、構造化DocumentからMarkdownを出力する実装。Parse-firstの強いベースライン候補。
- **MinerU**: PDF-Extract-Kitを使い、レイアウト、OCR、表、数式などの前処理・後処理を統合する。複雑なPDFへの実装候補だが、初回は依存と再現性を抑えてPyMuPDFベースを使う。
- **olmOCR**: VLMでPDFをページ画像から線形化テキストへ変換し、表・リスト・数式などの構造化を保つことを目指す。Image-firstの設計判断に近い。
- **PubTables-1M / Table Transformer**: 表検出・表構造認識・機能分析を分けて評価し、表を文字列一致だけで測らない根拠になる。
- **LayoutParser**: 文書画像のlayout detectionとOCRを組み合わせる。ページ画像から表・タイトル・本文を切り出す後続拡張候補。

## Methods And Design Ideas

### Parse-first

PyMuPDFでページごとの text block と bounding box を取得する。blockの座標から上から下、左から右へ近似的に並べ、ページ内の列を分離する。表は、同一水平帯に数値・短い文字列が密集する領域を候補として記録し、抽出されたtext blockと座標をGemmaへ渡す。モデルには「値を補完しない」「不明なセルは`[判読不能]`と書く」「表はMarkdown tableにする」「ページ境界を維持する」と指示する。

### Image-first

PyMuPDFでページを300 DPI相当へレンダリングし、PNGとして保存する。Gemma 4 26B A4Bの画像入力に、1ページ画像と同じ忠実度制約のプロンプトを渡す。小さい表が多いページでは、後続実験で表領域cropを追加できるよう、画像メタデータとページ番号を保存する。

### 共通の後処理

- モデル出力からコードフェンスを正規化する。
- ページ見出し（`<!-- page: N -->`）を保持する。
- Markdown tableの列数崩れを検出し、修正前後を別artifactにする。
- 原PDFのページ画像と出力Markdownをページ単位で対応づける。
- 実行時にモデルID、transformers版、generation設定、入力トークン数、出力時間をログする。

## Evaluation And Benchmarks

初回は自動評価と人手確認用artifactを併用する。

| 指標 | 内容 | 目的 |
| --- | --- | --- |
| text_normalized_similarity | Unicode、空白、改行を正規化した本文類似度 | 文字欠落・改変の把握 |
| numeric_token_recall | 原PDF抽出テキスト中の数値tokenの再現率 | 財務数値の欠落防止 |
| table_shape_accuracy | 参照表と出力表の行列形状一致 | 行列構造の保持 |
| table_cell_exact_match | 対応セルの完全一致率 | 金額・単位・比率の忠実度 |
| footnote_presence | 脚注候補が出力に残った割合 | 但し書き・注記の保持 |
| page_order_integrity | ページ順とページmarkerの整合 | 文書全体の順序保持 |
| wall_time_seconds | 前処理から出力までの時間 | 実用性の比較 |

参照正解はPDFを人手で全文転記したものではなく、まずPyMuPDFのblock抽出とページ画像を根拠にした「評価用reference subset」とする。したがって、類似度の数値は完全な正解率ではなく、reference subsetに対する測定値として扱う。

## Risks And Open Questions

- 現行のToyota公式IRサイトには独立した「中期経営計画書」カテゴリが見当たらない。初回は公式ダウンロードの「2030年電動化戦略」資料を中期方針資料相当とし、対象の妥当性をREADMEとspecに明記する。
- 2025年統合報告書は168ページで、全ページを26Bモデルへ一度に入力するのは不適切。ページ単位・小chunkを基本にする。
- Gemmaのローカル推論はモデル重み、利用規約同意、VRAM、vLLM対応版に依存する。今回の実行はvLLM OpenAI互換サーバーで行い、サーバー設定と実行ログを保存する。
- PDFのテキストlayerが誤っている場合、Parse-firstのreference自体も不完全になる。画像を根拠にした小規模な人手gold subsetを次runで追加する。

## Implications For Experiments

初回は、4資料の各資料から代表ページを自動選定し、両方式で同一ページを処理する。代表ページには本文中心、表中心、二段組み・脚注、図表を含むページを含める。完全版変換は、方式比較で優位な経路と表crop戦略を決めた後のexp-002で行う。

## Sources

詳細な出典、アクセス日、要約は [`sources.md`](sources.md) に記録する。
