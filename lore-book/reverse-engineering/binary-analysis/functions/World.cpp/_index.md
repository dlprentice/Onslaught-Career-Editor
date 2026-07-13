# world.cpp Functions

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x004081c0` → `CBattleEngine__Move` (was `CMonitor__Process`); `0x0050b9c0` signature/comment correction; `0x005362a0` comment correction. Older conflicting text below is superseded for these rows. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Wave1194 current-risk update: Wave1194 (`wave1194-unit-world-airunit-lifecycle-score17-current-risk-review`) accounts for `9 unit/world/airunit lifecycle score17 current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence and saved comment/tag normalization. The rows are `CUnit__VFunc08_InitAndAddToWorld`, `CUnit__VFunc18_SyncOldVectorAndClampHeight`, `CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk`, `CWorld__RemoveUnitFromOccupancyGrid_Thunk`, `CGroundAttackAircraft__Destructor_VFunc01`, `CDropship__Destructor_VFunc01`, `CPlane__Destructor_VFunc01`, `CDiveBomber__Destructor_VFunc01`, and `CFenrir__Destructor_VFunc01`. Ghidra dry/apply/final-dry reported `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=9 tags_added=132 missing=0 bad=0`, then `updated=9 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=9 tags_added=132 missing=0 bad=0`, then final dry updated=0 skipped=9. No rename, no signature change, no function-boundary change, and no executable-byte change occurred. Codex read-only consult used; no Cursor/Composer. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt; expanded static surface remains `1560/1560 = 100.00%`; Wave1108 current focused accounting is `865/1179 = 73.37%`; current risk candidates: 6166; current focused candidates: 1154; live regenerated current focused candidates: 1154; remaining active focused work: 314; current-risk denominator; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `26 xref rows`, `177 instruction rows`, and `9 decompile rows`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-193734_post_wave1194_unit_world_airunit_lifecycle_score17_current_risk_review_verified`. Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference; exact CUnit/CWorld/aircraft/grid/set/list layouts, exact source virtual/destructor identity, runtime lifecycle/occupancy/height/aircraft teardown behavior, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof. Probe token anchor: Wave1194; wave1194-unit-world-airunit-lifecycle-score17-current-risk-review; 865/1179 = 73.37%; 9 unit/world/airunit lifecycle score17 current-risk rows; current focused candidates: 1154; live regenerated current focused candidates: 1154; remaining active focused work: 314; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=9 skipped=0; comment_only_updated=9; tags_added=132; final dry updated=0 skipped=9; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consult used; no Cursor/Composer; CUnit__VFunc08_InitAndAddToWorld; CUnit__VFunc18_SyncOldVectorAndClampHeight; CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk; CWorld__RemoveUnitFromOccupancyGrid_Thunk; CGroundAttackAircraft__Destructor_VFunc01; CDropship__Destructor_VFunc01; CPlane__Destructor_VFunc01; CDiveBomber__Destructor_VFunc01; CFenrir__Destructor_VFunc01; 0 / 0 / 0; 6411/6411 = 100.00%; 26 xref rows; 177 instruction rows; 9 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260606-193734_post_wave1194_unit_world_airunit_lifecycle_score17_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.


> Source File: world.cpp | Binary: BEA.exe | Debug Path: `[maintainer-local-source-export-root]\world.cpp`

## Overview
> **Queue status (2026-05-26):** Ghidra export-contract closure **6246/6246** (Wave1073: every exported function commented with clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

World/level loading and management. Handles loading level data from .aya asset archives. CWorld is the main world/level manager class responsible for deserializing level data, spawning entities, and managing world state.

Wave905 static review (`mesh-motion-world-particle-static-review-wave905`) records a `static-coherent mesh/motion/world/particle core` after export-contract queue closure `6113/6113 = 100.00%` (static review slice only): `506` rows across `41` families, including `CMeshPart` `54`, `CMesh` `40`, `CWorld` `38`, `CWorldPhysicsManager` `32`, `CThing` `28`, `CParticleManager` `23`, and `CMeshCollisionVolume` `21`; anchors include `CThing__InitRenderThingFromInitMeshName`, `CMesh__LoadByNameWithStatus`, `CMeshPart__PopulatePoseCacheRecursive`, `CWorld__InitOccupancyBitplanes`, `CWorldPhysicsManager__CreateThingByType`, `CParticleManager__Update`, `CParticleSet__LoadFromArchive`, and `CParticleDescriptor__Load`; mesh bridge counts include `213/213` loose meshes, `139/139` embedded meshes, and `352/352` model material/texture-binding rows. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-103409_post_wave905_mesh_motion_world_particle_static_review_verified`.

