# Next Plan

1. embedding endpointまたはpinしたローカルembedding modelを導入し、hash embeddingを置き換える。
2. extract promptの出力長・chunk size・max tokensを調整して、relation extractionのtruncationを解消する。
3. 複数document・分離split・gold evidenceを持つ入力を固定し、baselineと同じcandidate budgetでRecall@k/MRRを測定する。
4. 上記が完了するまで、Qwen条件の性能差や原論文再現を主張しない。
