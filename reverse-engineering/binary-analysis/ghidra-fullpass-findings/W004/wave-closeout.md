# W004 wave closeout

Status: closed — W004 of the read-only fullpass expedition of 2026-07-23;
the reviews are finished and are not being re-run.
Date: 2026-07-23
Verdict: 375 functions reviewed across 15 primary shards — 260 graded
`ok` and 115 non-ok — then re-checked by 15 adversarial shards, which
confirmed 334, disputed 5, upgraded 24 and downgraded 12. The primary table
below is the **pre-adversarial** grading and is not reconciled against those
dispositions.
Evidence: MEASURED over documents, not over bytes — both tables are tallies of
the `- Verdict:` and `- Adversarial disposition:` lines in this wave's 30 shard
files, re-derived and reconciled 2026-07-28. What the shards themselves assert
rests on the 2026-07-23 `analyzeHeadless` static export, not on runtime
observation, and the function names they quote are Ghidra database labels of
that date rather than measured facts — see [`../README.md`](../README.md).

- Closed at: 2026-07-23T20:31:51Z
- Primary shards: 15
- Adversarial shards: 15
- Refreshed after late B02 overwrite (ops state untouched).

## Primary verdict totals

| Verdict | Count |
| --- | --- |
| ok | 260 |
| needs_tags | 36 |
| needs_signature | 28 |
| possible_missing_neighbor | 28 |
| needs_name | 9 |
| overclaim | 6 |
| needs_comment | 5 |
| needs_boundary | 3 |

## Adversarial disposition totals

| Disposition | Count |
| --- | --- |
| confirm | 334 |
| dispute | 5 |
| upgrade_severity | 24 |
| downgrade | 12 |

Parsed dispute total: **5**

## Notes

- Documentation-only; no Ghidra mutation in this wave.
- **The primary table is the pre-adversarial grading.** In this wave the
  adversary disputed 5, upgraded 24 and downgraded 12 of those verdicts; no
  reconciled post-adversarial total is published here. Take the per-address
  outcome from the `- Revised verdict (if changed):` lines in `adversarial/`.
  (Added 2026-07-28.)
- Per-shard details remain under `primary/` and `adversarial/`. (Repaired
  2026-07-28: this line read "under primary/ and " followed by a literal BEL
  control character (U+0007) and "dversarial." — the rollup generator emitted
  a non-raw `\adversarial` escape. A mangled word and a stray control byte,
  not a changed claim; the other 17 closeouts carry the intended wording.)
