# Function Notes

Status: active — front door for the per-function RE note corpus
Last updated: 2026-07-28
Summary: what these notes are, which naming authority is current, how the
2026-07-28 name corrections were made and what they rest on, and which of this
corpus's known defects are still open.

This directory contains retained, address-specific notes that carry unique
static evidence. A filename or saved symbol is a research label, not a source-
identity or runtime-behavior claim.

Useful starting points:

- [Career save/load](Career.cpp/CCareer__Load.md) — save, progression, ranks, links, goodies, and
  kill tracking.
- [Battle Engine movement](BattleEngine.cpp/CBattleEngine__Move.md) and
  [jet movement](BattleEngineJetPart.cpp/CBattleEngineJetPart__Move.md) — movement, targeting,
  morph support, projectiles, and configuration.
- [Main game loop](game.cpp/CGame__MainLoop.md) — level lifecycle, objectives, respawn,
  camera, and multiplayer predicates.
- [Frontend processing](FrontEnd.cpp/CFrontEnd__Process.md) and [Goodies processing](FEPGoodies.cpp/CFEPGoodies__Process.md) —
  menu and frontend behavior.
- [Unit damage](Unit.cpp/CUnit__ApplyDamage.md) — unit initialization, damage, transform, and effects.

Browse the directory tree for the complete retained set. Generated rollups and
per-owner mirror indexes were removed; Git history preserves them if an old
research label must be traced.

## Naming provenance

**Superseded 2026-07-28.** This section previously read, in full:

> Current corrections and provenance are owned by the
> [full re-audit closeout](../ghidra-full-reaudit-closeout-2026-07-13.md) and
> [reviewed correction plan](../ghidra-reviewed-correction-plan-2026-07-13.json).

Both of those documents still exist and both are still the record of the
2026-07-13 re-audit — nothing about them is withdrawn. What was wrong is the word
**current**: four naming authorities in the parent directory postdate them, and
two of those applied demotions that a 2026-07-13 document cannot know about. A
reader following the old sentence to establish current naming landed two weeks
and two demotions short.

Naming authority, as a dated chain, newest last:

| Date | Document | What it owns |
| --- | --- | --- |
| 2026-07-13 | [full re-audit closeout](../ghidra-full-reaudit-closeout-2026-07-13.md) | the re-audit of that date, and its correction plan |
| 2026-07-13 | [reviewed correction plan](../ghidra-reviewed-correction-plan-2026-07-13.json) | the machine-readable form of the same plan |
| 2026-07-25 | [name-grading ledger](../name-grading-ledger-2026-07-25.md) | the grading instrument, the RTTI re-prefix wave, and the 0x08-byte incident |
| 2026-07-26 | [name-grading ledger](../name-grading-ledger-2026-07-26.md) | the grader corrections, the 13-rename wave, and the first demotion (`0x0048c300`) |
| 2026-07-27 | [second demotion ledger](../name-grading-ledger-2026-07-27-demotion2.md) | the second demotion (`0x005386d0`), re-measured from the pristine specimen |
| 2026-07-27 | `ghidra-function-name-table-2026-07-27.tsv` | **the current address → symbol resolution authority** |

The mechanical check against that last row is
`tools/re_function_doc_names_check.py`. Read its own limits before quoting its
exit code: the table it resolves against is **not tracked in git**, so on any
clone but the maintainer's the check abstains with exit 2 rather than passing.
"I could not look" is not "I found no problem".

## The name corrections of 2026-07-28

A block headed `### Name corrections — 2026-07-28` appears in each note this
sweep touched. Every one of them links here, because the evidence, the grade and
the limits are the same for all of them and belong in one place rather than
repeated forty times.

**What was corrected.** On 2026-07-28 the oracle reported 95 drifted assertions
across 35 documents — an assertion being one "at address A the symbol is N" claim
in a table row, a header, or an address+name code span. 88 of those, in 28
distinct documents, named a symbol the current table contradicts **and did not
mention the current symbol anywhere in the file**, so a reader had no way to
recover the right name from the document. A further 35 live assertions sat in
prose, which the oracle does not gate by default. Those 123 assertions were
corrected in place.

**Evidence.** MEASURED — every "current name" below is read directly out of
`ghidra-function-name-table-2026-07-27.tsv`, the 2026-07-27 headless export of
the live maintainer Ghidra project. That file's own header names its specimen as
`BEA.exe`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
— the pristine image hash — and records that an independent export of the same
database agrees with it on all 7,555 names with 0 differences.