Wave1073 static re-audit (cworld-load-tail-review-wave1073) re-read the saved Wave555/Wave556 CWorld load/tail rows with no mutation. The reviewed CWorld anchors include `0x0050a870 CWorld__ClearSetArrays`, `0x0050ac70 CWorld__LoadScriptEvents`, `0x0050b520 CWorld__LoadWorldFile`, `0x0050d6a0 CWorld__PushWorldTextSlot`, and `0x0050dcb0 CWorld__SpawnInitialThings`; context ties them back through `0x0050b9c0 CWorld__LoadWorld`, `0x0046cdf0 CGame__LoadLevel`, occupancy helpers, world-text/CText helpers, WorldMeshList, and WorldPhysicsManager factory calls. Primary/context/raw exports verified `23/23/62/2095/23`, `18/18/362/6272/18`, and `253` rows respectively. Queue closure remains `6246/6246 = 100.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface advances to `1357/1560 = 86.99%`; top-500 remains `500/500 = 100.00%`. Verified read-only backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-044834_post_wave1073_cworld_load_tail_review_verified`. Raw no-function neighborhoods `0x00537c40` and `0x004dfa47` remain separate boundary-recovery candidates. Runtime world-load/script-event/world-text/spawn/occupancy behavior, exact raw-boundary identities, exact layouts, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain unproven. Probe token anchor: Wave1073; cworld-load-tail-review-wave1073; 0x0050a870 CWorld__ClearSetArrays; 0x0050ac70 CWorld__LoadScriptEvents; 0x0050b520 CWorld__LoadWorldFile; 0x0050d6a0 CWorld__PushWorldTextSlot; 0x0050d9e0 CWorldMeshList__Add; 0x0050dcb0 CWorld__SpawnInitialThings; 0x0050df80 CWorldPhysicsManager__CreateThingByType; 0x00537c40; 0x004dfa47; 812/1408 = 57.67%; 1357/1560 = 86.99%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260602-044834_post_wave1073_cworld_load_tail_review_verified; read-only review.

Wave1052 static re-audit (`cworld-line-trace-review-wave1052`) re-read `0x0050b030 CWorld__FindFirstThingToHitLine` with no mutation. Fresh exports verified `1` primary metadata row, `1` tag row, `12` xref rows, `321` function-body instruction rows, and `1` decompile row; context exports verified `13` metadata rows, `13` tag rows, `105` xref rows, `4547` instruction rows, and `13` decompile rows. The saved Wave843 line-trace row remains coherent with `CHeightField__TraceLineAgainstHeightfield`, `CMapWho__GetFirstEntryWithinLine`, `CMapWho__GetNextEntryWithinLine`, `CThing__GetPersistentCollisionSeekingThing`, `CBattleEngine__CalcUnitOverCrossHair`, `CBattleEngine__HandleAutoAim`, `CUnit__ApplyDamage`, `CDXEngine__Render`, and source callsites in `references/Onslaught/BattleEngine.cpp`, `references/Onslaught/DXEngine.cpp`, and `references/Onslaught/PCEngine.cpp`. Wave911 focused re-audit progress advances to `745/1408 = 52.91%`; expanded static surface progress advances to `1033/1509 = 68.46%`; top-500 coverage remains `500/500 = 100.00%`; export-contract function-quality closure remains `6246/6246 = 100.00%`. Verified read-only backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-154511_post_wave1052_cworld_line_trace_review_verified`. This remains static Ghidra evidence only; concrete `CLine` / `CWorldLineColReport` layouts, runtime collision/targeting/line-of-sight behavior, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain unproven. Probe token anchor: Wave1052; cworld-line-trace-review-wave1052; 0x0050b030 CWorld__FindFirstThingToHitLine; CHeightField__TraceLineAgainstHeightfield; CMapWho__GetFirstEntryWithinLine; CMapWho__GetNextEntryWithinLine; CThing__GetPersistentCollisionSeekingThing; CBattleEngine__CalcUnitOverCrossHair; CBattleEngine__HandleAutoAim; CUnit__ApplyDamage; CDXEngine__Render; references/Onslaught/BattleEngine.cpp; references/Onslaught/DXEngine.cpp; references/Onslaught/PCEngine.cpp; 745/1408 = 52.91%; 1033/1509 = 68.46%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-154511_post_wave1052_cworld_line_trace_review_verified; no mutation.

Wave935 static re-audit (`world-footprint-heightfield-review-wave935`) re-reviewed `0x004bd5c0 CWorld__RasterizeFootprintIntoOccupancyBitplanes` and the terrain-height sampler join at `0x0047ea20 CHeightField__GetHeightSamplePacked16`; no mutation was needed. Fresh exports verified the footprint rasterizer's calls into `0x0047ec60 CMonitor__SampleHeightfieldNormalAtXY`, `0x004bdf70 CWorld__SetOrClearOccupancyBit`, and `0x004bd440 CWorld__ClearCrossNeighborsInBitplane`, and preserved the load/rebuild context through `0x00490e30 CHeightField__BuildCellMinMaxHeightTable` and `0x004bcd60 CWorld__RebuildOccupancyGridFromDynamicSet`. Wave911 focused re-audit progress after Wave935 is `148/1408 = 10.51%`; export-contract function-quality closure remains `6113/6113 = 100.00%`. Verified read-only backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-011246_post_wave935_world_footprint_heightfield_review_verified`. This remains static Ghidra evidence only; runtime terrain sampling, runtime occupancy/pathing/static-shadow behavior, exact layouts, and rebuild parity remain unproven.

