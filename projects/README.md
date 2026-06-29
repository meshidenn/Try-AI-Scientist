# projects

研究テーマごとの作業場所。

各projectは、サーベイフェーズとcoding phaseを分けて管理する。

```text
projects/
  <project-name>/
    project.yaml
    survey/
      README.md
      sources.md
      changelog.md
      updates/
    experiments/
      exp-001/
        spec.yaml
        README.md
        workspace/
        results/
          results.md
          scores.json
          claims.json
        figures/
        logs/
        review/
          artifact-audit.md
          paper-review.md
          result-interpretation.md
          next-plan.md
          claim-audit.md
          rebuttal.md
        paper/
```

`survey/` は人間が学習しやすいMarkdownを残す場所。

`experiments/` はcoding agentが実行した個別実験の履歴を残す場所。

`review/` は1つのreviewerにまとめない。run直後のartifact audit、結果を解釈して次planを考えるinterpretation、paperを書く場合だけのpaper review、interpret後のclaim auditに分ける。
