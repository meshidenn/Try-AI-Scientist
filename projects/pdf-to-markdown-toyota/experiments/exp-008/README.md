# exp-008: Three-VLM numeric and text ensemble confidence

exp-006の4ページ・3モデルhybrid出力を再利用し、数値tokenだけでなく本文行、見出し、表内の非数値セルにもconfidenceを付与する。追加推論は行わない。Gemmaだけを座標chunk化したexp-007のp135出力は、Qwen/GLMと出力条件が異なるため用いない。

confidenceは未校正のevidence scoreであり、正答確率ではない。テキストは正規化文字列の類似とPDF text layerの包含だけを使い、意味的な言い換え、画像中文字、表セル位置を検証しない。

各モデルの元Markdown出力を確認できるよう、`outputs/colorized-model-output/<model>/hybrid/<document>/page-<page>.html` に実出力HTMLも生成する。候補一覧ではなく、元出力の見出し・本文・表に対して、数値・テキスト候補のevidence scoreをHigh/Medium/Lowで重ねる表示である。
