# Sources

調査日: 2026-07-30

## Toyota公式資料

| 種別 | title | URL | 要点 |
| --- | --- | --- | --- |
| 公式IR | 有価証券報告書・半期報告書 | https://global.toyota/jp/ir/library/securities-report/ | 現行ページに2026年3月期の有価証券報告書が掲載され、2021年3月期〜2025年3月期のアーカイブへの導線もある。実験初回は取得時点の最新版を固定する。 |
| 公式PDF | 2025年3月期 有価証券報告書 | https://global.toyota/pages/global_toyota/ir/library/securities-report/archives/archives_2025_03.pdf | 日本語の有価証券報告書PDF。財務表、注記、二段組み、ページ跨ぎの評価に使える。 |
| 公式IR | 決算報告 | https://global.toyota/jp/ir/financial-results/ | 2026年3月期の決算要旨、決算報告プレゼンテーション資料、スクリプト付き資料などの導線がある。 |
| 公式IR | 決算報告アーカイブズ | https://global.toyota/jp/ir/financial-results/archives/ | 2025年3月期について決算報告プレゼンテーション資料などを掲載している。 |
| 公式IR | 統合報告書 | https://global.toyota/jp/ir/library/annual/ | 統合報告書2025は33.9MB、168ページ。図表・写真・表・長文が混在する代表的な長文資料。 |
| 公式PDF | 統合報告書2025 | https://global.toyota/pages/global_toyota/ir/library/annual/2025_001_integrated_jp.pdf | インタラクティブPDFである旨が明記されており、リンクやレイアウト保持の評価にも使える。 |
| 公式説明会 | 新体制方針説明会 | https://global.toyota/jp/newsroom/corporate/39013179.html | 2023-04-07の公式発表。Toyota Mobility Concept、電動化・知能化・多様化などの中期方針候補を確認する参考資料として扱う。 |
| 公式説明会 | New Management Policy & Direction Announcement | https://global.toyota/en/newsroom/corporate/39013233.html | 英語ページではPresentation PDFの配布導線と発表内容が確認できる。 |

## PDF parsing / document AI

| title | authors / year | URL | 読んだ範囲と要点 |
| --- | --- | --- | --- |
| Docling Technical Report | Luis O. et al., 2024 | https://arxiv.org/abs/2408.09869 | abstractと公式Docling docsを確認。layout analysis、table structure recognition、OCRを統合したDocument modelからMarkdownを出力する設計。 |
| Docling documentation | Docling Project, accessed 2026-07-30 | https://docling-project.github.io/docling/getting_started/quickstart/ | PDFをDocumentConverterで変換し、`export_to_markdown()`できる公式手順を確認。 |
| MinerU: An Open-Source Solution for Precise Document Content Extraction | Bin Wang et al., 2024 | https://arxiv.org/abs/2409.18839 | abstractを確認。PDF-Extract-Kitと前処理・後処理で、多様な文書から高精度にコンテンツを抽出する設計。 |
| olmOCR: Unlocking Trillions of Tokens in PDFs with Vision Language Models | Jake Poznanski et al., 2025 | https://arxiv.org/abs/2502.18443 | abstractを確認。VLMを用いてPDFを線形化し、sections、tables、lists、equations等の構造を保つ方向性。Image-first方式の代表的な先行例。 |
| LayoutParser: A Unified Toolkit for Deep Learning Based Document Image Analysis | Zejiang Shen et al., 2021 | https://arxiv.org/abs/2103.15348 | abstractを確認。文書画像のlayout detection、OCR、再利用可能なpipelineの統合。 |
| MinerU / PDF-Extract-Kit repository | OpenDataLab, accessed 2026-07-30 | https://github.com/opendatalab/PDF-Extract-Kit | 公式READMEを確認。OCR、layout、table、数式などの構成要素を分離したモデルtoolbox。 |

## 表抽出と評価

| title | authors / year | URL | 読んだ範囲と要点 |
| --- | --- | --- | --- |
| PubTables-1M: Towards comprehensive table extraction from unstructured documents | Brandon Smock et al., CVPR 2022 | https://arxiv.org/abs/2110.00061 | abstractを確認。表検出、構造認識、機能分析を分け、セル・header・位置情報を含む大規模データセットと評価を提案。 |
| Table Transformer | Microsoft, accessed 2026-07-30 | https://github.com/microsoft/table-transformer | 公式repositoryを確認。表のrow/column/cell bounding boxとGriTS評価の実装があり、表を構造として評価する根拠になる。 |
| Benchmarking Table Extraction: Multimodal LLMs vs Traditional OCR | 2025 | https://aclanthology.org/2025.xllm-1.2/ | 概要を確認。画像表抽出でMLLMと従来OCR/vision系を比較し、表抽出の強みと限界を議論する。初回の比較指標設計の参考にする。 |

## Gemma 4

