# Ghidra WorldPhysicsManager Cleanup Resolve Wave559 Readiness Note

Date: 2026-05-18

Wave559 saved static Ghidra signature/comment/tag evidence for 15 adjacent WorldPhysicsManager cleanup, resolve, and add-by-name targets from `0x00510e60` through `0x00511ad0`. The bounded probe label for this tranche is `WorldPhysicsManager cleanup/resolve`.

## Saved Scope

- Definition cleanup helpers: `CWorldPhysicsManager__FreeEntryOwnedPtrs_00_0C_20`, `CWorldPhysicsManager__FreeRoundStatement`, `CWorldPhysicsManager__FreeWeaponModeStatement`, `CWorldPhysicsManager__FreeWeaponStatement`, `CWorldPhysicsManager__FreeTagDefinitionEntry`, `CWorldPhysicsManager__FreeThingOrComponentDefinitionEntry`, and `CWorldPhysicsManager__ClearEntryWorkSets_40_50`.
- Name/tag resolve helpers: `CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName`, `CWorldPhysicsManager__MapGunOrSpawnerTagToIndex`, `CWorldPhysicsManager__ResolveTagListNameToIndex_E8`, `CWorldPhysicsManager__ResolveTagListNameToIndex_EC`, and `CWorldPhysicsManager__ResolveTagListNameToIndex_F0`.
- Add-by-name helpers: `CWorldPhysicsManager__AddComponentByName`, `CWorldPhysicsManager__AddWeaponByName`, and `CWorldPhysicsManager__AddSpawnerByName`.

## Evidence

- `ApplyWorldPhysicsCleanupResolveWave559.java` dry run: `updated=0 skipped=15 renamed=0 would_rename=0 missing=0 bad=0`.
- Apply: `updated=15 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`.
- Final dry verification: `updated=0 skipped=15 renamed=0 would_rename=0 missing=0 bad=0`.
- Read-back exports: `15` metadata rows, `15` tag rows, `22` xref rows, `418` focused callsite instruction rows, and `15` decompile rows.
- Focused probe: `tools/ghidra_worldphysics_cleanup_resolve_wave559_probe.py`.

## Queue Telemetry

Post-Wave559 queue refresh:

- Total functions: `6089`
- Commented: `2765`
- Commentless: `3324`
- Exact-undefined signatures: `1513`
- `param_N` signatures: `1201`
- Strict clean-signature proxy: `2711/6089 = 44.52%`

## Limits

This is static retail-binary evidence only. Exact definition schemas, concrete list/owner layouts, source method identities, runtime cleanup/resolve/add-by-name behavior, BEA launch, patching, and rebuild parity remain unproven.
