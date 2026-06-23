# Ghidra BattleEngine Transition / Config Correction - 2026-05-10

## Scope

This note records a saved Ghidra name/signature/comment correction tranche for four transition, ground-effect, burst-timestamp, and BattleEngine configuration helpers. It is public-safe static RE evidence only: no BEA launch, no debugger attach, no executable patching, no installed-game mutation, and no private decompile excerpt is included here.

## Saved Targets

| Address | Prior saved name | Current saved name | Saved signature boundary |
| --- | --- | --- | --- |
| `0x0040eeb0` | `CUnit__FinishedPlayingCurrentAnimation` | `CBattleEngine__FinishedPlayingCurrentAnimation` | `int __thiscall ...(void * this)` |
| `0x0040ef20` | `CMonitor__SpawnGroundOrAirImpactEffect` | `CBattleEngine__GroundParticleEffect` | `void __thiscall ...(void * this)` |
| `0x0040f110` | `CEngine__ClampBurstStartTimeFloorNow` | `CEngine__ClampBurstStartTimeFloorNow` | `void __thiscall ...(void * this)` |
| `0x0040f2f0` | `CBattleEngine__GetWeaponProfileByIndex` | `BattleEngineConfigurations__GetConfiguration` | `void * __cdecl ...(int configurationId)` |

## Evidence Summary

- Source/decompile comparison found that `0x0040f2f0` matches `UBattleEngineConfigurations::GetConfiguration(int)`, not a BattleEngine weapon-profile accessor.
- Source/decompile comparison found that `0x0040eeb0` matches `CBattleEngine::FinishedPlayingCurrentAnimation()` transition-completion logic, superseding the earlier broad `CUnit` owner label.
- Source/decompile comparison found that `0x0040ef20` matches `CBattleEngine::GroundParticleEffect()` water/terrain altitude particle logic, superseding the earlier `CMonitor` effect label.
- Headless dry/apply saved the four names/signatures/comments with dry `updated=0 skipped=4 missing=0 bad=0` and apply `updated=4 skipped=0 missing=0 bad=0`.
- Final metadata and decompile read-back found `4/4` targets.
- Final xref export produced `10` xref rows across the targets.
- Final instruction export produced `692` instruction rows across the targets.
- The focused probe reports `4` corrected targets, `0` stale token hits, and `0` overclaim hits.

## Boundary

This tranche corrects saved Ghidra ownership/name mistakes and removes selected `param_N` signature debt. It does not claim local-variable cleanup is complete; the post-signature decompiler still emits temporary names in some bodies.

The tranche does not prove concrete object layouts, tags, local-variable names, structure types, runtime animation/particle/configuration behavior, BEA launch behavior, game patching, or rebuild parity. It also does not close exact retail `CBattleEngine::WeaponFired`, `weapon_fire_breaks_stealth`, runtime cloak activation, or fire-while-cloaked behavior.
