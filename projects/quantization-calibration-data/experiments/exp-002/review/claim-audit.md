# Claim Audit

## Verdict

PASS

## Checked Claims

- Three NVFP4 W4A4 pilot variants were produced.
- The pilot variants used 20 synthetic calibration samples and `max_seq_length=2048`.
- Held-out synthetic NLL evaluation was run for base and all three variants.
- Matched calibration did not win on the current synthetic NLL matrix.
- The current pilot is not final evidence about real calibration-domain effects.

## Unsupported Or Overstated Claims

None found in the updated artifacts.

## Notes

The updated interpretation correctly treats the matched-domain result as weak pilot evidence and avoids claiming that calibration-domain effects are resolved.
