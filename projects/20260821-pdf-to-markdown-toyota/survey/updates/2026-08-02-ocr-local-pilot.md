# OCR local pilot sources

- 対象: PaddleOCR-VL-1.6、MinerU2.5-Pro、DeepSeek-OCR-2、Unlimited-OCR。
- PaddleOCR-VLは公式CLI/ローカルdirect inferenceでMarkdown保存を提供する。
- MinerUは公式local CLIを提供し、2.5-Proを主VLMとしている。
- DeepSeek-OCR-2は公式Transformers/vLLM実装にMarkdown変換promptがある。
- Unlimited-OCRはBaidu公式GitHubでlocal Transformers/vLLM/SGLang経路を公開している。
- いずれも外部推論APIを使わない経路に限定する。
