---
name: paper-planning
description: 研究projectの計画、survey、experiment spec、既存原稿から、論文の構成・claim・引用・必要evidenceを設計する。論文を書き始める前のblueprint作成、Proposal Modeの論文設計、実験前の主張と結果表の事前登録で使用する。
---

# Paper Planning Skill

## Purpose

project artifactから、論文を一貫して書くためのblueprintを作る。文章を先に生成せず、research question、hypothesis、claim、citation、必要なevidenceを対応付ける。

## Inputs

最初に次を読む。

- `projects/<project-name>/project.yaml`
- `projects/<project-name>/RESEARCH_PLAN.md` または同等の研究計画
- `projects/<project-name>/survey/sources.md`
- `projects/<project-name>/survey/updates/`（存在する場合）
- `projects/<project-name>/experiments/<exp-id>/spec.yaml`
- `projects/<project-name>/paper/draft.md`（存在する場合）
- 結果がある場合は `experiments/<exp-id>/results/`、`figures/`、`review/`

既存artifactが存在しない場合は、推測で補完せず、blueprintに不足入力として記録する。

## Modes

入力artifactからモードを決める。

### Proposal Mode

実験結果が未実行、または結果artifactが未監査の場合に使う。

- 数値、順位、改善率、実験成功を結果として書かない。
- `we show`、`achieves`、`outperforms` のような結果断定を避ける。
- 仮説は `we hypothesize`、検証計画は `we will evaluate` と書く。
- 結果表は空欄または `TBD` とし、期待値を埋めない。
- contributionは実施済みの成果ではなく、提案する分析枠組みとして記述する。

### Data-Aware Mode

`artifact-audit.md` が PASS または解釈可能な WARN で、結果とscoreが存在する場合に使う。

- 数値は `results/scores.json`、`results/results.md`、log、figureのいずれかへ対応付ける。
- claimごとに `supported`、`partially_supported`、`unsupported`、`contradicted` を記録する。
- 未支持の主張は削除、弱化、limitationsへの移動のいずれかにする。
- 結果を見た後に実験仮説や評価指標を都合よく変更しない。変更した場合は変更理由を記録する。

## Workflow

1. `project.yaml` からproject名、研究状態、paperの正規pathを確認する。
2. Research planからresearch question、scope、hypothesis、planned contribution、禁止された主張を抽出する。
3. surveyから関連研究を、問題設定、方法、データ、限界、本研究との関係に分類する。
4. experiment specからbaseline、dataset、budget、metric、leakage control、success criteriaを抽出する。
5. 論文claimを次の粒度で列挙する。
   - motivation claim
   - prior-work claim
   - method/design claim
   - evaluation claim
   - result claim
   - limitation claim
6. 各claimに、必要なcitation、必要なartifact、現時点のsupport statusを対応付ける。
7. 論文のsection outlineを作る。各sectionに目的、中心claim、引用、必要evidence、Proposal/Data-Awareの制約を付ける。
8. 結果表・図のblueprintを作る。Proposal Modeではセルを空欄または `TBD` にする。
9. `paper/plan.md` にblueprintを書き、既存の `paper/draft.md` がある場合は矛盾を報告する。文章の書き換えは `paper-writing` に委ねる。

## Required Output

`projects/<project-name>/paper/plan.md` に次の構成で保存する。

```markdown
# Paper Plan

## Mode And Status
## Research Question
## Central Hypotheses
## Intended Contributions
## Section Outline
## Claim-Evidence Map
## Citation Map
## Planned Tables And Figures
## Unsupported Or Prohibited Claims
## Open Inputs And Decisions
```

`Claim-Evidence Map` には少なくとも `claim_id`、`claim`、`status`、`citation`、`artifact`、`allowed_mode` を含める。

## Integrity Rules

- 実験前の計画を実験済みの結果として書かない。
- surveyにない引用を記憶だけで追加しない。必要なら `literature-search` を使ってから更新する。
- 同じclaimに複数の表現がある場合、canonical wordingを一つ定める。
- 主張がsupportされるartifact pathを空欄にしたまま「supported」としない。
- 新規性を主張する前に、関連研究との差分、未検証点、scopeを明示する。
- `paper-reviewer` の仕事である文章品質reviewや、`claim-auditor` の仕事である結果後の監査を代行しない。

## Validation

作成後に次を確認する。

- `paper/plan.md` が存在し、projectの正規paper pathを使っている。
- Proposal Modeで数値結果や未実行実験の成功断定がない。
- 各予定結果表に、対応するmetric、dataset、budget、必要artifactがある。
- citationとclaimの対応がsurveyのsourceに存在する。
- open inputs、未決定のdataset、未実行の実験が明示されている。
