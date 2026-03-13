# Widescreen Diff Unresolved Tracker

> Canonical unresolved subset tracker for `widescreen-diff-regions-28.tsv`
> Last updated: 2026-03-01

## Summary

| Metric | Value |
|---|---|
| Total diff regions | 28 |
| `known-functional` | 14 |
| `known-supporting` | 14 |
| `unknown-needs-RE` | 0 |

## Unknown Region Queue

No unresolved regions remain in the current canonical 28-region map.

| region_id | file_off_start | file_off_end | va_start | va_end | blocker | next_probe |
|---|---|---|---|---|---|---|
| _none_ | - | - | - | - | - | - |

## Reopen Criteria

Reopen this queue when any of the following occurs:

1. A new widescreen binary variant is introduced.
2. A region classification in `widescreen-diff-regions-28.tsv` is downgraded to `unknown-needs-RE`.
3. New contradictory behavior evidence appears for an already-classified region.

## Canonical Inputs

- `reverse-engineering/binary-analysis/widescreen-diff-regions-28.tsv`
- `reverse-engineering/binary-analysis/widescreen-patch-analysis.md`
- `reverse-engineering/binary-analysis/widescreen-regions-8-11-validation.md`

