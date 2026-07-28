# W012 wave closeout

Status: closed — W012 of the read-only fullpass expedition of 2026-07-23;
the reviews are finished and are not being re-run.
Date: 2026-07-23
Verdict: 375 functions reviewed across 15 primary shards — 214 graded
`ok` and 161 non-ok — then re-checked by 15 adversarial shards, which
confirmed 306, disputed 4, upgraded 65 and downgraded 0. The primary table
below is the **pre-adversarial** grading and is not reconciled against those
dispositions.
Evidence: MEASURED over documents, not over bytes — both tables are tallies of
the `- Verdict:` and `- Adversarial disposition:` lines in this wave's 30 shard
files, re-derived and reconciled 2026-07-28. What the shards themselves assert
rests on the 2026-07-23 `analyzeHeadless` static export, not on runtime
observation, and the function names they quote are Ghidra database labels of
that date rather than measured facts — see [`../README.md`](../README.md).

- Closed at: 2026-07-23T22:53:45Z
- Primary shards: 15
- Adversarial shards: 15

## Primary verdict totals

| Verdict | Count |
| --- | --- |
| ok | 214 |
| needs_signature | 117 |
| needs_name | 23 |
| possible_missing_neighbor | 10 |
| needs_tags | 8 |
| needs_comment | 3 |

## Adversarial disposition totals

| Disposition | Count |
| --- | --- |
| confirm | 306 |
| dispute | 4 |
| upgrade_severity | 65 |
| downgrade | 0 |

Parsed dispute total: **4**

## Notes

- Documentation-only; no Ghidra mutation in this wave.
- **The primary table is the pre-adversarial grading.** In this wave the
  adversary disputed 4, upgraded 65 and downgraded 0 of those verdicts; no
  reconciled post-adversarial total is published here. Take the per-address
  outcome from the `- Revised verdict (if changed):` lines in `adversarial/`.
  (Added 2026-07-28.)
- Per-shard details remain under `primary/` and `adversarial/`.
