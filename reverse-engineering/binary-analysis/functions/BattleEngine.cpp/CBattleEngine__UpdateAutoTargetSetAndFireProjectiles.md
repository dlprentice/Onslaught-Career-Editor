# CBattleEngine__UpdateAutoTargetSetAndFireProjectiles

> Address: `0x00406560` | Source family: `references/Onslaught/BattleEngine.cpp`

## Status

- Named in Ghidra: yes
- Fresh read-back: `release/readiness/battleengine_helper_ghidra_readback_2026-05-06.md`
- Runtime behavior proof: not yet

## Summary

Large BattleEngine helper that updates target-selection state and emits projectiles through existing entry-resolution and projectile-add paths.

The current decompile read-back supports the name with these token-level signals:

- `CBattleEngine__GetIndexedEntry`
- `CBattleEngine__IsIndexedEntryUsable`
- `CGeneralVolume__ResolveCurrentOrFallbackEntry`
- `CBattleEngine__SelectNearestForwardTargetFromGlobalSet`
- `CBattleEngine__AddProjectile`
- `CSPtrSet__Remove`

## Interpretation

This is currently the strongest documented retail call-chain anchor connecting BattleEngine entry resolution, target selection, and projectile emission. It supports the existing helper name, but it does not prove the full runtime firing model or source-to-binary identity for every firing-related source branch.

## Boundaries

- Does not launch the game.
- Does not mutate `BEA.exe`.
- Does not apply a Ghidra rename map.
- Does not prove target/firing behavior in a running mission.
