# Artifact Audit

# Artifact Audit

## Verdict

FAIL

## Checked Artifacts

- `spec.yaml`: present.
- `workspace/train_baseline.py`: present.
- `pyproject.toml`: present at repository root for uv-managed dependencies.
- `workspace/data/train.csv`: missing.
- `workspace/data/test.csv`: missing.
- `workspace/data/sample_submission.csv`: missing.
- `logs/data-acquisition.log`: present.
- `results/results.md`: present and records the acquisition failure.
- `results/scores.json`: present with status `blocked`.

## Blocking Issues

Official Kaggle data was not available. Training and scoring did not run, so
this experiment cannot support any model-performance claim.

## Warnings For Interpretation

Interpret only as an environment and workflow finding: the repository needs a
documented data acquisition path or a credential check before launching Kaggle
runs.

## Notes

This is a valid failed run and should be archived.
