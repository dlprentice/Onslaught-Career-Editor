# CBattleEngine__GroundParticleEffect

> Address: `0x0040ef20` | Source family: `references/Onslaught/BattleEngine.cpp`

## Status

- Named in Ghidra: yes
- Saved signature: `void __thiscall CBattleEngine__GroundParticleEffect(void * this)`
- Static authority: [Ghidra reference](../../GHIDRA-REFERENCE.md)
- Runtime behavior proof: not yet

## Summary

BattleEngine ground-effect helper that samples water/terrain height, chooses the land or water particle effect, and positions the effect near the BattleEngine instance position when altitude is below the source threshold.

The current Ghidra correction supersedes the older `CMonitor__SpawnGroundOrAirImpactEffect` label. Source/decompile evidence supports `CBattleEngine::GroundParticleEffect()`.

## Evidence

- Source anchor: `CBattleEngine::GroundParticleEffect()` in `references/Onslaught/BattleEngine.cpp`.
- Read-back tokens include the water/terrain height comparison, static ground-effect resources, particle creation, and position fields around `this+0x1c..0x28`.
- Saved signature uses a `this` pointer and removes the old generic `param_1` signature.

## Boundaries

- Does not prove runtime particle behavior in a mission.
- Does not prove concrete `CBattleEngine` layout, tags, local variable names, or structure types.
- Does not mutate `BEA.exe`.
- Does not close rebuild parity.
