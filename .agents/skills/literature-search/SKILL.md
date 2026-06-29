---
name: literature-search
description: Project surveyやnovelty checkのために、文献を検索し、出典と要点をproject artifactに残す。
---

# Literature Search Skill

## Purpose

研究projectに必要な文献を検索し、後続agentと人間が再利用できる形で保存する。

## Inputs

- project objective
- research question
- existing `survey/README.md`
- existing `survey/sources.md`
- optional seed papers

## Outputs

- `projects/<project-name>/survey/sources.md`
- `projects/<project-name>/survey/updates/YYYY-MM-DD.md`
- 必要に応じて `survey/README.md`

## Procedure

1. 既存の `sources.md` を読み、重複を避ける。
2. 検索対象を明確にする。
3. arXiv、Semantic Scholar、OpenAlex、公式docs、著者blogなどを検索する。
4. 各sourceについて、title、authors、year、URL、短い要約、projectへの関係を書く。
5. 重要文献は `survey/README.md` の該当節へ統合する。
6. 新規追加分は `updates/YYYY-MM-DD.md` にまとめる。

## Rules

- URLとアクセス日を残す。
- 読んでいない文献を読んだように書かない。
- abstractだけ読んだ場合はその旨を明記する。
- project固有の文献は `projects/<project-name>/survey/` に置き、AI-Scientist基盤文献とは混ぜない。