| title | URL | 読んだ範囲と要点 |
| --- | --- | --- |
| Get started with Gemma models | https://ai.google.dev/gemma/docs/get_started | 公式ガイドを確認。Gemma 4は画像入力を含むmultimodal familyで、26B A4Bはdesktop/small server向けの候補とされる。 |
| Run Gemma with the Gemini API | https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api | 公式ガイドを確認。モデルID `gemma-4-26b-a4b-it` と画像入力例がある。ローカル実行ではHugging FaceのIDを使う。 |
| Gemma 4 model card | https://huggingface.co/google/gemma-4-26B-A4B-it | model cardを確認。26B A4B MoEは総パラメータ25.2B、active parameters 3.8B、context length 256K、text/image対応と記載。Transformersの`AutoProcessor`と`AutoModelForMultimodalLM`の利用例がある。 |
| Gemma 4 Technical Report | https://arxiv.org/abs/2607.02770 | abstractを確認。Gemma 4をopen-weightでnative multimodalなモデル群として説明する一次技術報告。 |

## Notes

- 上記の論文は、初回サーベイでは主にabstractと公式README/docsを確認した。全文精読済みとは扱わない。
- Toyota資料のPDF直リンクはページ構造の変更に備え、実験manifestには最終取得URLとSHA-256を保存する。


## vLLM実行基盤

| title | URL | 読んだ範囲と要点 |
| --- | --- | --- |
| vLLM Gemma 4 recipe | https://docs.vllm.ai/projects/recipes/en/stable/Google/Gemma4.html | Gemma 4 26B A4B-itのserve例と単一GPU構成を確認した。 |
| vLLM multimodal inputs | https://docs.vllm.ai/en/latest/features/multimodal_inputs/ | OpenAI互換Chat Completionsのimage_url入力とローカル画像利用時のallowed-local-media-pathを確認した。 |
| vLLM supported models | https://docs.vllm.ai/en/latest/models/supported_models/ | Gemma 4を含む対応モデル一覧を確認した。 |

## ローカル文書パーサ・汎用VLM候補（exp-004）

調査日: 2026-08-01。以下は外部推論APIを使わず、重みと実装をローカルで実行する候補である。スコアは各プロジェクトの公表値であり、Toyota PDFでの優劣を表さない。

| title | URL | 読んだ範囲と要点 |
| --- | --- | --- |
| PaddleOCR-VL-1.6 documentation | https://www.paddleocr.ai/main/en/version3.x/algorithm/PaddleOCR-VL/PaddleOCR-VL-1.6.html | 公式導入ページを確認。ローカルCLIを第一候補とする。 |
| MinerU repository | https://github.com/opendatalab/MinerU | 公式READMEの範囲を確認。PDF・Office文書をLLM-ready Markdown/JSONに変換するローカルtoolchainを提供する。 |
| DeepSeek-OCR-2 repository | https://github.com/deepseek-ai/DeepSeek-OCR-2 | 公式repositoryの公開先を確認。ローカル実装またはvLLM互換性をpilotで検証する。 |
| dots.mocr repository | https://github.com/rednote-hilab/dots.mocr | 公式READMEの範囲を確認。文書OCRと図表をSVGとして表現する出力経路がある。 |
| Qwen3.6-27B model card | https://huggingface.co/Qwen/Qwen3.6-27B | model cardを確認。画像入力を受ける27Bモデルを提供する。実験ではローカルvLLMを用いる。 |
| InternVL3.5 paper | https://arxiv.org/abs/2508.18265 | abstractと主要benchmark表を確認。DocVQA、ChartQA、OCRBench等を含む評価を報告する。 |
| GLM-V repository | https://github.com/zai-org/GLM-V | 公式repositoryの範囲を確認。GLM-4.6Vのローカル重み・実装への導線を確認した。 |

## OCR・文書パーサ local pilot（exp-005）

調査日: 2026-08-02。公式実装・重みのみを対象とし、外部API経路は実験から除外する。

| title | URL | 読んだ範囲と要点 |
| --- | --- | --- |
| PaddleOCR-VL documentation | https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/version3.x/pipeline_usage/PaddleOCR-VL.en.md | 公式docのlocal direct inference、CLI、Markdown保存、vLLM/FastDeploy server節を確認。PaddleOCR-VL 1.6はローカルdirect inferenceと`save_to_markdown()`を提供する。 |
| MinerU repository | https://github.com/opendatalab/MinerU | 公式READMEのinstall、GPU backend、`mineru -p <input> -o <output>`を確認。MinerU2.5-Proを主VLMとし、PDFをlocal CLIで処理できる。 |
| DeepSeek-OCR-2 repository | https://github.com/deepseek-ai/DeepSeek-OCR-2 | 公式READMEのTransformers/vLLM手順とMarkdown変換promptを確認。公式exampleは`<|grounding|>Convert the document to markdown.`を使う。 |
| Unlimited-OCR repository | https://github.com/baidu/Unlimited-OCR | 公式READMEのTransformers/vLLM/SGLang手順を確認。モデルIDは`baidu/Unlimited-OCR`、local vLLM imageと単ページ・複数ページpromptが公開されている。 |
