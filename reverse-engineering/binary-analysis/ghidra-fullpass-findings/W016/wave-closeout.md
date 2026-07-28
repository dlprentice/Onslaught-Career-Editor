# W016 wave closeout

Status: closed — W016 of the read-only fullpass expedition of 2026-07-23;
corrected in place 2026-07-28 — see the note under the primary table.
Date: 2026-07-23
Verdict: 375 functions reviewed across 15 primary shards — 365 graded
`ok` and 10 non-ok — then re-checked by 15 adversarial shards, which
confirmed 321, disputed 0, upgraded 54 and downgraded 0. The primary table
below is the **pre-adversarial** grading and is not reconciled against those
dispositions.
Evidence: MEASURED over documents, not over bytes — both tables are tallies of
the `- Verdict:` and `- Adversarial disposition:` lines in this wave's 30 shard
files, re-derived and reconciled 2026-07-28. What the shards themselves assert
rests on the 2026-07-23 `analyzeHeadless` static export, not on runtime
observation, and the function names they quote are Ghidra database labels of
that date rather than measured facts — see [`../README.md`](../README.md).

- Closed at: 2026-07-23T23:57:17Z
- Primary shards: 15
- Adversarial shards: 15

## Primary verdict totals

| Verdict | Count |
| --- | --- |
| ok | 365 |
| needs_comment | 9 |
| needs_tags | 1 |

> **Corrected 2026-07-28 — one invented verdict row removed and folded back.**
> The table above read:
>
> ```
> | needs_comment | 8 |
> | needs_comment; | 1 |
> | needs_tags | 1 |
> ```
>
> `needs_comment;` is not a verdict. The wave taxonomy is the nine values `ok`,
> `needs_name`, `needs_signature`, `needs_comment`, `needs_tags`,
> `needs_boundary`, `possible_missing_neighbor`, `overclaim`, `inconclusive`.
> The row is a rollup artefact of splitting a *compound* verdict string on
> whitespace: `primary/A13.md` carries `- Verdict: needs_comment; needs_tags`,
> where the rest of the corpus writes the compound with ` + `. Tallied by
> leading verdict token, this wave's 15 primary shard bodies give `ok 365`,
> `needs_comment 9`, `needs_tags 1` — 375, matching `- Function count:`. So
> `needs_comment` was reported as 8 and is 9. **Unchanged:** `ok`, `needs_tags`,
> every adversarial disposition, and every per-function verdict in the shards.
> Nothing was re-graded; the shard verdict line was deliberately left as its
> author wrote it.

## Adversarial disposition totals

| Disposition | Count |
| --- | --- |
| confirm | 321 |
| dispute | 0 |
| upgrade_severity | 54 |
| downgrade | 0 |

Parsed dispute total: **0**

## Notes

- Documentation-only; no Ghidra mutation in this wave.
- **The primary table is the pre-adversarial grading.** In this wave the
  adversary disputed 0, upgraded 54 and downgraded 0 of those verdicts; no
  reconciled post-adversarial total is published here. Take the per-address
  outcome from the `- Revised verdict (if changed):` lines in `adversarial/`.
  (Added 2026-07-28.)
- Per-shard details remain under `primary/` and `adversarial/`.
