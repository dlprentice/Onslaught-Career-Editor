# Ghidra Reference

This is the active workflow reference for the Steam `BEA.exe` analysis. The
maintainer's loaded database and executable are local proprietary inputs. The
reviewed canonical snapshot under [`../ghidra/`](../ghidra/) and narrow
metadata projections are the explicit tracked evidence exceptions.

## Current authority

Select campaign state only through `developer_state.json` →
`current_re_authority`. Select rolling tracked/live Ghidra state through
[`../ghidra/README.md`](../ghidra/README.md) plus fresh inspection. The dated
history below is evidence chronology, not a live routing table.

The [2026-07-13 full re-audit closeout](ghidra-full-reaudit-closeout-2026-07-13.md)
verified the trusted 6,411-address snapshots, reviewed the 459-address metadata
delta, and independently re-reviewed 92 unique correction targets. Ninety-one
were confirmed and applied; the proposed `0x004dac90` ABI correction was
rejected. Exact outcomes and before/after metadata are recorded in the
[reviewed correction plan](ghidra-reviewed-correction-plan-2026-07-13.json).
The closeout numbers do not mean that all names, prototypes, semantics,
layouts, or behaviors are proven.

> **Corrected 2026-07-28 — the closeout is a record, not the current name
> state.** The paragraph above is unchanged and still accurate about what the
> 2026-07-13 audit did. What it omitted is that the "trusted 6,411-address
> snapshots" it describes have since been overtaken. Established in tracked
> evidence: the inventory grew **6,411 → 6,969**
> ([re-coverage-baseline-2026-07-25.md](re-coverage-baseline-2026-07-25.md));
> **332** RTTI re-prefixes, then **13** renames and **two** destructor
> demotions, were applied to the live database. **The current record of which
> names are demoted is the three name-grading ledgers**, not this closeout:
> [2026-07-25](name-grading-ledger-2026-07-25.md) (read its banner — two of its
> figures are superseded), [2026-07-26](name-grading-ledger-2026-07-26.md),
> [2026-07-27](name-grading-ledger-2026-07-27-demotion2.md).
>
> Later waves raised the saved live/tracked inventory to 8,136 functions by
> 2026-08-12. The first verified 2026-08-13 Mission-registry promotion admitted
> 34 additional callable starts as default-metadata Function objects; the later
> separate ceremony normalized 75 reviewed existing-entry names/comments/tags.
> A still-later separate ceremony gave the 34 new entries bounded Tier-2
> registry names/comments/tags while preserving every body and ABI/storage
> field. The 2026-08-14 text-gap ceremony then added 31 reviewed default-
> metadata boundaries while preserving all 8,170 PRE rows exactly. A later
> external-table ceremony added 79 more default-metadata boundaries while
> preserving all 8,201 PRE rows exactly. The five-body repair kept the census
> at 8,280 and changed only five reviewed body rows. The latest JPEG/IJG
> promotion adds 24 default-metadata functions while preserving every PRE row,
> advancing exact saved-body ownership to 93.840186987%. The later CRT P0
> promotion adds 23 default-metadata functions while preserving all 8,304 PRE
> rows and advances exact saved-body ownership to 93.898814846%. The later CRT
> EH parent-range repair keeps all 8,327 entries, preserves all 8,326 non-target
> rows, joins one split parent body, and advances exact ownership to
> 93.900110776%. The later D3DX promotion added two exact DEFAULT-source
> functions while preserving all 8,327 PRE rows, advancing the then census
> to 8,329/db.18618 and exact ownership to 93.912966399%. Rolling
> project state is owned by
> [`../ghidra/README.md`](../ghidra/README.md).
> The D3DX-era saved census and lower bound were 8,329, not a ceiling. That
> 8,329-row db.18618 projection and its live-state
> receipts are reconciled in
> [`../../../ghidra-functions.md`](../ghidra-functions.md); the 6,411- and
> 7,555-row states remain dated history only.

## Safe workflow

1. Record the executable specimen and database identity without committing
   either payload.
2. Export only the smallest metadata, xref, instruction, or decompile slice
   needed for the question.
3. Separate observed bytes and control flow from inferred names or source
   vocabulary.
4. For a metadata mutation, create and verify a local backup, review the exact
   before/after rows, apply once, and read the rows back.
5. Keep the final bounded conclusion in the owning contract or per-function
   note. Do not create another wave, readiness packet, mirror, or generated
   inventory.

Reusable scripts under [`tools/`](../../tools/README.md) include read-only
address, disassembly, metadata, tag, scalar, vtable, and xref exporters plus
reviewed TSV correction helpers. One-off applied mutation scripts live in Git
history.

## Boundaries

- Static evidence does not prove live gameplay, patch safety, or exact source
  identity.
- Reference source may suggest vocabulary but does not override the retail
  body.
- Never commit a live/alternate Ghidra project, backup, executable, raw
  debugger transcript, or copied game payload. The reviewed canonical snapshot
  under `reverse-engineering/ghidra/` is the single explicit Ghidra exception.
- Never mutate the installed game as part of analysis.