Probe token anchor: Wave935; `world-footprint-heightfield-review-wave935`; `0x0047ea20 CHeightField__GetHeightSamplePacked16`; `0x004bd5c0 CWorld__RasterizeFootprintIntoOccupancyBitplanes`; `0x0047ec60 CMonitor__SampleHeightfieldNormalAtXY`; `0x004bdf70 CWorld__SetOrClearOccupancyBit`; `0x004bd440 CWorld__ClearCrossNeighborsInBitplane`; `0x00490e30 CHeightField__BuildCellMinMaxHeightTable`; `0x004bcd60 CWorld__RebuildOccupancyGridFromDynamicSet`; `148/1408 = 10.51%`; `6113/6113 = 100.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260528-011246_post_wave935_world_footprint_heightfield_review_verified`; no mutation.

## Functions

| Address | Name | Purpose |
|---------|------|---------|
| 0x004bc260 | CWorld__InitOccupancyBitplanes | Initialize one packed occupancy bitplane and slope threshold |
| 0x004bc2d0 | CWorld__ClearDynamicOccupancySet | Clear dynamic world-occupancy set `DAT_00809588` |
| 0x004bc3e0 | CWorld__RemoveUnitFromOccupancyGrid | Remove unit from tracked occupancy set and rerasterize its footprint |
| 0x004bc480 | CWorld__AddUnitToOccupancyGridAndRebuildShadows | Add unit to tracked occupancy set, rerasterize footprint, rebuild static shadows |
| 0x004bc8d0 | CWorld__ClearOccupancyBitsUsingHeightBands | Clear unsafe occupancy-bitplane cells from height/normal evidence |
| 0x004bcbf0 | CWorld__ApplyStaticMaskToOccupancyBitplanes | Apply static occupancy mask to three occupancy bitplanes |
| 0x004bcd60 | CWorld__RebuildOccupancyGridFromDynamicSet | Rebuild occupancy mask/bitplanes from dynamic object set |
| 0x004bd440 | CWorld__ClearCrossNeighborsInBitplane | Clear center/cross-neighbor cells in one half-resolution occupancy bitplane |
| 0x004bd5c0 | CWorld__RasterizeFootprintIntoOccupancyBitplanes | Rasterize clamped world-footprint bounds into three occupancy bitplanes |
| 0x004bdf70 | CWorld__SetOrClearOccupancyBit | Set or clear one packed half-resolution occupancy bit |
| 0x004bdff0 | CWorld__SkipLegacyOccupancyChunk | Skip legacy occupancy bitplane chunk payloads during world load |
| 0x004be050 | CWorld__LoadOccupancyBitplaneChunk | Load versioned occupancy bitplane chunks from a memory buffer |
| 0x004be170 | CWorld__ReadOccupancyChunkHeader | Read trailing occupancy chunk header fields from a memory buffer |
| 0x0050a870 | CWorld__ClearSetArrays | Clear nineteen CWorld `CSPtrSet` slots |
| 0x0050a9c0 | CWorld__InitSetArraysAndState | Initialize nineteen CWorld `CSPtrSet` slots and reset load/resource state |
| 0x0050abb0 | CWorld__ShutdownAndClear_Thunk | Thunk/wrapper to core world teardown routine (`CWorld__ShutdownAndClear`) |
| 0x0050abc0 | CWorld__CloneScriptObjectCodeByName | Find script object code by name in world registry and clone it |
| 0x0050ac70 | CWorld__LoadScriptEvents | Load script events from world file buffer |
| 0x0050ada0 | CWorld__ShutdownAndClear | Core world teardown and state-clear routine |
| 0x0050af70 | CWorld__FindThingByName | Find first world thing by name in world object set |
| 0x0050b010 | CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk | Thin wrapper into occupancy-grid add / shadow rebuild helper |
| 0x0050b020 | CWorld__RemoveUnitFromOccupancyGrid_Thunk | Thin wrapper into occupancy-grid removal helper |
| 0x0050b030 | CWorld__FindFirstThingToHitLine | Find first static line-trace hit across heightfield/MapWho/thing candidates |
| 0x0050b520 | CWorld__LoadWorldFile | Open and load a world file (.wrd) |
| 0x0050b780 | CWorld__DeserializeWorld | Deserialize world data (base/real world positions) |
| 0x0050b9c0 | [CWorld__LoadWorld](./CWorld__LoadWorld.md) | Main world-load worker; fresh `RET 0xc` review proves `mem_buffer`, `is_base_world`, and `initialize_world_state` stack arguments after `ECX`. The live one-argument signature is stale. |
| 0x0050d4c0 | CWorld__LoadWorldHeader | Load world header and configuration |
| 0x0050d580 | CWorld__InitLODLists | Initialize LOD (Level of Detail) lists |
| 0x0050d680 | CWorld__ReleaseSubObject_AndMaybeFree | Cleanup helper with optional free-on-flag behavior |
| 0x0050d6a0 | CWorld__PushWorldTextSlot | Queue/push a world text entry into first free display slot |
| 0x0050d720 | CWorld__UpdateWorldTextSlotTiming | Update timing/aux state for active world text slot entry |
| 0x0050d7a0 | CWorld__ClearWorldTextSlot | Clear/deactivate world text slot entry by text id |
| 0x0050d7d0 | CWorld__IsMultiplayerMode | Predicate for multiplayer world mode/state values |
| 0x0050d7f0 | CWorld__ClearLinkedObjectPairSet | Clear linked object-pair set and release pair objects |
| 0x0050dcb0 | CWorld__SpawnInitialThings | Spawn initial world things/entities |

## Wave844 CWorld LoadWorld (2026-05-25)

