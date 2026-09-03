# Artifact Audit

## Verdict

PASS

## Checked Artifacts

- `inputs/manifest.json`にUltraDomain revision、全量index、query hash、gold evidence未提供の制約を記録した。
- `inputs/contexts.jsonl`と`inputs/generated_queries.json`のhashはmanifestと一致する。
- 評価用LightRAG storeは61件すべて`processed`であり、BGE-M3 vector storeの件数はchunk 1,375、entity 20,281、relationship 23,869である。
- hybrid/naiveの結果JSONは各5件で、空回答は0件だった。
- `run_summary.json`はcompletedで、Qwen non-stop終了は0件だった。
- Prometheus-2 judgeは5件すべてを判定し、勝数はhybrid 3、naive 2である。
- gpt-oss-20b judgeは同一の5回答対をすべて判定し、勝数はhybrid 3、naive 2である。判定ごとの勝者はPrometheus-2と5/5一致する。
- 正本BGE-M3 indexの3 vector store hashはexp-034時点の値と一致し、query評価によって変更されていない。
- 公式条件との差分を`review/protocol-differences.md`へ記録した。

## Blocking Issues

なし。

## Warnings For Interpretation

- Gold evidenceおよびreference answerが未提供のため、勝率は検索精度・正解率ではない。
- 評価queryは1 contextから生成した5問であり、61文書全体を代表する評価ではない。
- gpt-oss-20bの判定もreference answerなしであり、judge間一致は正解性の保証ではない。
- gpt-oss-20bのquery 2は`[RESULT] B`のみで、要求した詳細な比較理由を返さなかった。勝者の構文解析には支障がないが、rationale品質の比較には使えない。
- chunk vectorの閾値未達によりentity-related chunkへのfallbackが生じ、rerankerも未設定である。

## Notes

これはIssue #4のQwen LightRAG再評価のend-to-end実装確認である。原論文または公式実装の完全再現とは扱わない。
