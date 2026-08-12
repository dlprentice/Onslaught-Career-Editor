# CBattleEngine__DisplayLock

> Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe (the Ghidra database's specimen, SHA-256 `74154bfa…`)
> Address: `0x00407310`
> Status: source identity promoted in Ghidra 2026-08-04
> Last updated: 2026-08-12
> The **filename** is retained at the withdrawn name so historical links resolve.

## Name corrections — 2026-07-28

Superseded in place against `ghidra-function-name-table-2026-07-27.tsv`, the
2026-07-27 headless export of the live maintainer Ghidra project. The evidence
grade, and the limits of what a corrected name does and does not establish, are
stated once at [the area index](../_index.md#the-name-corrections-of-2026-07-28).

| Address | Superseded label | 2026-07-28 intermediate label (historical) | Correction |
| --- | --- | --- | --- |
| `0x00407310` | `CBattleEngine__IsCurrentResolvedEntry` | `CBattleEngine__IsExpectedCurrentWeapon` | same class; suffix re-read |

## Source-identity promotion — 2026-08-04

The later backed-up, scratch-reproduced, independently refuted and separately
read-back target-lock promotion proves this range as
`CBattleEngine__DisplayLock`. Its live promotion READY is
`local-lab/ghidra-target-lock-semantic-live-promotion-20260804-v2/promotion/promotion.ready.json`,
SHA-256
`77f635e552b7a2dd8425af012204f8172eadcb1de8ecdb02a30e2c12ff9b9945`.
The July comparator interpretation below is retained as historical analysis and
is superseded; it is not the current function contract.

**The rename invalidates part of this note's own supporting argument, and that is
said here rather than left for a reader to notice.** The "Summary" section below
argues that the decompile read-back *supports the name*, and one of the four
signals it lists is the exported signature line, which quoted the withdrawn name
back to itself. That signal is circular now and was always weak. The remaining
three signals — the two neighbouring symbols and the `ret 0x4` evidence — are
untouched and still support a **one-stack-argument boolean comparator**; what
they never established is what the compared thing *is*.

- **MEASURED:** the current symbol is `CBattleEngine__DisplayLock`.

---

## Status

- Named in Ghidra: yes
- Static authority: [Ghidra reference](../../GHIDRA-REFERENCE.md)
- Runtime behavior proof: not yet

## Summary

Historical July interpretation: a small comparator helper. The August 4
source-identity promotion supersedes that description with the bounded
`CBattleEngine::DisplayLock` contract.

The current decompile read-back supports the name with these token-level signals:

- `CBattleEngine__GetIndexedEntry`
- `CGeneralVolume__ResolveCurrentOrFallbackEntry`
- `bool __thiscall CBattleEngine__IsCurrentResolvedEntry(void * this, void * expectedEntry)` in the exported index
- `ret 0x4` instruction evidence

## Interpretation

This helper supports the BattleEngine current/fallback entry-resolution cluster. It is useful context for weapon and target selection paths, but by itself it does not prove gameplay behavior.

The 2026-05-09 early-helper signature tranche hardened this helper from a stale two-argument `int` signature to a one-stack-argument boolean comparator. The exact entry type, concrete `CBattleEngine` layout, local names, tags, runtime target/weapon behavior, and rebuild parity remain open.

## Boundaries

- Does not launch the game.
- Does not mutate `BEA.exe`.
- Does not apply a Ghidra rename map; the signature/comment update was a direct headless postscript dry/apply/read-back pass.
- Does not prove runtime target or weapon selection behavior.
