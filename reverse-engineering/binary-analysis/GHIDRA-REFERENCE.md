# Ghidra Reference

This is the active workflow reference for the Steam `BEA.exe` analysis. The
loaded database and executable are local proprietary inputs and are never
tracked.

## Current authority

The [2026-07-13 full re-audit closeout](ghidra-full-reaudit-closeout-2026-07-13.md)
verified the trusted 6,411-address snapshots, reviewed the 459-address metadata
delta, and independently re-reviewed 92 unique correction targets. Ninety-one
were confirmed and applied; the proposed `0x004dac90` ABI correction was
rejected. Exact outcomes and before/after metadata are recorded in the
[reviewed correction plan](ghidra-reviewed-correction-plan-2026-07-13.json).
The closeout numbers do not mean that all names, prototypes, semantics,
layouts, or behaviors are proven.

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
- Never commit a Ghidra project, backup, executable, raw debugger transcript,
  or copied game payload.
- Never mutate the installed game as part of analysis.