Historical Wave844 CWorld LoadWorld (`cworld-load-world-wave844`, `wave844-readback-verified`) saved comment/tag evidence for `0x0050b9c0 CWorld__LoadWorld` and preserved the then-existing one-argument signature. The 2026-07-13 critical ABI review supersedes that signature with three stack arguments; Wave844 remains valid only as mutation/read-back provenance. The pass made no function-boundary or executable-byte change. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-050626_post_wave844_cworld_load_world_verified`.

Static read-back anchors:

| Address | Evidence |
| --- | --- |
| `0x0050b720` | Sole caller xref from `CWorld__LoadWorldFile` into `CWorld__LoadWorld`. |
| `0x0050b9da` / `0x0050d4af` | Prologue calls `CRT__AllocaProbe` for a `0x38cc-byte stack frame`; tail returns with `RET 0xc`. |
| `0x0050ba7a` / `0x0050baed` | Calls `CWorld__InitLODLists` and `CWorld__LoadWorldHeader`. |
| `0x0050bbde` / `0x0050bbf5` | Calls `CWorld__LoadScriptEvents` and recursive/base `CWorld__LoadWorldFile`. |
| `0x0050bd8a`, `0x0050ca98`, `0x0050bf56`, `0x0050c146` | Creates squads, things, effects, and triggers through `CWorldPhysicsManager` helpers. |
| `0x0050cad1` | Adds mesh names through `CWorldMeshList__Add`. |
| `0x0050cf23` / `0x0050cf38` | Chooses `CInfluenceMapManager__SkipLoad` or `CInfluenceMapManager__Load`. |
| `0x0050d187` | Calls `CWaypointManager__LoadWaypoints`. |
| `0x0050d331`, `0x0050d363`, `0x0050d386` | Version-gated occupancy chunk skip/load/header paths. |
| `0x0050d431`, `0x0050d456`, `0x0050d473`, `0x0050d47a` | Non-base-world tail calls `CWorld__SpawnInitialThings`, old-version occupancy clearing, and either static-mask apply or dynamic-set rebuild. |

Post-Wave844 queue telemetry is `6098` total, `5668` commented, `430` commentless, `0` exact-undefined signatures, `0` `param_N`, and strict proxy `5668/6098 = 92.95%`; next raw commentless row is `0x0050f680 CSpawnerThng__IsSpawnTypeAllowed`. This is static saved-Ghidra evidence only. Exact world-buffer schema, concrete stack-local structure layouts, exact source-body identity, runtime load behavior, BEA patching, and rebuild parity remain deferred.

## Wave843 CWorld FindFirstThingToHitLine (2026-05-25)

Wave843 CWorld FindFirstThingToHitLine (`cworld-find-first-thing-to-hit-line-wave843`, `wave843-readback-verified`) renamed `0x0050b030 OID__TraceLineAndSelectBestTargetHit` to `0x0050b030 CWorld__FindFirstThingToHitLine` and saved `int __thiscall CWorld__FindFirstThingToHitLine(void * this, undefined4 line_00, undefined4 line_04, undefined4 line_08, undefined4 line_0c, undefined4 line_10, undefined4 line_14, undefined4 line_18, undefined4 line_1c, undefined4 line_20, undefined4 line_24, undefined4 line_28, undefined4 line_2c, undefined4 line_30, void * ignored_owner, void * hit_result, int stop_on_first_valid_hit, int child_trace_mode, int collision_mode, uint reject_flags, int heightfield_trace_flags, uint required_thing_flags)`. Source callsites use `WORLD.FindFirstThingToHitLine(...)`; retail callsites load `ECX` with `DAT_00855090`, matching the CWorld singleton receiver. The body ends in `RET 0x54`, matching a `0x34-byte by-value CLine-style stack copy` plus eight explicit stack fields after `this`.

Static evidence ties the body to `CHeightField__TraceLineAgainstHeightfield`, `CMapWho__GetFirstEntryWithinLine`, `CMapWho__GetNextEntryWithinLine`, `CMapWhoEntry__GetOwner`, `CThing__GetPersistentCollisionSeekingThing`, and early return when `stop_on_first_valid_hit` is nonzero. Post xrefs include `CDXEngine__Render`, `CBattleEngine__HandleAutoAim`, `CBattleEngine__CalcUnitOverCrossHair`, `CMCMech__GetFootHeight`, `CMonitor__Process`, `CCollisionSeekingRound__CreateEffect`, `OID__CanFireAtTarget_BallisticArcA/B`, and `CUnit__ApplyDamage`.

Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-043624_post_wave843_cworld_find_first_thing_to_hit_line_verified`; queue after Wave843 is `5667/6098 = 92.93%`, with next raw commentless row `0x0050b9c0 CWorld__LoadWorld`. This is static saved-Ghidra evidence only. Exact CLine layout, exact CWorldLineColReport layout, enum names, runtime collision/targeting behavior, BEA patching, and rebuild parity remain deferred.

## Wave819 World Occupancy Bitplanes (2026-05-24)

