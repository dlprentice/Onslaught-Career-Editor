# W003 wave closeout

Status: closed — W003 of the read-only fullpass expedition of 2026-07-23;
the reviews are finished and are not being re-run.
Date: 2026-07-23
Verdict: 375 functions reviewed across 15 primary shards — 297 graded
`ok` and 78 non-ok — then re-checked by 15 adversarial shards, which
confirmed 337, disputed 6, upgraded 24 and downgraded 8. The primary table
below is the **pre-adversarial** grading and is not reconciled against those
dispositions.
Evidence: MEASURED over documents, not over bytes — both tables are tallies of
the `- Verdict:` and `- Adversarial disposition:` lines in this wave's 30 shard
files, re-derived and reconciled 2026-07-28. What the shards themselves assert
rests on the 2026-07-23 `analyzeHeadless` static export, not on runtime
observation, and the function names they quote are Ghidra database labels of
that date rather than measured facts — see [`../README.md`](../README.md).

- Closed at: 2026-07-23T20:10:01Z
- Primary shards: 15
- Adversarial shards: 15

## Primary verdict totals

| Verdict | Count |
| --- | --- |
| ok | 297 |
| possible_missing_neighbor | 24 |
| needs_signature | 18 |
| needs_name | 12 |
| needs_comment | 11 |
| needs_tags | 11 |
| needs_boundary | 1 |
| overclaim | 1 |

## Adversarial disposition totals

| Disposition | Count |
| --- | --- |
| confirm | 337 |
| dispute | 6 |
| upgrade_severity | 24 |
| downgrade | 8 |

Parsed dispute total: **6**

## Notes

- Documentation-only; no Ghidra mutation in this wave.
- **The primary table is the pre-adversarial grading.** In this wave the
  adversary disputed 6, upgraded 24 and downgraded 8 of those verdicts; no
  reconciled post-adversarial total is published here. Take the per-address
  outcome from the `- Revised verdict (if changed):` lines in `adversarial/`.
  (Added 2026-07-28.)
- Per-shard details remain under `primary/` and `adversarial/`.
