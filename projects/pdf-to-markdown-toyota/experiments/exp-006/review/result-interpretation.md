# Result Interpretation

## Supported Findings

- 4ページ平均のPDF数値token被覆率は0.704411、被覆率調整confidenceは0.643828である。
- 有価証券報告書 p135は出力候補が全てHighでも、PDF数値token被覆率が0.583333である。候補側だけの合意では欠落を検知できない。
- 統合報告書 p11は被覆率0.270677であり、この数値token方式では図・複合レイアウトを十分に検証できない。

## Not Supported

- High/Medium/Lowを正答確率として解釈すること。
- 表の列・セル位置、グラフ系列、系統図の関係が正しいという主張。

## Interpretation Boundary

このpilotは数値候補の人手レビュー優先順位付けに使えるevidence scoreの試作である。最終変換を自動採択する判断には、位置つきセル照合と人手ラベルによる校正が必要である。
