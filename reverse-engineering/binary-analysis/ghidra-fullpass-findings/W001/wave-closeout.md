# W001 wave closeout

Status: closed — W001 of the read-only fullpass expedition of 2026-07-23;
the reviews are finished and are not being re-run.
Date: 2026-07-23
Verdict: 375 functions reviewed across 15 primary shards — 213 graded
`ok` and 162 non-ok — then re-checked by 15 adversarial shards, which
confirmed 331, disputed 12, upgraded 21 and downgraded 11. The primary table
below is the **pre-adversarial** grading and is not reconciled against those
dispositions.
Evidence: MEASURED over documents, not over bytes — both tables are tallies of
the `- Verdict:` and `- Adversarial disposition:` lines in this wave's 30 shard
files, re-derived and reconciled 2026-07-28. What the shards themselves assert
rests on the 2026-07-23 `analyzeHeadless` static export, not on runtime
observation, and the function names they quote are Ghidra database labels of
that date rather than measured facts — see [`../README.md`](../README.md).

- Closed at: 2026-07-23T19:38:38Z
- Primary shards: 15
- Adversarial shards: 15

## Primary verdict totals

| Verdict | Count |
| --- | --- |
| ok | 213 |
| needs_tags | 66 |
| needs_name | 31 |
| needs_comment | 26 |
| possible_missing_neighbor | 23 |
| needs_signature | 13 |
| overclaim | 2 |
| inconclusive | 1 |

## Adversarial disposition totals

| Disposition | Count |
| --- | --- |
| confirm | 331 |
| dispute | 12 |
| upgrade_severity | 21 |
| downgrade | 11 |

Parsed dispute total: **12**

## Notes

- Documentation-only; no Ghidra mutation in this wave.
- **The primary table is the pre-adversarial grading.** In this wave the
  adversary disputed 12, upgraded 21 and downgraded 11 of those verdicts; no
  reconciled post-adversarial total is published here. Take the per-address
  outcome from the `- Revised verdict (if changed):` lines in `adversarial/`.
  (Added 2026-07-28.)
- Per-shard details remain under `primary/` and `adversarial/`.
