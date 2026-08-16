# Results

Status: blocked before model run.

## Summary

The experiment environment was created before the repository-wide `uv` rule was
introduced. The official Kaggle dataset could not be downloaded because Kaggle
API credentials were not available locally.

## Planned command

```bash
cd projects/kaggle-spaceship-titanic/experiments/exp-001/workspace
uv run python train_baseline.py
```

## Expected outputs

- `submission.csv`
- `../results/scores.json`
- `../logs/run.log`

## Observed failure

```text
OSError: Could not find kaggle.json. Make sure it's located in /Users/hiroki-iida/.kaggle.
```

## Notes

Model training was not attempted because `train.csv`, `test.csv`, and
`sample_submission.csv` were not present.
