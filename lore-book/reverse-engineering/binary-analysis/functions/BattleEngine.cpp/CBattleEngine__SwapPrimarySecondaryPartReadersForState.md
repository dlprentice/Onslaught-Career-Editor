# CBattleEngine__SwapPrimarySecondaryPartReadersForState

> Address: `0x00406460` | Source family: `references/Onslaught/BattleEngine.cpp`

## Status

- Named in Ghidra: yes
- Fresh read-back: `release/readiness/battleengine_helper_ghidra_readback_2026-05-06.md`
- Runtime behavior proof: not yet

## Summary

State-gated helper that swaps primary/secondary active reader pointers and reattaches related part links while the BattleEngine changes state.

The current decompile read-back supports the name with these token-level signals:

- state checks around `+0x260`
- reader/swap fields around `+0x5ec`, `+0x5f0`, and `+0x5f4`
- active part link updates around `+0x30` and `+0x70`
- `CMCMech__Reset`
- `CInfluenceMap__SetTrackedThingAndClearCachedObject`

## Interpretation

This helper is a likely retail-binary support point for source-side BattleEngine transform state changes, but the current proof is decompile token read-back only. It does not prove the full source `CBattleEngine::Morph` body or runtime transform behavior.

## Boundaries

- Does not launch the game.
- Does not mutate `BEA.exe`.
- Does not apply a Ghidra rename map.
- Does not prove gameplay-state interpretation.
