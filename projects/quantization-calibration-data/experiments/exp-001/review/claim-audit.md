# Claim Audit

## Verdict

PASS

## Checked Claims

- The 8-bit non-pathological robustness claim is directly supported by `results/results.md` and `results/scores.json`.
- The 4-bit non-pathological range claim is directly supported by the result table.
- The `blank_zeros_200` collapse claim is directly supported by `scores.json` and `logs/run.log`.
- The limitation claim is supported by `review/artifact-audit.md` and `results/results.md`.

## Unsupported Or Overstated Claims

None found.

## Notes

The interpretation correctly avoids claiming that representative calibration was always best. In this single-run toy setup, `small_20` and `high_intensity_200` tied for best 4-bit accuracy.
