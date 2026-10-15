# CBattleEngine__IsWalkerGroundedOrCollision

> Source File: UNKNOWN — the previous attribution to `references/Onslaught/game.cpp` is withdrawn below | Binary: BEA.exe (the Ghidra database's specimen, SHA-256 `74154bfa…`)
> Address: `0x004080f0`
> Status: name corrected 2026-07-28; owner file unresolved
> Last updated: 2026-07-28
> The **filename** is retained at the withdrawn name so historical links resolve.

## Name corrections — 2026-07-28

Superseded in place against `ghidra-function-name-table-2026-07-27.tsv`, the
2026-07-27 headless export of the live maintainer Ghidra project. The evidence
grade, and the limits of what a corrected name does and does not establish, are
stated once at [the area index](../_index.md#the-name-corrections-of-2026-07-28).

| Address | Superseded label | Current name | Correction |
| --- | --- | --- | --- |
| `0x004080f0` | `CGame__IsWalkerGroundedOrCollision` | `CBattleEngine__IsWalkerGroundedOrCollision` | class prefix moved; suffix unchanged |

Only the class prefix moved, so the behavioural reading below is unaffected. Two
other lines carried the withdrawn label and now read the current one: the H1 and
the saved signature in the second Note.

**The `Source context` line is withdrawn, and not replaced.** It read
`references/Onslaught/game.cpp` (behavior-level alignment pass). The class is
now `CBattleEngine`, and the signature already names its single argument
`battleEngine`, so game.cpp is no longer the natural owner — but that is a reason
to stop asserting an owner, not a licence to assert `BattleEngine.cpp` instead.
`grep -rn 'IsWalkerGroundedOrCollision' references/Onslaught/` returns **zero
hits**, so the pinned drop supports neither file. Owner: **UNKNOWN**. What would
settle it: a debug-path string constant referenced from inside this function's
extent, of the kind other notes in this directory quote.

---

## Summary

Checks walker-state plus ground/collision condition gate used by movement/camera logic.

## Notes

- Recovered and semantically renamed via headless decompile + batch-rename workflow (2026-02-25).
- 2026-05-09 signature tranche saved `bool __fastcall CBattleEngine__IsWalkerGroundedOrCollision(void * battleEngine)` after metadata/decompile/xref/instruction read-back. *(The saved name in this line read `CGame__IsWalkerGroundedOrCollision` until 2026-07-28; the argument shape is unchanged.)*
- Current owner/source-method identity and concrete layout remain provisional; this is not runtime movement/collision proof.
