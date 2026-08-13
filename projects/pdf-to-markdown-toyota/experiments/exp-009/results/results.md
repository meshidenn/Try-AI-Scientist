# Results

## Summary

PDFのtext layerをページ単位の正解とみなし、exp-003/004の既存hybrid Markdown出力を、3モデル共通の4ページで比較した。各ページの出力から正規化後のユニーク文字n-gramを作り、そのn-gramが同じPDFページ内に存在するかを n=1〜10 で判定した。

主指標である出力側ページ内一致率は、全12 model-page recordの平均で n=1 の **0.969974** から n=10 の **0.735759** まで低下した。PDF側n-gramの出力回収率は n=1 の **0.907552** から n=10 の **0.537383** まで低下した。

## Setup

- 対象ページ: 有価証券報告書 p135、決算説明会資料 p8、統合報告書 p11、中期方針資料 p2
- モデル: Gemma 4 26B MoE、Qwen 3.6 27B、GLM-4.6V-Flash
- 出力: 既存の `hybrid` Markdown。追加のVLM推論は行っていない
- 比較単位: 1ページ内のユニーク文字n-gram集合
- 正規化: NFKC、空白除去、Markdown/HTMLの表示構文除去
- ページ境界: PDFページをまたいだ一致は認めない

## Metrics

| 指標 | 定義 |
| --- | --- |
| Output page n-gram match rate | 出力Markdownのユニークn-gramのうち、同じPDFページtext layerに存在する割合。主指標 |
| Reference page n-gram coverage | PDFページのユニークn-gramのうち、出力Markdownにも存在する割合 |
| F1 | 上記2指標の調和平均 |

## Main Results

| n | 出力側一致率（全体） | PDF側回収率（全体） | F1（全体） | Gemma一致率 | Qwen一致率 | GLM一致率 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.969974 | 0.907552 | 0.927653 | 0.926887 | 0.987500 | 0.995536 |
| 2 | 0.937923 | 0.815910 | 0.851508 | 0.900483 | 0.943541 | 0.969745 |
| 3 | 0.911700 | 0.715392 | 0.772133 | 0.868831 | 0.914032 | 0.952237 |
| 4 | 0.876056 | 0.664820 | 0.721576 | 0.827874 | 0.870657 | 0.929638 |
| 5 | 0.842297 | 0.628056 | 0.683616 | 0.789343 | 0.828415 | 0.909132 |
| 6 | 0.810193 | 0.596354 | 0.651028 | 0.752680 | 0.788416 | 0.889482 |
| 7 | 0.785934 | 0.574851 | 0.628286 | 0.726710 | 0.758972 | 0.872120 |
| 8 | 0.766779 | 0.559165 | 0.611325 | 0.707403 | 0.737122 | 0.855811 |
| 9 | 0.751009 | 0.547741 | 0.598504 | 0.692456 | 0.720503 | 0.840069 |
| 10 | 0.735759 | 0.537383 | 0.586825 | 0.677987 | 0.704946 | 0.824342 |

GLMは全てのnで出力側一致率が最も高く、n=10では0.824342だった。Qwenは0.704946、Gemmaは0.677987だった。ただし、これはPDF text layerに対する文字列一致であり、モデルの意味的正確性や表のセル位置を示すものではない。

## Figures

図は作成していない。n=1〜10の曲線に相当する全値は `results/page_ngrams.json` に保存した。

## Failures And Negative Results

- Gemmaの元ログには対象4ページ以外の成功ページもあったため、モデル間比較は3モデル共通の4ページに限定した。最終artifactは12件で、各モデル4件である。
- n=1は頻出文字の一致でも高くなりやすく、文字内容の完全な再現や順序を保証しない。
- nが大きくなるほど、文字欠落、誤字、分割・結合、読み順差の影響を受けやすい。
- PDFの画像中文字、レイアウト、表セル位置、ページ間の継続関係はこのmetricの対象外である。

## Reproduction

```bash
PYTHONPATH=projects/pdf-to-markdown-toyota/workspace uv run python projects/pdf-to-markdown-toyota/workspace/evaluate_shared_page_ngrams.py \
  --root projects/pdf-to-markdown-toyota/experiments/exp-009 \
  --model-log gemma4-26b-moe=projects/pdf-to-markdown-toyota/experiments/exp-003/logs/hybrid-run-v2.json \
  --model-log qwen3.6-27b=projects/pdf-to-markdown-toyota/experiments/exp-004/logs/qwen3.6-27b-hybrid-pilot.json \
  --model-log glm-4.6v-flash=projects/pdf-to-markdown-toyota/experiments/exp-004/logs/glm-4.6v-flash-pilot.json \
  --method hybrid
```

## Notes For Reviewer

「ページ内に一致するか」は、各n-gramを同一PDFページの正規化済み文字列集合に対して存在判定する形で実装した。重複n-gramは1回として数えた。出力側一致率はprecision相当、PDF側回収率はrecall相当であり、片方だけでは出力の過剰生成または欠落を区別できないため両方を保存している。
