# Next Plan

## Immediate

- Fix the fixture generator missing-value warning.
- Rerun the fixture after the fix to ensure results remain reproducible.
- Add an experiment that compares at least two sklearn models under the same
  artifact contract.

## Kaggle Path

- Add `kaggle.json` or manually place official CSV files under
  `exp-001/workspace/data`.
- Rerun `exp-001` on official Kaggle data.
- Submit `workspace/submission.csv` and record public leaderboard score in
  `scores.json`.
