# PDFパース改善TODO

表と図の構造を、文字n-gramとは別に評価・改善するためのTODOである。

## 優先度

- P0: 次の実験で必ず対応する
- P1: P0の結果を受けて対応する
- P2: 必要性を確認して対応する

## 表処理

### P0: 表領域の座標manifestを作成

- 対象: 有価証券報告書 p135
- 罫線、文字の整列、空白領域から表bboxを定義する
- 本文、脚注、キャプションを表領域から分離する
- `inputs/table-gold.json`にページ番号、bbox、表IDを保存する

完了条件:

- 対象表が座標付きで再現可能に定義されている
- 表領域と本文・脚注の境界を確認できるreview HTMLがある

### P0: 表の行列・セル構造を抽出

- 行境界と列境界を座標から推定する
- セルのbbox、row、columnを保存する
- rowspan / colspanを表現できるschemaを作る
- 空セルと結合セルを区別する

完了条件:

- `row`、`column`、`bbox`、`rowspan`、`colspan`がmanifestに記録されている
- 表構造だけを確認できるdebug HTMLがある

### P0: Markdown表との構造比較を実装

- 行数・列数を比較する
- セル位置ごとの対応を比較する
- rowspan / colspanの一致を比較する
- ヘッダ行とデータ行を区別する

主なmetric:

- `table_row_recall`
- `table_column_recall`
- `table_cell_alignment_accuracy`
- `table_span_accuracy`
- `table_structure_score`

完了条件:

- 文字列一致とは独立して表構造の誤りを検出できる
- 列ずれ、行ずれ、セル結合の誤りをHTMLで確認できる

### P1: 表セル内の文字・数値評価を実装

- line-aware 1-gram評価をセル単位に適用する
- 数字はnumeric tokenとして別評価する
- 単位、年度、前年・当年の列対応を確認する
- セル位置が合っている場合だけセル内容の一致を加点する

主なmetric:

- `table_cell_text_cov`
- `table_numeric_token_recall`
- `table_numeric_token_precision`
- `table_cell_exact_match`
- `table_value_position_accuracy`

### P1: 表HTML rendererを修正

- Markdownの行を`<tr>`、ヘッダを`<th>`、データを`<td>`へ変換する
- colspan / rowspanをHTMLへ反映する
- セル内の一致・不一致・漏れの色付けを維持する

完了条件:

- 表の行列がブラウザ上で崩れない
- 色付けしてもセル境界と表構造を確認できる

## 図処理

### P0: 図領域の座標manifestを作成

- 対象: 統合報告書 p11
- 図、キャプション、凡例、本文のbboxを分ける
- 複数panelはpanel IDを付ける
- `inputs/figure-gold.json`にページ番号、bbox、panelを保存する

完了条件:

- 図領域が座標付きで再現可能に定義されている
- 元PDF画像とbboxを重ねたreview HTMLがある

### P0: 図中ラベルと要素を抽出

- PDF text layerの文字を図領域内から抽出する
- 画像内文字はOCRまたはVLMで抽出する
- ノード、凡例、軸、ラベル、キャプションを分類する
- 各要素にbboxとsource（PDF text / OCR / VLM）を付ける

主なmetric:

- `figure_label_precision`
- `figure_label_recall`
- `figure_element_precision`
- `figure_element_recall`

### P1: 図の接続関係を抽出・比較

- 矢印、線、分岐、包含関係を要素間relationとして表現する
- `from`、`to`、`type`、`direction`、bboxを保存する
- vector drawingと画像情報を併用する
- 出力Markdownの箇条書き・階層・矢印表現へ対応づける

主なmetric:

- `figure_relation_precision`
- `figure_relation_recall`
- `figure_relation_f1`
- `figure_direction_accuracy`

### P1: 図のレイアウトを比較

- 左右・上下の相対位置を比較する
- panel順、要素のグループ、凡例位置を比較する
- 絶対座標ではなく相対位置を主に評価する

主なmetric:

- `figure_relative_position_accuracy`
- `figure_panel_order_accuracy`
- `figure_grouping_accuracy`
- `figure_layout_score`

### P1: 図のHTML rendererを実装

- 図領域の元画像を表示する
- 抽出した要素bboxを重ねる
- ラベル、relation、漏れ要素を色分けする
- 元Markdownの図表現と並べて表示する

## 共通基盤

### P0: 表・図の人手gold manifestを作成

- 表と図を文字列n-gramのproxy正解から分離する
- bbox、要素、セル、relation、相対位置を人手で記録する
- JSON schemaとannotationルールをREADMEに記載する

対象はまず以下に限定する。

- 有価証券報告書 p135の表
- 統合報告書 p11の図

### P0: crop/chunk単位のhybrid処理を実装

- 本文・表・図を領域単位に分割する
- 各領域へ対応する画像cropとPDF parse情報を渡す
- 領域ID付きで出力を保存する
- 最後にページ単位のMarkdownへ構造化mergeする

### P1: review dashboardを作成

- 文字、数値、表、図を別metricとして表示する
- PDF画像、parse要素、モデル出力、評価結果を同時表示する
- model、page、content typeで絞り込めるようにする

## 推奨実施順

1. p135の表gold manifest
2. p11の図gold manifest
3. 表の行列・セル構造評価
4. 図のラベル・要素評価
5. 表・図のHTML review
6. crop/chunk単位のhybrid処理
7. relation・layout評価
8. review dashboard
