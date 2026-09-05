# Dataset Audit for Issue #3

Access date: 2026-08-22

## Decision Summary

| Dataset | Status | Question / evidence mapping | Corpus reproducibility | License | Decision |
| --- | --- | --- | --- | --- | --- |
| FanOutQA | conditional | dev schemaにquestion ID、human decomposition、`necessary_evidence`（page ID / revision ID / title）がある | 2023-09 Wikipedia ZIMまたは公式snapshotをpinできる | dataset: CC-BY-SA-4.0; Wikipediaの利用条件も継承する | 小規模pilot候補。snapshotを取得・hash固定後にのみ`accepted`へ変更する |
| FRAMES | conditional | test splitはquestion、answer、Wikipedia URL群、reasoning typeを含む | URLはあるがrevision IDがない。live Wikipediaでは再現不能 | Apache-2.0 | URLからrevisionを解決してsnapshotを保存できる場合だけ採用する |
| MuSiQue | needs-official-source | community mirrorのvalidation splitは確認できたが、公式releaseとの同一性を確認できていない | official corpus / evidence mappingを未確認 | mirror card: CC-BY-4.0 | 公式配布物とlicenseを確認するまで採用しない |
| HDS-QA | blocked | 公開論文は確認できたが、候補HF dataset viewerは401でschemaを確認できない | corpus、gold evidence、licenseを未確認 | 未確認 | 公開配布元・利用条件が確認できるまで採用しない |

## Source Checks

### FanOutQA

- Official repository: <https://github.com/zhudotexe/fanoutqa>
- Dataset license: <https://huggingface.co/datasets/zhuexe/fanoutqa/blob/main/LICENSE>
- The repository documents `DevQuestion.id`, `necessary_evidence`, and evidence-level `pageid`, `revid`, `title`, `url` fields. It also provides a 2023-09 Wikipedia ZIM and a larger November 2023 snapshot.
- The experiment must record the exact `fanoutqa` release and one immutable corpus artifact. Live API retrieval is not an acceptable primary corpus because the upstream documentation reports rate limiting and page changes.

### FRAMES

- Dataset card: <https://huggingface.co/datasets/google/frames-benchmark>
- The Hub card declares Apache-2.0. The Dataset Viewer exposed one `test` split with question (`Prompt`), answer, `wikipedia_link_*`, `wiki_links`, and `reasoning_types` columns.
- The currently exposed rows identify evidence by URLs, not revision IDs. The audit therefore requires resolving each URL to a historical revision or storing an immutable page snapshot before retrieval evaluation.

### MuSiQue

- Original project reference: <https://github.com/StonyBrookNLP/musique>
- Observed Hub mirror: <https://huggingface.co/datasets/fladhak/musique>
- The observed mirror reports a `validation` split and CC-BY-4.0, but this audit does not treat a third-party mirror as the canonical release. Its data version, corpus source, and supporting-evidence mapping must be checked against the original project before use.

### HDS-QA

- Paper: <https://openreview.net/forum?id=rXpTZyucal>
- Candidate dataset page: <https://huggingface.co/datasets/dayoon/HDS-QA-Single-Query>
- The paper describes HDS-QA as a synthetic dataset derived from Natural Questions. The candidate dataset could not be read through the public Dataset Viewer during this audit (HTTP 401), so the released schema, evidence fields, and license remain unverified.

## Admission Gate

A dataset is `accepted` only when all of the following are saved in an input manifest:

1. immutable dataset revision and license;
2. question ID to gold-evidence ID mapping;
3. immutable corpus snapshot and document/passage mapping;
4. split assignment; and
5. preprocessing and chunking configuration.

No model run has been executed as part of this audit.
