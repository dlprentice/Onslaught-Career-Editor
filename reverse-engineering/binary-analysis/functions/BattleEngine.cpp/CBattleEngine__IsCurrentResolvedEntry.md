# CBattleEngine__IsCurrentResolvedEntry

> Address: `0x00407310` | Source family: `references/Onslaught/BattleEngine.cpp`

## Status

- Named in Ghidra: yes
- Fresh read-back: `release/readiness/ghidra_early_helper_signature_tranche_2026-05-09.md`
- Runtime behavior proof: not yet

## Summary

Small comparator helper that checks whether the current resolved entry matches a supplied entry.

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
