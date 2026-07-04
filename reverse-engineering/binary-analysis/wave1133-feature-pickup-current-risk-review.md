# Wave1133 Feature/Pickup Current-Risk Review

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1133-feature-pickup-current-risk-review`

Wave1133 accounts for `6 rows` from the Wave1108 current focused continuity denominator as a feature/pickup spawn bridge cluster. This wave uses fresh Ghidra export evidence as a read-only review and makes no mutation. Current focused accounting moves to `184/1179 = 15.61%` of the continuity denominator. The current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 995. Static closure debt remains `0 / 0 / 0` for commentless / exact-undefined / `param_N`.

Covered anchors:

| Address | Static evidence |
| --- | --- |
| `0x00442710 CDestroyableSegment__SpawnConfiguredPickup` | Destroyable-segment pickup helper reached by segment/rubble effects paths; reads owner/config through `this+0x3c`, uses profile/config `+0xe8`, calls `CWorldPhysicsManager__CreatePickup`, resolves type context through `DAT_008553f8`, and dispatches the created pickup vfunc. |
| `0x0044ca30 CFeature__Init` | Feature init copies feature data from `init+0x3bc`, builds resource/object state, calls `CActor__Init`, adds occupancy context, updates shadows, and preserves random-sample setup evidence. |
| `0x0044cbe0 CFeature__ShutdownAndRemoveFromWorld` | Feature shutdown calls `CSoundManager__KillSamplesForThing`, `CWorld__RemoveUnitFromOccupancyGrid_Thunk`, `CStaticShadows__UpdateVisibility(feature,1)`, and then forwards to base cleanup. |
| `0x0044cee0 CFeature__MaybeSpawnRandomPickupFromData` | Feature-adjacent randomized pickup helper gates on feature data at `+0xe4`, samples transform/random thresholds, calls `CWorldPhysicsManager__CreatePickup`, resolves `DAT_008553f8`, and dispatches the pickup init vfunc. |
| `0x0044e300 PickupSpawn__MaybeSpawnAttachedPickupFromFrame_0044e300` | Owner-neutral attached pickup helper gates on `+0x164`, resolves frame/transform context, uses profile `+0xec`, calls `CWorldPhysicsManager__CreatePickup`, resolves `DAT_008553f8`, and dispatches the pickup init vfunc. |
| `0x004fd230 CUnit__SpawnProfileDropPickup` | Unit-family profile drop helper reached from AirUnit, Plane, hit, reset, UnitAI, and event paths; uses profile `+0xe8`, copies side/team `this+0x138` and world position `this+0x1c..0x28`, derives a small init flag from vfunc `+0x10c` or `HeightDelta__Below025_D0`, and initializes the pickup through vfunc `+0x24`. |

Context rows re-read: `0x0040dfb0 CGeneralVolume__SpawnPickupAndDispatch` and `0x004ef100 CUnit__VFunc64_SpawnConfiguredPickupThreeTimes`. Both remain important pickup-spawn context, but they were already accounted by earlier current-risk waves and are not counted as new Wave1133 primary rows.

Mutation status:

- Read-only review.
- No Ghidra mutation.
- No rename.
- No signature change.
- No comment change.
- No tag change.
- No function-boundary change.
- No executable-byte change.
- No BEA launch, installed-game mutation, or runtime-file mutation.

Evidence:

- Primary metadata/tag/xref/instruction/decompile exports: `6` / `6` / `22` / `681` / `6`.
- Context metadata/tag/xref/instruction/decompile exports: `2` / `2` / `4` / `180` / `2`.
- Primary logs report `targets=6 found=6 missing=0`, `rows=6 missing=0`, `Wrote 22 rows`, `Wrote 681 function-body instruction rows`, and `targets=6 dumped=6 missing=0 failed=0`.
- Context logs report `targets=2 found=2 missing=0`, `rows=2 missing=0`, `Wrote 4 rows`, `Wrote 180 function-body instruction rows`, and `targets=2 dumped=2 missing=0 failed=0`.
- Final backup after the read-only evidence wave: `[maintainer-local-ghidra-backup-root]\BEA_20260605-100620_post_wave1133_feature_pickup_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed Ghidra review backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-093432_post_wave1132_component_ai_current_risk_review_verified`.
- Codex read-only consult recommended an eight-row feature/pickup cluster; root kept `0x0040dfb0 CGeneralVolume__SpawnPickupAndDispatch` and `0x004ef100 CUnit__VFunc64_SpawnConfiguredPickupThreeTimes` as context because they were already accounted by earlier waves, then counted the six still-unaccounted primary rows.

What this proves:

- The six target rows still exist in the saved Ghidra project with expected names and signatures.
- The saved comments, xrefs, instruction windows, and decompile rows remain coherent with the prior feature, destroyable-segment, GeneralVolume, and Unit pickup-spawn evidence.
- The wave narrows current-risk accounting for this feature/pickup bridge without changing the saved Ghidra project.
- The Ghidra project was backed up and verified after the read-only evidence wave.

What remains separate:

- Runtime pickup/drop behavior.
- Runtime feature lifecycle behavior.
- Runtime destroyable-segment pickup behavior.
- Runtime GeneralVolume or Unit configured-pickup behavior.
- Exact source-body identity.
- Concrete feature/pickup/unit/profile/init/layout schemas.
- BEA patching behavior.
- Gameplay outcomes.
- Visual QA.
- Rebuild parity.
