# Ghidra CThing Core Wave516 Readiness

Status: static read-back complete
Date: 2026-05-17

## Scope

Wave516 saved name/signature/comment/tag hardening for 22 CThing, CCSPersistentThing, and collision-seeking adjacency helpers:

- `0x004f33e0` `CThing__ctor_base`
- `0x004f3480` `CThing__scalar_deleting_dtor`
- `0x004f34a0` `CThing__Init`
- `0x004f35d0` `CThing__InitRenderThing`
- `0x004f3600` `CThing__Shutdown`
- `0x004f3640` `CThing__dtor_base`
- `0x004f36d0` `CThing__Render`
- `0x004f3710` `CThing__RenderImposter`
- `0x004f3730` `CThing__HandleEvent`
- `0x004f37c0` `CThing__DrawDebugCuboid`
- `0x004f3940` `CThing__GetBoundingRadius`
- `0x004f3970` `CThing__SetObjective`
- `0x004f39b0` `CThing__UpdatePosition`
- `0x004f39c0` `CThing__InitCollisionSeekingThing`
- `0x004f3a50` `CCSPersistentThing__scalar_deleting_dtor`
- `0x004f3a70` `CCSPersistentThing__dtor_base`
- `0x004f3ac0` `CThing__GetCentrePos`
- `0x004f3c50` `CThing__StickToGround`
- `0x004f3cb0` `CThing__MoveTo`
- `0x004f3ce0` `CThing__Teleport`
- `0x004f3d10` `CThing__GetPersistentCollisionSeekingThing`
- `0x004f3de0` `CThing__IsOverWater`

The pass applied 15 renames, including correcting stale `CUnit__DebugTraceIfFlag30Set`, `CThing__AddCollision`, `CUnitAI__GetWorldPositionForTargeting`, and `CCollisionSeekingRound__GetCollisionComponentOrNull` owner/name labels into the source-supported CThing neighborhood.

## Evidence

- Pre-state exports: `subagents/ghidra-static-reaudit/wave516-cthing-core-004f33e0/pre_*`.
- Mutation script: `tools/ApplyCThingCoreWave516.java`.
- Dry run: `updated=0 skipped=22 renamed=0 would_rename=15 missing=0 bad=0`.
- Apply run: `updated=22 skipped=0 renamed=15 would_rename=0 missing=0 bad=0`.
- Verify dry run: `updated=0 skipped=22 renamed=0 would_rename=0 missing=0 bad=0`.
- Post read-back: `22` metadata rows, `22` tag rows, `416` xref rows, `4862` instruction rows, and `22` decompile exports.
- Focused probe: `tools/ghidra_cthing_core_wave516_probe.py --check`.
- Queue refresh after Wave516: `6078` functions, `2433` commented, `3645` commentless, `1610` exact-undefined signatures, and `1403` `param_N` signatures.
- Current whole-project telemetry proxy: comment-backed `2433/6078 = 40.03%`; strict comment-plus-clean-signature proxy `2379/6078 = 39.14%`.
- Backup verified at `[maintainer-local-ghidra-backup-root]\BEA_20260517-204846_post_wave516_cthing_core_verified` with `19` files, `158501767` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Claim Boundary

This is static Ghidra metadata evidence only. It improves source-parity readability for CThing construction, init, render, position, objective, collision-seeking, and water/terrain helpers. It does not prove runtime object lifecycle behavior, runtime rendering, runtime collision behavior, exact structure layouts, exact source-body identity for every optimized retail helper, BEA patching, or rebuild parity.
