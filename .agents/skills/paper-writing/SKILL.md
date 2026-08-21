---
name: paper-writing
description: paper-planningのblueprintとproject artifactから、研究論文の原稿を作成・更新する。特に実験前のProposal Modeで、未実行結果を捏造せずIntroduction、Related Work、Method、Experimental Planを執筆する場合に使用する。
---

# Paper Writing Skill

## Purpose

`paper-planning` のblueprintを、projectのsurvey・research plan・experiment spec・結果artifactと整合する論文原稿へ変換する。既存のdraftを更新する場合も、claimとevidenceの対応を壊さない。

## Inputs

最初に次を読む。

- `projects/<project-name>/paper/plan.md`
- `projects/<project-name>/RESEARCH_PLAN.md`
- `projects/<project-name>/survey/sources.md`
- `projects/<project-name>/experiments/<exp-id>/spec.yaml`
- `projects/<project-name>/paper/draft.md`（更新時）

Data-Aware Modeでは追加で読む。

- `projects/<project-name>/experiments/<exp-id>/results/results.md`
- `projects/<project-name>/experiments/<exp-id>/results/scores.json`
- `projects/<project-name>/experiments/<exp-id>/figures/`
- `projects/<project-name>/experiments/<exp-id>/review/artifact-audit.md`
- `projects/<project-name>/experiments/<exp-id>/review/result-interpretation.md`
- `projects/<project-name>/experiments/<exp-id>/results/claims.json`

`plan.md` がない場合は、先に `paper-planning` を実行する。文献が不足する場合は記憶で補わず、`literature-search` を使う。

## Modes

### Proposal Mode

実験前、未監査、または結果artifactがない場合の既定モード。

- `paper/draft.md` に実験結果の数値、順位、改善率、成功を記述しない。
- 「本研究は示す」ではなく、「本研究は検証する」「我々は仮説を置く」と書く。
- 結果、table、figureの未取得値は `TBD`、空欄、または検証項目として残す。
- 検証予定の差分と、すでに知られている先行研究の結果を混同しない。
- 「新規性がある」と断定せず、既存研究との差分と未検証の研究課題として記述する。
- 研究計画にない追加baseline、metric、datasetを、実施済みのように導入しない。

### Data-Aware Mode

結果artifactとartifact auditが利用可能な場合のみ使用する。

- 数値・図・表は、対応するartifact path、dataset、split、seed、metricと照合する。
- 結果に支持されないclaimは削除、弱化、limitationsへの移動のいずれかにする。
- null、negative、failure、未実行を結果から隠さない。
- 結果に合わせて文章を更新する場合も、実験specと変更理由を記録する。

## Writing Workflow

1. `paper/plan.md` のsection outlineとcanonical claim wordingを読む。
2. 既存draftがあれば、見出し、用語、引用、TBDを保持しながら更新する。
3. Introductionでは、背景、問題の分解、research gap、研究問い、仮説、貢献を順序立てて書く。
4. Related Workでは、先行研究を単なる列挙にせず、本研究の比較軸と差分へ接続する。
5. Methodでは、方式、入力構造、one-shot/closed-loop、budget、top-N、turn、reader条件をspec通りに書く。
6. Proposal Modeでは、Experimental SetupとExpected Analysisを先に書き、Resultsは空の構造だけを用意する。
7. Data-Aware Modeでは、results artifactからResults、Analysis、Limitationsを埋める。
8. 各sectionのclaimをclaim-evidence mapと照合する。
9. 原稿内の用語（one-shot、open-loop、closed-loop、cumulative top-N、turn、MeSHなど）を統一する。
10. `paper/draft.md` を保存し、変更概要と未解決事項を報告する。

## Proposal Mode Paper Structure

最低限、次の順で構成する。研究対象に不要なsectionは計画に理由を残して省略する。

1. Title
2. Abstract placeholder（結果を含めない）
3. Introduction
4. Related Work
5. Research Question and Hypotheses
6. Method / Experimental Design
7. Evaluation Protocol
8. Expected Analysis or Results Template
9. Risks and Limitations
10. Conclusion（計画上のまとめ）
11. References

Proposal Modeのabstractとconclusionは、実験結果を示す代わりに、検証する問い、比較条件、予定する分析を記述する。

## Citation Rules

- 引用は `survey/sources.md` にあるsourceを優先する。
- title、authors、year、URLを確認できない文献を追加しない。
- 先行研究の実験結果を引用する場合、原論文の条件と本研究の条件を明示する。
- 本研究の計画、仮説、実測結果を、先行研究のclaimとして書かない。
- 引用を増やすこと自体を関連研究の目的にしない。各引用がどのclaimを支えるかを確認する。

## Integrity Rules

- 未実行の実験を実行済みとして扱わない。
- `TBD` を推測値で埋めない。
- 研究計画の仮説を結果の要約へ変換しない。
- 数値がない段階で「改善」「優位」「最良」と書かない。
- `paper-reviewer` は原稿への批判的review、`result-verification` と `claim-auditor` は結果後のevidence監査を担当する。これらを執筆作業と混同しない。
- 実験結果を含む原稿を更新する場合、`results/claims.json` または対応する結果artifactを参照する。

## Validation

保存前に次を確認する。

- Proposal Modeで未実行の数値・成功・優位の断定がない。
- すべてのsectionがpaper planのresearch questionとscopeに対応する。
- 引用リンクが `survey/sources.md` と一致する。
- Methodのdataset、budget、top-N、turn、metricがspecと一致する。
- 既存draftを更新した場合、削除・追加したclaimを記録できる。
- 変更後に `git diff --check` を実行する。
