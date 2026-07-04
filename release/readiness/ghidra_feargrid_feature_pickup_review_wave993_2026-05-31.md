# Ghidra FearGrid Feature Pickup Review Wave993 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-31
Scope: `feargrid-feature-pickup-review-wave993`

Wave993 re-audited the FearGrid/Feature/pickup-spawn join after the Wave900-Wave992 recheck gate. The pass saved one Ghidra comment/tag normalization at `0x0044c440 CFearGrid__RebuildOccupancyAndScheduleTick`, replacing stale Wave366 callee-owner wording with the current Wave826-proven `FearGridTrackedObject__LookupFearWeightByArchetype` context. It made no rename, signature change, function-boundary change, executable-byte change, BEA launch, runtime proof, or game-file mutation.

Reviewed targets and context:

| Address | Evidence |
| --- | --- |
| `0x0040dda0 CUnitAI__RefreshGridCooldownFromOccupiedCells` | Context from Wave990; calls `CFearGrid__GetOccupancyAtWorldVector` through `DAT_008a9d7c` and `DAT_008a9d80` at `0x0040ddf3` and `0x0040de22`. |
| `0x0044c3d0 CFearGrid__ctor_base` | Installs the `CFearGrid` vtable, stores `grid_id` at `this+0x8008`, and calls `CFearGrid__RebuildOccupancyAndScheduleTick`. |
| `0x0044c440 CFearGrid__RebuildOccupancyAndScheduleTick` | Saved Wave993 normalization: clears occupancy/clearance planes, filters tracked objects by `grid_id`, calls `FearGridTrackedObject__LookupFearWeightByArchetype`, clears nearby clearance cells, and schedules event `1000`. |
| `0x0044c720 CFearGrid__GetOccupancyAtWorldVector` | Occupancy sampler called by `CUnitAI__RefreshGridCooldownFromOccupiedCells` and `CSquadNormal__Process`; reads the occupancy plane at `this+0x08`. |
| `0x0044c780 CFearGrid__ReadClearanceAtWorldVectorIfAboveTerrainDelta` | Clearance sampler called by both `OID__CanFireAtTarget_BallisticArc*` helpers; reads the clearance plane at `this+0x4008` after static-shadow height gating. |
| `0x0044c810 CFearGrid__FindNearestFreeCellSpiral` | Free-cell search called twice by `CSquadNormal__Process`; updates an in/out world-vector when a free occupancy cell is found. |
| `0x0044ca30 CFeature__Init` | Feature init creates the owned resource object, calls `CActor__Init`, adds the feature to occupancy context, updates shadow context, and optionally plays a random sample. |
| `0x0044cbe0 CFeature__ShutdownAndRemoveFromWorld` | Feature shutdown kills samples, removes occupancy, updates visibility, and forwards base cleanup. |
| `0x0044cee0 CFeature__MaybeSpawnRandomPickupFromData` | Feature-adjacent randomized pickup helper gates on feature data at `+0xe4`, calls `CWorldPhysicsManager__CreatePickup`, resolves `DAT_008553f8` type context, and dispatches pickup init. |
| `0x0044e300 PickupSpawn__MaybeSpawnAttachedPickupFromFrame_0044e300` | Owner-neutral attached pickup helper gates on `+0x164`, samples attached frame transform context, creates a pickup, resolves `DAT_008553f8`, and dispatches pickup init. |
| `0x004e7110 CSquadNormal__Process` | Context caller for FearGrid occupancy/free-cell helpers during squad path/formation processing. |

Read-back evidence:

- `ApplyFearGridFeaturePickupWave993.java dry`: `updated=0 skipped=1 comment_only_updated=1 tags_added=5 missing=0 bad=0`
- `ApplyFearGridFeaturePickupWave993.java apply`: `updated=1 skipped=0 comment_only_updated=1 tags_added=5 missing=0 bad=0`
- `ApplyFearGridFeaturePickupWave993.java final dry`: `updated=0 skipped=1 comment_only_updated=0 tags_added=0 missing=0 bad=0`
- Post exports: `11` metadata rows, `11` tag rows, `19` xref rows, `1893` body-instruction rows, and `11` decompile rows.
- Queue after Wave993: `6222` total functions, `6222` commented, `0` commentless, `0` exact-undefined signatures, `0` `param_N`, static closure `6222/6222 = 100.00%`.
- Wave911 focused re-audit progress: `447/1408 = 31.75%`.
- Expanded static surface progress: `549/1478 = 37.14%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-061908_post_wave993_feargrid_feature_pickup_review_verified`, `19` files, `173869959` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The reviewed function rows exist in the saved Ghidra project with the expected names and signatures.
- `0x0044c440 CFearGrid__RebuildOccupancyAndScheduleTick` now has saved Wave993 comment/tag evidence naming `FearGridTrackedObject__LookupFearWeightByArchetype` as the tracked-object weight helper.
- The old stale `CFearGrid__LookupFearWeightByArchetype` callee-owner wording is no longer present in the saved target comment.
- Static xrefs preserve the FearGrid consumer join through CUnitAI, CSquadNormal, and OID ballistic helpers plus Feature/pickup-spawn context.

What remains unproven:

- Runtime AI/fear behavior.
- Runtime pickup behavior.
- Exact `CFearGrid`, `CFeature`, or pickup data layouts.
- Exact source-body identity.
- BEA patching behavior.
- Rebuild parity.
