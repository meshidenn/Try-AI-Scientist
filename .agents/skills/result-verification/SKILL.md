---
name: result-verification
description: 解釈、next plan、paper内claimが実際のartifactと一致しているか検証する。
---

# Result Verification Skill

## Purpose

AI-Scientistが「結果から言えないことを言っている」状態を防ぐ。paperがない場合でも、`result-interpretation.md` と `next-plan.md` を対象にする。

## Inputs

- `results/results.md`
- `results/scores.json`
- `figures/`
- `logs/`
- `review/artifact-audit.md`
- `review/result-interpretation.md`
- `review/next-plan.md`
- optional `paper/`

## Output

- `results/claims.json`
- optional `review/claim-audit.md`

## claims.json Shape

```json
{
  "claims": [
    {
      "claim": "The proposed method improves accuracy over baseline.",
      "source": "review/result-interpretation.md",
      "artifacts": [
        "results/scores.json",
        "figures/main_result.png"
      ],
      "status": "supported",
      "support_level": "direct",
      "notes": ""
    }
  ]
}
```

## Status Values

- `supported`: artifactで確認できる
- `partially_supported`: 一部は確認できるが不足がある
- `unsupported`: artifactと一致しない、またはartifactがない
- `not_checked`: 時間や依存関係の理由で未確認

## Support Levels

- `direct`: 数値、ログ、図などで直接支えられている
- `indirect`: 複数artifactから推論すれば支えられる
- `weak`: 示唆はあるがclaimとしては弱い
- `none`: 支えがない

## Rules

- 数値は `scores.json` またはログと照合する。
- 図の説明は実際の図と照合する。
- 未実行の実験を支持根拠にしない。
- `result-interpretation.md` と `next-plan.md` の主張も検証対象にする。
- paperがない場合も実行する。
- `unsupported` はfile pathと理由を明記する。
