# exp-007: Coordinate-chunked hybrid conversion

有価証券報告書 p135をPDF text blockの座標で領域分割し、各領域のcrop画像と文字blockをGemma 4へ個別に渡す。ページ全体を `max_new_tokens=1024` で処理したexp-003をbaselineとし、chunkごとに4096 tokenまで生成する。

実装は共有の `workspace/run_chunked_hybrid.py` に置く。実験ディレクトリには条件、入力manifest、出力、log、評価だけを置く。
