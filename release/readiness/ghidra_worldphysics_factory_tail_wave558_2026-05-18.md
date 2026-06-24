# Ghidra WorldPhysicsManager Factory Tail Wave558 Readiness Note

Date: 2026-05-18

Wave558 saved static Ghidra name/signature/comment/tag evidence for 22 adjacent targets from `0x0050f610` through `0x005102a0`.

## Saved Scope

- Scalar-deleting destructor wrappers: `CRelaxedSquad__scalar_deleting_dtor`, `CMissile__scalar_deleting_dtor`, `CGillMHead__scalar_deleting_dtor`, `CTentacle__scalar_deleting_dtor`, `CComponent__scalar_deleting_dtor`, `CExplosion__scalar_deleting_dtor`, `CHazard__scalar_deleting_dtor`.
- Factory/list signatures: `CWorldPhysicsManager__CreateWeaponByIndex`, `CWorldPhysicsManager__CreateProjectile`, `CWorldPhysicsManager__CreateSpawner`, `CWorldPhysicsManager__CreateCharacter`, `CWorldPhysicsManager__CreatePickup`, `CWorldPhysicsManager__CreateEffect`, `CWorldPhysicsManager__CreateTrigger`, `CWorldPhysicsManager__InitializeLists`.
- Destructor bodies: `CRelaxedSquad__Destructor`, `CMissile__Destructor`, `CComponent__Destructor`, `CGillMHead__Destructor_VFunc01`, `CTentacle__Destructor`, `CExplosion__Destructor`, `CHazard__Destructor`.

## Evidence

- `ApplyWorldPhysicsFactoryTailWave558.java` dry run: `updated=0 skipped=22 renamed=0 would_rename=7 missing=0 bad=0`.
- Apply: `updated=22 skipped=0 renamed=7 would_rename=0 missing=0 bad=0`.
- Final dry verification: `updated=0 skipped=22 renamed=0 would_rename=0 missing=0 bad=0`.
- Read-back exports: `22` metadata rows, `22` tag rows, `50` xref rows, and `22` decompile rows.
- Focused probe: `tools/ghidra_worldphysics_factory_tail_wave558_probe.py`.

## Queue Telemetry

Post-Wave558 queue refresh:

- Total functions: `6089`
- Commented: `2750`
- Commentless: `3339`
- Exact-undefined signatures: `1516`
- `param_N` signatures: `1213`
- Strict clean-signature proxy: `2696/6089 = 44.28%`

## Limits

This is static retail-binary evidence only. Exact definition schemas, concrete object layouts, source method identities, runtime factory/list/lifecycle behavior, BEA launch, patching, and rebuild parity remain unproven.
