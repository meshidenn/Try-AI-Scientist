# Artifact Audit

## Verdict

WARN

## Checked Artifacts

- `spec.yaml`
- `README.md`
- `results/results.md`
- `results/scores.json`
- `results/claims.json`

## Blocking Issues

- Baseline has not been executed yet, so no measurement can be interpreted.

## Warnings For Interpretation

- Do not claim FP8 slowdown until both variants complete under the same
  benchmark settings.
- If vLLM does not expose speculative acceptance metrics directly, acceptance
  evidence must be derived from server metrics/logs and documented as such.

## Notes

Initial scaffold audit only.