Wave819 world occupancy bitplanes (`world-occupancy-bitplanes-wave819`, `wave819-readback-verified`) saved static Ghidra comments/tags/signatures for the adjacent occupancy/load helpers from `0x004bc2d0 CWorld__ClearDynamicOccupancySet` through `0x004be170 CWorld__ReadOccupancyChunkHeader`. It made no renames, no function-boundary changes, and no executable-byte changes. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-164330_post_wave819_world_occupancy_bitplanes_verified`. Post-Wave819 queue telemetry is `6098` total, `5612` commented, `486` commentless, `0` exact-undefined signatures, `0` `param_N`, and strict proxy `5612/6098 = 92.03%`; next raw commentless row is `0x004bc2e0 CExplosionInitThing__ClearCostGridBoundsAndBuildPath`.

| Address | Saved state | Static read-back evidence |
| --- | --- | --- |
| `0x004bc2d0 CWorld__ClearDynamicOccupancySet` | `void __cdecl CWorld__ClearDynamicOccupancySet(void)` | Tail-jumps into `0x004e5c60 CSPtrSet__Clear` for dynamic set `DAT_00809588`; direct xref `0x0050d683 CWorld__ReleaseSubObject_AndMaybeFree`. |
| `0x004bc8d0 CWorld__ClearOccupancyBitsUsingHeightBands` | `void __cdecl CWorld__ClearOccupancyBitsUsingHeightBands(void)` | `CWorld__LoadWorld` callsite `0x0050d456`; samples `CHeightField__GetHeightSamplePacked16` and `CMonitor__SampleHeightfieldNormalAtXY`, compares thresholds stored after `DAT_00855290`, `DAT_00855294`, and `DAT_00855298`, and clears center/cross-neighbor occupancy bits. |
| `0x004bcbf0 CWorld__ApplyStaticMaskToOccupancyBitplanes` | `void __cdecl CWorld__ApplyStaticMaskToOccupancyBitplanes(void)` | `CWorld__LoadWorld` callsite `0x0050d473`; scans static mask `DAT_00807580`, clears corresponding packed bits in the three occupancy bitplanes, and sets `DAT_00809598 = 1`. |
| `0x004bcd60 CWorld__RebuildOccupancyGridFromDynamicSet` | `void __cdecl CWorld__RebuildOccupancyGridFromDynamicSet(void)` | `CWorld__LoadWorld` callsite `0x0050d47a`; resets `DAT_00807580`, iterates dynamic objects from `DAT_00809588` through `CSPtrSet__First`/`CSPtrSet__Next`, and clears occupancy mask/bitplane cells through `CWorld__SetOrClearOccupancyBit` and `CWorld__ClearCrossNeighborsInBitplane`. |
| `0x004bdff0 CWorld__SkipLegacyOccupancyChunk` | `void __thiscall CWorld__SkipLegacyOccupancyChunk(void * this, void * mem_buffer)` | `CWorld__LoadWorld` callsites `0x0050d331`, `0x0050d33d`, and `0x0050d349` load ECX from `DAT_00855290`, `DAT_00855294`, or `DAT_00855298` and push the `CDXMemBuffer` pointer; body skips mode `1` (`0x8000`) or mode `2` (`0x2000`) byte payloads and exits with `RET 0x4`. |
| `0x004be170 CWorld__ReadOccupancyChunkHeader` | `void __cdecl CWorld__ReadOccupancyChunkHeader(void * mem_buffer)` | `CWorld__LoadWorld` callsite `0x0050d386` pushes the `CDXMemBuffer` pointer and cleans with `ADD ESP, 0x4`; body reads five 4-byte fields through `CDXMemBuffer__Read`. |

This is static saved-Ghidra evidence only. Exact global field names/layouts, exact legacy occupancy chunk schema, runtime world-load/pathing behavior, exact source-body identity, BEA patching, and rebuild parity remain deferred.

## Wave556 CWorld Tail / WorldMeshList Corrections (2026-05-18)

Wave556 saved static Ghidra signature/comment/tag corrections for the adjacent CWorld tail, WorldMeshList, and world-thing factory bridge cluster:

| Address | Current saved Ghidra state | Evidence summary |
| --- | --- | --- |
| `0x0050d680` | `void * __thiscall CWorld__ReleaseSubObject_AndMaybeFree(void * this, uint flags)` | `CWorld__ShutdownAndClear` calls this for the three world-owned LOD/occupancy subobjects at `world +0x200/+0x204/+0x208`, always pushing `flags=1`; the older second explicit parameter was register carryover. |
| `0x0050d6a0` | `void __thiscall CWorld__PushWorldTextSlot(void * this, int text_id, int slot_state)` | Raw script wrapper loads ECX with `DAT_00855090` and passes `text_id` plus `slot_state`; body fills the first empty four-slot world-text entry using `CText__GetStringById`. |
| `0x0050d720` | `void __thiscall CWorld__UpdateWorldTextSlotTiming(void * this, int text_id, float primary_time, float secondary_time)` | Raw script wrapper passes one text id plus two float timing values; body matches stored ids at `this +0x21c`, updates timing at `+0x23c/+0x24c`, and treats state `3` as an absolute expiry against `DAT_00672fd0`. |
| `0x0050d760` | `double __thiscall CWorld__GetWorldTextSlotTimerValue(void * this, int slot_index)` | Corrected stale `CExplosionInitThing__GetSlotTimerValueByMode` owner: HUD/script callers and field offsets show CWorld world-text slot state/timer access. |
| `0x0050d7a0` | `void __thiscall CWorld__ClearWorldTextSlot(void * this, int text_id)` | Raw script wrapper passes one `text_id`; body scans four slots and clears state at `this +0x20c` for matching ids at `this +0x21c`. |
| `0x0050d7d0` | `int __fastcall CWorld__IsMultiplayerMode(void * world)` | `CGame__LoadLevel` loads ECX with `DAT_00855090`; body returns nonzero when `world +0x27c` is `1` or `2`. |

MissionScript HUD / Display Command-Effect static proof: `../missionscript-hud-display-command-effect-static-proof.md` and `../missionscript-hud-display-command-effect.v1.json` use `CWorld__PushWorldTextSlot`, `CWorld__UpdateWorldTextSlotTiming`, `CWorld__ClearWorldTextSlot`, `CWorld__GetWorldTextSlotTimerValue`, and `DAT_00855090` as world-text display-context anchors for `InitVariable`, `SetVariable`, and `ShutdownVariable`. This is static context only; it does not prove the five raw descriptor entries dispatch to these helpers or prove runtime HUD behavior, visible HUD flashing, runtime variable display, exact layouts, patching, Godot, rebuild parity, or no-noticeable-difference parity.
| `0x0050d7f0` | `void __fastcall CWorld__ClearLinkedObjectPairSet(void * pair_set)` | `CWorld__ShutdownAndClear` passes embedded pair set `world +0x120`; body dispatches deleting destructors for both pointer fields, frees each pair node, and clears the backing `CSPtrSet`. |
| `0x0050d9a0` | `void __cdecl CWorldMeshList__Clear(void)` | Global cleanup drains `DAT_00855358`, removes each node, frees the copied mesh-name string, and frees the 8-byte node. |
| `0x0050d9e0` | `void __cdecl CWorldMeshList__Add(char * mesh_name)` | `CWorld__LoadWorld`, `CSpawnerThng__Init`, `CScriptObjectCode__CollectSpawnThings`, and recursive self-calls pass one mesh-name pointer; body deduplicates `DAT_00855358`, matches definitions at `DAT_008553fc +0xb0`, and recurses through child names via `DAT_008553f4`. |
| `0x0050dc20` | `void __cdecl CWorldMeshList__MarkUsed(char * mesh_name)` | `CUnit__Init` passes one mesh-name pointer; body scans `DAT_00855358` and sets the node used flag at `+0x04` on match. |
| `0x0050dcb0` | `void __cdecl CWorld__SpawnInitialThings(void)` | `CWorld__LoadWorld` calls this no-argument pass after mesh-list population; body spawns unused mesh entries by resolving thing-definition indices, calling `CWorldPhysicsManager__CreateThingByType`, creating init thing type `8`, and using default `256/256/0` position fields. |
| `0x0050df80` | `void * __cdecl CWorldPhysicsManager__CreateThingByType(int thing_type_index)` | Callers pass one definition index; body walks `DAT_008553fc`, switches on definition type enum `+0xe0`, allocates the matching runtime object, installs class tables, and returns object/null. |

This is static saved-Ghidra evidence only. Exact CWorld slot structure names, text-slot state enum names, WorldMeshList node/list ownership invariants, thing-definition layouts, runtime HUD/spawn/world-load behavior, BEA launch, patching, and rebuild parity remain unproven.

## Wave555 CWorld Load/Core Corrections (2026-05-18)

Wave555 saved static Ghidra owner/signature/comment/tag corrections for the adjacent CWorld load, registry, and cleanup cluster:

| Address | Current saved Ghidra state | Evidence summary |
| --- | --- | --- |
| `0x0050a870` | `void __fastcall CWorld__ClearSetArrays(void * world)` | Raw singleton callsite loads ECX with `DAT_00855090`; body clears nineteen `CSPtrSet` slots at `world +0x00..+0x120`. |
| `0x0050a9c0` | `void * __fastcall CWorld__InitSetArraysAndState(void * world)` | Raw singleton callsite loads ECX with `DAT_00855090`; body initializes nineteen `CSPtrSet` slots, zeros state arrays/fields, sets resource/load sentinels at `+0x26c..+0x278` to `-1`, and returns `world`. |
| `0x0050abb0` | `void __fastcall CWorld__ShutdownAndClear_Thunk(void * world)` | `CGame__ShutdownRestartLoop` calls this with the CWorld singleton in ECX; entry is a pure jump into `CWorld__ShutdownAndClear`. |
| `0x0050abc0` | `void * __thiscall CWorld__CloneScriptObjectCodeByName(void * this, char * script_name)` | `RET 0x4` and `CComplexThing__SetScript` prove one explicit `script_name` argument; scans the script-event set at `this +0x120`, clones the matching `CScriptObjectCode`, and fatal-errors if absent. |
| `0x0050ac70` | `void __thiscall CWorld__LoadScriptEvents(void * this, void * mem_buffer)` | `CWorld__LoadWorld` pushes one buffer argument and `RET 0x4` confirms it; body reads event count, allocates name/code pairs, and appends them at `this +0x120`. |
| `0x0050ada0` | `void __fastcall CWorld__ShutdownAndClear(void * world)` | ECX-only cleanup releases global/subobject pointers, destroys object sets and linked pairs, clears readers/pending waypoint objects, shuts down BattleEngineConfigurations, clears CWorldMeshList, frees resource fields, and resets state. |
| `0x0050af70` | `void * __thiscall CWorld__FindThingByName(void * this, char * thing_name)` | Callers pass one name pointer after loading the CWorld singleton into ECX; `RET 0x4` confirms one explicit argument. The body iterates the thing set at `this +0xa0`, compares each vfunc-derived name, and returns the matching thing or null. |
| `0x0050b520` | `int __thiscall CWorld__LoadWorldFile(void * this, int world_id, int is_base_world)` | `CGame__LoadLevel` and recursive base-world callsites pass two stack arguments; the base-world path pushes `is_base_world=1`. Return is treated as nonzero success. |
| `0x0050b780` | `void __thiscall CWorld__DeserializeWorld(void * this, void * chunk_reader)` | `CResourceAccumulator__ReadResourceFile` passes one reader/buffer argument and `RET 0x4` confirms it; body reads base/current world ids, stores handles at `+0x26c..+0x278`, allocates managers/objects, and deserializes world data when present. |
| `0x0050d4c0` | `void __thiscall CWorld__LoadWorldHeader(void * this, void * mem_buffer, int is_base_world)` | `CWorld__LoadWorld` pushes buffer and base flag; `RET 0x8` confirms two explicit args. Non-base path loads `BattleEngineConfigurations` and stores a header field at `this +0x27c`. |
| `0x0050d580` | `void __fastcall CWorld__InitLODLists(void * world)` | `CWorld__LoadWorld` calls this ECX-only helper; body allocates three `0x2004`-byte bitplane/LOD structures, initializes thresholds `35/45/60`, and stores them at `world +0x200/+0x204/+0x208`. |

This is static saved-Ghidra evidence only. Exact CWorld member names/layouts, script-event and thing-set concrete types, resource/chunk reader schemas, runtime load/shutdown behavior, BEA launch, patching, and rebuild parity remain unproven.

## Wave457 Occupancy Bitplane Corrections (2026-05-16)

Wave457 saved signature/comment/tag corrections for the CWorld occupancy-grid helper family:

| Address | Current saved Ghidra state | Evidence summary |
| --- | --- | --- |
| `0x004bc260` | `CWorld__InitOccupancyBitplanes(void * this, float max_slope_degrees)` | `RET 0x4` proves one stack threshold argument. `CWorld__InitLODLists` calls this three times with 35, 45, and 60 degree thresholds. The body clears active state, fills `DAT_00809dc0`, seeds bounds globals, and initializes packed rows to `0xff`. |
| `0x004bc3e0` | `CWorld__RemoveUnitFromOccupancyGrid(void * unit)` | Removes from `DAT_00809588`, computes bounds from unit position/radius, and rerasterizes with `skip_shadow_rebuild=1` when occupancy is active. |
| `0x004bc480` | `CWorld__AddUnitToOccupancyGridAndRebuildShadows(void * unit)` | Adds to `DAT_00809588`, rerasterizes with `skip_shadow_rebuild=1`, then calls `CEngine__BuildStaticShadowVolumesAroundUnit`. |
| `0x004bd440` | `CWorld__ClearCrossNeighborsInBitplane(void * this, int world_x, int world_y)` | `RET 0x8` removes the stale phantom parameter; clears half-resolution packed center/cross-neighbor bits. |
| `0x004bd5c0` | `CWorld__RasterizeFootprintIntoOccupancyBitplanes(int min_world_x, int min_world_y, int max_world_x, int max_world_y, int skip_shadow_rebuild)` | Clamps bounds to `0..511`, touches `DAT_00855290/294/298`, samples height/normal, clears unsafe slope/height cells, and optionally rebuilds tracked-unit static shadows. |
| `0x004bdf70` | `CWorld__SetOrClearOccupancyBit(void * this, int world_x, int world_y, int set_flag)` | `RET 0xc` removes the stale fourth stack argument; sets or clears one packed half-resolution bit. |
| `0x004be050` | `CWorld__LoadOccupancyBitplaneChunk(void * this, void * mem_buffer)` | `RET 0x4` confirms one stack buffer argument after `this`; version 1 expands source bits over a `0x200 x 0x200` grid and version 2 reads packed `0x100 x 0x20` rows. |

This is static saved-Ghidra evidence only. Runtime pathfinding, occupancy, static-shadow, world-load behavior, concrete layouts, exact source identities, and rebuild parity remain unproven.

## Level Loading Overview

Battle Engine Aquila stores levels in .aya archive files. The World system handles:

1. Parsing .aya archive headers
2. Extracting level geometry, textures, scripts
3. Setting up the game world for play
4. Managing world state during gameplay

## .AYA Archive Format

The AYA format is a proprietary archive containing:

- Level geometry/terrain
- Textures and materials
- MSL mission scripts
- Entity placement data
- Audio cues
- Lighting information

See `reverse-engineering/game-assets/` for detailed AYA format documentation.

## CWorld Class Structure

Based on decompilation analysis, the CWorld class has the following member offsets:

| Offset | Type | Member Name | Notes |
|--------|------|-------------|-------|
| 0x000 | CSPtrSet[19] | mWorldSets | Wave555 observed nineteen adjacent `CSPtrSet` slots initialized/cleared from `+0x00` through `+0x120`; exact per-slot names remain open |
| 0x0a0 | CSPtrSet* | mThingSet | `CWorld__FindThingByName` iterates this set |
| 0x0a8 | void* | mThingIterator | Iterator/current entry field used during `CWorld__FindThingByName` scan |
| 0x120 | CSPtrSet* | mScriptEvents | List of script event name/code pairs |
| 0x200 | void* | mLODList0 | LOD list for distance 35.0f |
| 0x204 | void* | mLODList1 | LOD list for distance 45.0f |
| 0x208 | void* | mLODList2 | LOD list for distance 60.0f |
| 0x20c | int[4] | mWorldTextSlotState | Four world-text slot state values; Wave556 static evidence only |
| 0x21c | int[4] | mWorldTextSlotTextId | Four stored text ids used by push/update/clear helpers |
| 0x22c | void*[4] | mWorldTextSlotString | Localized string pointers from `CText__GetStringById` |
| 0x23c | float[4] | mWorldTextPrimaryTime | Primary timer/absolute-expiry value depending on slot state |
| 0x24c | float[4] | mWorldTextSecondaryTime | Secondary timer value |
| 0x25c | float[4] | mWorldTextCreatedTime | Creation timestamp seeded from `DAT_00672fd0` |
| 0x26c | int | mCurrentWorldId | Current loaded world ID |
| 0x270 | int | mBaseWorldId | Base world ID (for linked worlds) |
| 0x274 | int | mRealWorldResource | Resource handle for real world |
| 0x278 | int | mBaseWorldResource | Resource handle for base world |
| 0x27c | int | mWorldMode | Header-loaded mode value; `CWorld__IsMultiplayerMode` treats values `1` and `2` as multiplayer |

## Function Details

### CWorld__LoadScriptEvents (0x0050ac70)

Loads script events from the world file buffer. Iterates through events, allocating:
- CStringDataType for event names
- CScriptObjectCode for event code
- Creates name/code pairs and adds them to the script events list

### CWorld__LoadWorldFile (0x0050b520)

Opens a world file and delegates to CWorld__LoadWorld.
- Constructs path: `data\\worlds\\%sworld_%03d.wrd`
- Handles caching of previously loaded worlds
- Uses CChunker for file reading
- Debug strings: "Loading world %d", "Loading base world %d"

### CWorld__DeserializeWorld (0x0050b780)

Deserializes world state from buffer:
- Debug string: "Deserializing world"
- Creates CRelaxedSquad instances
- Loads base world position (if exists)
- Loads real world position
- Uses global squad manager (DAT_0067a748)

### CWorld__LoadWorldHeader (0x0050d4c0)

Reads the world file header:
- Reads configuration data
- Calls BattleEngineConfigurations__Load or BattleEngineConfigurations__Skip
- Version-dependent field handling (version > 1, version > 2)

### CWorld__InitLODLists (0x0050d580)

Initializes three Level of Detail lists with different distance thresholds:
- LOD 0: 35.0f (0x420c0000)
- LOD 1: 45.0f (0x42340000)
- LOD 2: 60.0f (0x42700000)

Allocates 0x2004 bytes per LOD list.

### CWorld__SpawnInitialThings (0x0050dcb0)

Spawns initial world entities:
- Iterates through spawn list (DAT_00855358)
- Looks up thing-definition indices by mesh/name
- Creates things via CWorldPhysicsManager__CreateThingByType
- Initializes thing positions (256.0f, 256.0f, 0.0f default)

## World File Version History

The LoadWorld function checks version ranges:
- Version < 0x2b (43): Invalid
- Version > 0x32 (50): Invalid
- Valid range: 43-50

Version-specific handling:
- Version < 0x11 (17): Old format, many ReadBytes calls
- Version < 0x14 (20): Single string field
- Version < 0x1c (28): Two string fields
- Version < 0x22 (34): Three string fields
- Version >= 0x2e (46): Additional data fields
- Version >= 0x30 (48): Extra configuration field

## Global Variables

| Address | Type | Purpose |
|---------|------|---------|
| 0x0067a748 | CSquadManager* | Global squad manager |
| 0x0067a07c | void* | Unknown world object |
| 0x0067a078 | void* | Unknown world object |
| 0x00855358 | void* | Spawn list head |
| 0x00855360 | void* | Spawn list iterator |
| 0x008553fc | void** | Squad type list |

## Related Systems

- Script.cpp - MSL mission scripts loaded from .aya
- Career.cpp - Tracks level completion
- Game.cpp - Coordinates world loading
- WorldPhysicsManager.cpp - Creates world entities
- WorldMeshList.cpp - Manages world mesh rendering
- InfluenceMapManager - AI pathfinding data
- WaypointManager.cpp - Waypoint loading

---
*Migrated from ghidra-analysis.md (Dec 2025)*
*Updated Dec 2025: Added 6 new functions from world.cpp xref analysis*

## Wave1151 Current-Risk Tag Normalization

Wave1151 tag-only normalization also covers `0x004bd5c0 CWorld__RasterizeFootprintIntoOccupancyBitplanes` as a score21 current-risk row. It preserves the world occupancy/static-shadow rasterizer evidence and adds Wave1151/current-risk tags only. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-201419_post_wave1151_mixed_score21_current_risk_review_verified`. Runtime behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
