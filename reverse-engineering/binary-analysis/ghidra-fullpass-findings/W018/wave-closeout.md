# W018 wave closeout

Status: closed — W018 of the read-only fullpass expedition of 2026-07-23;
the reviews are finished and are not being re-run.
Date: 2026-07-24
Verdict: 36 functions reviewed across 2 primary shards — 32 graded
`ok` and 4 non-ok — then re-checked by 2 adversarial shards, which
confirmed 36, disputed 0, upgraded 0 and downgraded 0. The primary table
below is the **pre-adversarial** grading and is not reconciled against those
dispositions.
Evidence: MEASURED over documents, not over bytes — both tables are tallies of
the `- Verdict:` and `- Adversarial disposition:` lines in this wave's 4 shard
files, re-derived and reconciled 2026-07-28. What the shards themselves assert
rests on the 2026-07-23 `analyzeHeadless` static export, not on runtime
observation, and the function names they quote are Ghidra database labels of
that date rather than measured facts — see [`../README.md`](../README.md).

- Closed at: 2026-07-24T00:21:59Z
- Primary shards: 2
- Adversarial shards: 2

## Primary verdict totals

| Verdict | Count |
| --- | --- |
| ok | 32 |
| needs_comment | 4 |

## Adversarial disposition totals

| Disposition | Count |
| --- | --- |
| confirm | 36 |
| dispute | 0 |
| upgrade_severity | 0 |
| downgrade | 0 |

Parsed dispute total: **0**

## Notes

- Documentation-only; no Ghidra mutation in this wave.
- **The primary table is the pre-adversarial grading.** In this wave the
  adversary disputed 0, upgraded 0 and downgraded 0 of those verdicts; no
  reconciled post-adversarial total is published here. Take the per-address
  outcome from the `- Revised verdict (if changed):` lines in `adversarial/`.
  (Added 2026-07-28.)
- Per-shard details remain under `primary/` and `adversarial/`.
