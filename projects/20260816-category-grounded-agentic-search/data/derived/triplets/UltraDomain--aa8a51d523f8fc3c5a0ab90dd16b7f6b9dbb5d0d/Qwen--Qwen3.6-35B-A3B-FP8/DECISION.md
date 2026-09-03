# Triplet Extraction Decision

## Date

2026-08-29

## Decision

書誌一覧のように高密度なentity/relationを含むchunkで、モデルが同一tripletを反復して
`finish_reason=length`へ到達することを確認した。以後のtriplet抽出は、次の3層を必須とする。

1. 抽出promptに、既出entity/relationを再出力せず、重複しそうな場合はJSONを閉じるよう明記する。
2. 1 chunkあたりの出力上限をentity 30件、relation 50件に制限する。
3. 実装側で非空行の一意率を検出し、20行以上かつ一意行率が0.5未満のcompletionを
   警告として記録する。`finish_reason=stop`かつ非空のcompletionはKG抽出を継続し、
   非`stop`または空応答だけを失敗として扱う。
4. QwenのvLLM生成パラメータに`repetition_penalty=1.05`を設定する。これは高密度chunkでの
   停止しない反復を抑えつつ、固有表現の抽出漏れを過度に増やさないための最小の追加ペナルティである。

## Evidence

- Qwen delimiter mode: 32,768 token出力で1,007行中18行のみが一意、989行が重複。
- Qwen JSON mode: 8,192 token出力で643行中213行が一意、430行が重複。
- gpt-oss-120b JSON mode: 8,192 token出力で334行中115行が一意、219行が重複。
- Qwen JSON mode（3層対策後）: `finish_reason=stop`でも374行中145行のみが一意
  （一意率0.388）となった（exp-025）。当時は反復を失敗扱いにしていたが、現在は診断値である。
- Gemma 4 JSON mode（同一対策）: `finish_reason=stop`でも246行中79行のみが一意
  （一意率0.321）となった（exp-026）。同様に、現在は反復率のみでは失敗にしない。
- Qwen警告モード: 最初の4チャンクは反復警告つきで受理されたが、5チャンク目が
  8,192 tokensで`finish_reason=length`となり未完了だった（exp-027）。
- Qwen 32,768-token mode: 同一文書の全11チャンクが`stop`で完結し、326 entityと
  602 relationからなるKGを生成した（exp-028）。この文書では、出力長不足が未完了の直接原因だった。
- Qwen `repetition_penalty=1.05`: 32,768-token上限で過去にlength終了した36チャンク文書が
  全chunk `stop`で完結した。最大completionは3,679 tokensだった（exp-032）。

## Rationale

出力token上限の増加だけでは反復を解消しない。`repetition_penalty=1.05`を併用し、
抽出結果をembedding/indexから独立して保存してから次段階へ渡す。行単位の一意率はJSON構造に
影響されるため、停止判定ではなく診断記録として扱う。