**What the corrections do NOT establish, stated because it is easy to over-read.**

- A current Ghidra symbol is a **research label graded by its evidence**, not a
  proven developer name. Correcting a note to match the database moves the note
  from *contradicting* the database to *agreeing* with it. It does not promote
  the name.
- **UNKNOWN: which naming wave produced each individual rename.** The export's
  header attributes this whole window collectively to "the 580-creation / AIF /
  DPI mutation waves, the 533-name vtable naming wave, and both destructor
  demotions", and no tracked ledger resolves it row by row. The "Correction"
  column in each block therefore describes the *shape* of the change — a class
  prefix moved, a `FUN_` placeholder was replaced, a behavioural suffix was
  re-read — which is an observation about the two strings and not a provenance
  claim. Where a tracked ledger does name the cause, that block cites it.
  What would settle the rest: a per-rename provenance column in the export, or
  the wave scripts' own apply logs, which live in gitignored `local-lab/`.
- Nothing in a corrected note's **behavioural** text was re-derived by this
  sweep. Where a rename disagrees with the behavioural gloss beside it — the one
  measured case is `0x0052e0f0` in
  [AsmInstruction.cpp.md](AsmInstruction.cpp.md) — the disagreement is recorded
  as open rather than resolved by assuming the new name is right.

**Old text is quoted, never deleted.** Each block carries a `Superseded label`
column holding the exact cell text the row used to have. That column heading is
also what stops the checker reading the withdrawn name as a live assertion, so
the correction blocks are themselves gated.

## Wave accounting ratios in these notes are frozen at their wave date

Many notes carry a wave-time closure ratio — `6411/6411 = 100.00%`,
`6410/6410`, `5654/6098`, and thirty-odd others — and several state it in the
present tense ("Static closure **remains** `6411/6411 = 100.00%`"). Read every
one of them as historical.

Those figures were true when their wave ran and have been superseded by function
creation since: the 2026-07-27 export carries **7,555** functions, so no
denominator below 7,555 describes today's database. The figures are kept rather
than rewritten because they are the wave's own record and deleting them would
lose the provenance; the present-tense verbs around them are what is wrong, and
this paragraph is the correction.

`RE-INDEX.md` already carries the other half of this caveat and it is worth
repeating at this door: the 6,411/6,411 closeout was "a metadata/export
accounting result, not a claim that every function is semantically correct".

## What this pass did not fix

Recorded here rather than left implicit, because an unlisted defect gets
re-derived.

- **The header standard is applied only to the notes this sweep touched.** The
  rest of the corpus predates [`DOCUMENTATION.md`](../../../DOCUMENTATION.md) and
  is listed in `tools/doc_header_backlog.txt`. Bulk-normalising the remaining
  notes is deliberately *not* done: the `Source File:` field carries a source-file
  attribution, and several notes' attributions are unsupported rather than merely
  differently formatted — see
  [game.cpp/CGame__ResetRenderStateForWorldRender.md](game.cpp/CGame__ResetRenderStateForWorldRender.md)
  for a case where the attribution is withdrawn. A mechanical retrofit would
  mass-produce exactly that defect under a tidier header.
- **`0x005386d0` has no positive name.** It was demoted to a body label on
  2026-07-27 because the class name it carried was proven false. Whether it earns
  `CPostEventData__Destructor` is open and evidenced work.
- **`0x005385e0` moved to `IScript__HandleMessage` with no tracked ledger.**
  MEASURED: the 2026-07-27 export says so. UNKNOWN: on what evidence. What would
  settle it: the apply log of the wave that renamed it.
- **Two `RET`-shaped false positives** remain in the oracle's prose mode, at
  `game.cpp/CGame__Shutdown.md:28`, where the literal word `RET` after an address
  parses as a symbol. They are an instrument artefact, not a document defect, and
  the document was left alone.
- **One header false positive** remains at
  [Player.cpp/CPlayer__dtor.md](Player.cpp/CPlayer__dtor.md), where the oracle
  pairs the topic H1 with the first address on a line that explicitly labels that
  address with a different, correct symbol. The document is right and the
  instrument is wrong; it is annotated in place rather than "corrected".
