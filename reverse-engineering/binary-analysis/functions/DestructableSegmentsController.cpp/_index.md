# DestructableSegmentsController.cpp

> Destructible object segment management from BEA.exe

**Debug Path**: `C:\dev\ONSLAUGHT2\DestructableSegmentsController.cpp` (0x006287b4)

## Overview
> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

This source file implements the destruction system for segmented objects (buildings, structures). It manages hierarchical segments that can be individually damaged and destroyed, with parent-child relationships determining destruction propagation.

Wave1205 (`wave1205-destroyable-segment-current-risk-review`) re-read `5 destroyable-segment current-risk rows` with fresh Ghidra export evidence and no mutation. The reviewed rows are `CDestructableSegment__RegisterChild`, `CDestroyableCoreSegment__AreCoreChildrenDestroyed`, `CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex`, `CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex`, and `CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric`. Fresh exports verified `5` metadata rows, `5` tag rows, `9 xref rows`, `96 instruction rows`, and `5 decompile rows`; no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change occurred. Codex read-only consults used; no Cursor/Composer. Active current-risk accounting is `1076/1179 = 91.26%`; current focused candidates: 1141; live regenerated current focused candidates: 1141; remaining active focused work: 103; current risk candidates: 6166; legacy additive counter is deprecated (`1107/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; this is the Wave1108 current-risk denominator with focused threshold `15`, not Wave911 reconstruction. Verified backup: `G:\GhidraBackups\BEA_20260607-021737_post_wave1205_destroyable_segment_current_risk_review_verified`. Runtime destructable-segment behavior, runtime destroyable-segment behavior, runtime cascade behavior, exact concrete layouts, exact source-body identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof. Probe token anchor: Wave1205; wave1205-destroyable-segment-current-risk-review; 1076/1179 = 91.26%; 5 destroyable-segment current-risk rows; current focused candidates: 1141; live regenerated current focused candidates: 1141; remaining active focused work: 103; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; no rename; no signature change; no comment change; no tag change; no function-boundary change; no executable-byte change; Codex read-only consults used; legacy additive counter is deprecated; 1107/1179; 26 duplicate-address overcount; Wave1145 arithmetic overcount: 5; CDestructableSegment__RegisterChild; CDestroyableCoreSegment__AreCoreChildrenDestroyed; CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex; CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex; CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric; 0 / 0 / 0; 6411/6411 = 100.00%; 9 xref rows; 96 instruction rows; 5 decompile rows; G:\GhidraBackups\BEA_20260607-021737_post_wave1205_destroyable_segment_current_risk_review_verified; static-reaudit-current-risk-ledger.json; wave1108-current-risk-rank; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.

Wave1157 (`wave1157-destroyable-segment-vfunc-current-risk-review`) re-read `12 destroyable-segment vfunc current-risk rows` with fresh Ghidra export evidence and no mutation. The reviewed rows are the current-risk vtable damage, break, rubble, parent-gate, and stage helpers now consolidated in [`destroyable-segments-static-contract.md`](../../destroyable-segments-static-contract.md): `CDestroyableSegment__VFunc_03_ApplyDamage`, `CDestroyableSegment__VFunc_08_HandleSegmentBreak`, `CDestroyableSegment__VFunc_10_SpawnRubbleEffects`, `CDestroyableCoreSegment__VFunc_03_ApplyDamage`, `CDestroyableSwapSegment__VFunc_04_GetDamageStageIndex`, and `CDestroyableEndSegment__VFunc_11_RecomputeEndDamageScaleFields`. Fresh exports verified `12` metadata rows, `12` tag rows, `23 xref rows`, `694 instruction rows`, and `12` decompile rows. Wave1108 current focused accounting is now `465/1179 = 39.44%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 714; focused threshold `15`; not Wave911 reconstruction. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; this was a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, no runtime-file mutation, and Codex read-only consults used for candidate/accounting and system-map sanity while Codex root made the final judgment. Verified backup: `G:\GhidraBackups\BEA_20260605-235134_post_wave1157_destroyable_segment_vfunc_current_risk_review_verified`. Runtime destructable-segment behavior, exact concrete layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof. Probe token anchor: Wave1157; wave1157-destroyable-segment-vfunc-current-risk-review; 465/1179 = 39.44%; 12 destroyable-segment vfunc current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 714; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; 23 xref rows; 694 instruction rows; CDestroyableSegment__VFunc_03_ApplyDamage; CDestroyableSegment__VFunc_08_HandleSegmentBreak; CDestroyableSegment__VFunc_10_SpawnRubbleEffects; CDestroyableCoreSegment__VFunc_03_ApplyDamage; CDestroyableSwapSegment__VFunc_04_GetDamageStageIndex; CDestroyableEndSegment__VFunc_11_RecomputeEndDamageScaleFields; G:\GhidraBackups\BEA_20260605-235134_post_wave1157_destroyable_segment_vfunc_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Wave1133 (`wave1133-feature-pickup-current-risk-review`) re-read `0x00442710 CDestroyableSegment__SpawnConfiguredPickup` as part of the feature/pickup spawn bridge cluster with fresh Ghidra export evidence and no mutation. Fresh xrefs keep the configured-pickup helper reached from `CDestroyableSegment__VFunc_09_UpdatePickupAndChildSlot09`, `CDestroyableSegment__VFunc_10_SpawnRubbleEffects`, and `CDestroyableEndSegment__VFunc_10_SpawnEndRubbleEffects`; decompile evidence keeps the helper tied to `CWorldPhysicsManager__CreatePickup`, `DAT_008553f8`, segment field `this+0x3c`, and config field `+0xe8`. Wave1133 covers `6 rows`; current focused accounting is `184/1179 = 15.61%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 995; static debt remains `0 / 0 / 0`; the wave is a read-only review with no mutation. Verified backup: `G:\GhidraBackups\BEA_20260605-100620_post_wave1133_feature_pickup_current_risk_review_verified`. Runtime segment pickup/rubble behavior, exact source-body identity, concrete segment/config/pickup layouts, BEA patching, gameplay outcomes, visual QA, and rebuild parity remain separate proof.

## Wave1067 Destructable Controller Lookup/Damage Review

Wave1067 (`destructable-controller-lookup-damage-review-wave1067`) re-read sixteen existing `CDestructableSegmentsController__*` lookup, damage, health, cascade, and name-dispatch rows plus twenty adjacent segment/controller/unit context rows with no mutation. Fresh primary exports verified `16` metadata rows, `16` tag rows, `17` xref rows, `590` function-body instruction rows, and `16` decompile rows; context exports verified `20` metadata rows, `20` tag rows, `142` xref rows, `1757` function-body instruction rows, and `20` decompile rows.

Representative controller anchors:

| Address | Function | Static read-back evidence |
| --- | --- | --- |
| `0x00443fc0` | `CDestructableSegmentsController__Ctor` | Called from `CHiveBoss__Init`; constructor-like initializer stores caller-provided fields and clears controller state. |
| `0x00444030` | `CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold` | Called from `CUnit__ApplyDamage`; indexed segment damage path with threshold/callback update evidence. |
| `0x00444160` | `CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold` | Called from `CUnit__ApplyRandomDestructibleDamageBurst`; deduplicated random-damage burst plus threshold update logic. |
| `0x004442d0` | `CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex` | Called by `CUnit__VFunc26_GetRecentSegmentDamageMeter`; indexed getter for segment field `+0x14`. |
| `0x00444300` | `CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex` | Called by `CUnit__VFunc26_GetRecentSegmentDamageMeter`; indexed getter for segment field `+0x18`. |
| `0x004443f0` | `CDestructableSegmentsController__TriggerCoreCascadeIfEligible` | Called from `CUnit__MarkDestroyedAndCleanupLinks`; root/core cascade trigger without proving runtime cascade outcome. |
| `0x00444450` | `CDestructableSegmentsController__SetSegmentField0CByName` | Name-dispatch helper resolving mesh child names and writing segment field `+0x0c`. |
| `0x00444520` | `CDestructableSegmentsController__FindSegmentByName` | Name-dispatch lookup used by `CHiveBoss__Init`; returns tracked segment pointer or warning path. |
| `0x004445b0` | `CDestructableSegmentsController__SetSegmentActiveFlagByName` | Name-dispatch helper writing active flag `+0x1c` and refreshing cached metric. |
| `0x00444620` | `CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric` | Bulk active-flag setter and cached active-value refresh; preserves prior `CExplosionInitThing` owner correction. |

Queue closure remains `6246/6246 = 100.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface progress advances to `1248/1560 = 80.00%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260602-003225_post_wave1067_destructable_controller_lookup_damage_review_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`.

The pass made no mutation: no rename, signature change, comment change, tag change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation. Runtime destructable-controller damage/random burst/cascade/health-meter/name-dispatch behavior, exact controller/segment/CUnit layouts, exact wrapper/source identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1067; destructable-controller-lookup-damage-review-wave1067; 0x00443fc0 CDestructableSegmentsController__Ctor; 0x00444030 CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold; 0x00444160 CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold; 0x004442d0 CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex; 0x00444300 CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex; 0x004443f0 CDestructableSegmentsController__TriggerCoreCascadeIfEligible; 0x00444450 CDestructableSegmentsController__SetSegmentField0CByName; 0x00444520 CDestructableSegmentsController__FindSegmentByName; 0x004445b0 CDestructableSegmentsController__SetSegmentActiveFlagByName; 0x00444620 CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric; 812/1408 = 57.67%; 1248/1560 = 80.00%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260602-003225_post_wave1067_destructable_controller_lookup_damage_review_verified; read-only review.

## Wave1065 Destroyable Segment VFunc Review

Wave1065 (`destroyable-segment-vfunc-review-wave1065`) re-read twenty existing destroyable/destructable segment vtable/vfunc rows plus thirty-eight context rows with no mutation. Fresh primary exports verified `20` metadata rows, `20` tag rows, `41` xref rows, `1253` function-body instruction rows, and `20` decompile rows; context exports verified `38` metadata rows, `38` tag rows, `73` xref rows, `1948` function-body instruction rows, and `38` decompile rows.

Representative vtable anchors:

| Address | Function | Static read-back evidence |
| --- | --- | --- |
| `0x00442870` | `CDestroyableSegment__VFunc_11_RecomputeDamageScaleFields` | Shared slot-11 damage-scale recompute helper, DATA-backed from segment vtables including `0x005db058`, `0x005db0d8`, `0x005db140`, and `0x005db174`. |
| `0x00442960` | `CDestroyableSegment__VFunc_03_ApplyDamage` | Base slot-3 damage helper; DATA xref `0x005db038`. |
| `0x00442b20` | `CDestroyableSegment__VFunc_08_HandleSegmentBreak` | Base break handler; DATA xref `0x005db04c` plus direct reuse by core/swap/shared break paths. |
| `0x00442f60` | `CDestroyableSegment__VFunc_10_SpawnRubbleEffects` | Rubble/effects helper with DATA xrefs `0x005db054`, `0x005db094`, `0x005db13c`, and `0x005db170`. |
| `0x00443460` | `CDestroyableSegment__VFunc_00_HandleEvent3000Dispatch` | Shared slot-0 event-code-3000 dispatcher across base/component/core/variant vtables. |
| `0x004436d0` | `CDestroyableCoreSegment__VFunc_00_HandleEvent3000And3002Dispatch` | Core slot-0 event dispatcher for event records `3000` and `3002`; DATA xref `0x005db06c`. |
| `0x00443890` | `CDestroyableSegmentVariant__VFunc_03_ApplyDamage` | Shared leaf/end damage helper; DATA xrefs `0x005db0ec` and `0x005db120`. |
| `0x00443ea0` | `CDestroyableSegmentComponent__VFunc_08_HandleComponentBreak` | Component slot-8 break helper with owner-callback context; DATA xref `0x005db0cc`. |

Queue closure remains `6246/6246 = 100.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface progress advances to `1219/1560 = 78.14%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260601-232711_post_wave1065_destroyable_segment_vfunc_review_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`.

The pass made no mutation: no rename, signature change, comment change, tag change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation. Runtime destructable-segment damage/break/cascade/pickup/rubble/component behavior, exact event payload schema, exact layouts, exact source identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1065; destroyable-segment-vfunc-review-wave1065; 0x00442870 CDestroyableSegment__VFunc_11_RecomputeDamageScaleFields; 0x00442960 CDestroyableSegment__VFunc_03_ApplyDamage; 0x00442b20 CDestroyableSegment__VFunc_08_HandleSegmentBreak; 0x00442f60 CDestroyableSegment__VFunc_10_SpawnRubbleEffects; 0x00443460 CDestroyableSegment__VFunc_00_HandleEvent3000Dispatch; 0x004436d0 CDestroyableCoreSegment__VFunc_00_HandleEvent3000And3002Dispatch; 0x00443890 CDestroyableSegmentVariant__VFunc_03_ApplyDamage; 0x00443ea0 CDestroyableSegmentComponent__VFunc_08_HandleComponentBreak; 812/1408 = 57.67%; 1219/1560 = 78.14%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260601-232711_post_wave1065_destroyable_segment_vfunc_review_verified; no mutation.

## Wave942 Destructable-Segments Motion Review

Wave942 (`destructable-segments-motion-review-wave942`) re-reviewed the adjacent destructable-segments motion-controller bridge and saved six comment/tag normalizations after fresh Ghidra read-back. This was a comment-only mutation: no rename, no signature change, no function-boundary change, and no executable-byte change.

Primary rows: `0x00494c60 CDestructableSegmentsMotionController__Ctor`, `0x00494ca0 CDestructableSegmentsMotionController__ScalarDeletingDestructor`, `0x00494cc0 CDestructableSegmentsMotionController__Destructor`, `0x00494ce0 CDestructableSegmentsMotionController__ApplyRumbleTransform`, `0x00497130 CDestructableSegmentsMotionController__DestructorThunk_00497130`, and `0x00497140 CDestructableSegmentsMotionController__CacheNamedCollisionCylinders`.

Context read-back ties the cluster to `0x00497090 CMCHiveBoss__Constructor`, `0x00497110 CMCHiveBoss__ScalarDeletingDestructor`, `0x004976d0 CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0`, the recovered caller at `0x004976f1`, and vtables `0x005dc27c` and `0x005dc388`. The key normalization is that the `0x004976f1` cylinder-cache call is inside the recovered CMCHiveBoss slot-4 boundary, not a missing-boundary callsite, and the `0x00497130` row is a one-instruction `JMP 0x00494cc0` destructor thunk.

Fresh evidence counts: primary pre/post exports each have 6 metadata rows, 6 tag rows, 8 xref rows, 826 instruction rows, and 6 decompile rows; context exports have 9 metadata rows, 9 tag rows, 10 xref rows, 1371 instruction rows, and 9 decompile rows; vtable exports have 24 rows across `0x005dc27c` and `0x005dc388`. Wave911 focused re-audit progress after Wave942 is `180/1408 = 12.78%`; static export-contract closure remains `6113/6113 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260528-040608_post_wave942_destructable_segments_motion_review_verified`.

Probe token anchor: Wave942; `destructable-segments-motion-review-wave942`; comment-only mutation; `0x00494c60 CDestructableSegmentsMotionController__Ctor`; `0x00494ca0 CDestructableSegmentsMotionController__ScalarDeletingDestructor`; `0x00494cc0 CDestructableSegmentsMotionController__Destructor`; `0x00494ce0 CDestructableSegmentsMotionController__ApplyRumbleTransform`; `0x00497130 CDestructableSegmentsMotionController__DestructorThunk_00497130`; `0x00497140 CDestructableSegmentsMotionController__CacheNamedCollisionCylinders`; `0x00497090 CMCHiveBoss__Constructor`; `0x00497110 CMCHiveBoss__ScalarDeletingDestructor`; `0x004976d0 CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0`; `0x004976f1`; `0x005dc27c`; `0x005dc388`; `180/1408 = 12.78%`; `6113/6113 = 100.00%`; `G:\GhidraBackups\BEA_20260528-040608_post_wave942_destructable_segments_motion_review_verified`.

Runtime HiveBoss rumble/cylinder behavior, exact destructable-segments motion-controller and CMCHiveBoss layouts, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

## Wave841 Shared Default/False VFunc09

Wave841 Shared Default/False VFunc09 (`cvertexshader-shared-vfunc09-wave841`, `wave841-readback-verified`) records that `0x005019c0 VFuncSlot_09_005019c0` is now saved as `int __cdecl VFuncSlot_09_005019c0(void)`. The body is `XOR EAX,EAX; RET`. In this ownership area, the shared default/false virtual appears across destructible-segment/component and motion-controller RTTI-backed owner/slot rows; broader Wave841 evidence records `26 DATA pointer slots`, `49 RTTI-backed owner/slot rows`, representative owners `CControllerDefinition`, `CVertexShader`, and `CDXTrees`, queue proxy `5665/6098 = 92.90%`, next raw commentless row `0x0050ab60 CVBufTexture__RenderAndRestoreStateFlag4`, and verified backup `G:\GhidraBackups\BEA_20260525-032940_post_wave841_cvertexshader_shared_vfunc09_verified`. Exact source virtual method names, caller-specific semantics, concrete class layouts, runtime behavior, BEA patching, and rebuild parity remain deferred.

## Wave814 Mesh Segment Tail Caller Evidence (2026-05-24)

Wave814 mesh segment tail (`mesh-segment-tail-wave814`, `wave814-readback-verified`) corrected four adjacent CMesh helpers used by destructible-segment name and diagnostic paths: `0x004aa4e0 CMesh__SumChainedField1C`, `0x004aa500 CMesh__GetChainedRecordNameAndIdByIndex`, `0x004aa6b0 CMesh__GetNameOrUnknown`, and `0x004aa8a0 CMesh__FindPartByNameI`. Destructible-segment caller read-back shows the controller init/process/name-dispatch helpers calling `CMesh__GetNameOrUnknown` and `CMesh__FindPartByNameI` with CMesh pointers; the same wave records global mesh list `DAT_00704ad8`, empty-string fallback `0x00662b2c`, unknown-name fallback `0x0062f8d4`, post-wave strict proxy `5595/6098 = 91.75%`, and next raw commentless row `0x004adf80 CMesh__ClearField08`. Verified backup: `G:\GhidraBackups\BEA_20260524-141602_post_wave814_mesh_segment_tail_verified`. Exact concrete CMesh/CMeshPart/CRTMesh/destructible layouts, exact source-body identity, runtime mesh/destructible/RTMesh behavior, BEA patching, and rebuild parity remain deferred.

## Functions

| Address | Name | Status | Notes |
|---------|------|--------|-------|
| 0x00444620 | CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric | CORRECTED | Bulk active-flag setter over tracked segment array plus cached active-value refresh; replaces older `CExplosionInitThing` owner label |
| 0x00444660 | CDestructableSegmentsController__Init | HARDENED | Initialize controller, allocate segment tracking, process mesh roots, and set behavior/warning context |
| 0x00444940 | CDestroyableSegmentComponent__scalar_deleting_dtor | CORRECTED | Component scalar-deleting destructor wrapper |
| 0x00444960 | CDestroyableSegmentComponent__dtor_base | CORRECTED | Removes owner-link cell and chains directly to canonical `CDestroyableSegment__dtor_base` at `0x00442660` |
| 0x004449c0 | CDestructableSegmentsController__CreateSegment | HARDENED | Factory for segment types (0-3) |
| 0x00444be0 | CDestroyableSegmentVariant__scalar_deleting_dtor | RECOVERED | Shared scalar-deleting destructor boundary used by three non-core segment vtable slot-1 entries |
| 0x00444c00 | CDestroyableSegment__dtor_base_thunk | CORRECTED | Tail thunk jumping to canonical `CDestroyableSegment__dtor_base` at `0x00442660` |
| 0x00444c10 | CDestructableSegmentsController__ProcessNode | HARDENED | Recursive node processor, determines segment types |
| 0x00443460 | CDestroyableSegment__VFunc_00_HandleEvent3000Dispatch | RECOVERED | Shared slot-0 event-code-3000 dispatcher used by base/component/core/variant vtables |
| 0x004436d0 | CDestroyableCoreSegment__VFunc_00_HandleEvent3000And3002Dispatch | RECOVERED | Core slot-0 event dispatcher for event records `3000`/`0x0bb8` and `3002`/`0x0bba` |
| 0x00443480 | CDestroyableCoreSegment__Init | HARDENED | Core/primary segment initializer |
| 0x004434c0 | CDestroyableCoreSegment__VFunc_07_GetCoreField48 | RECOVERED | Core slot-7 field reader returning the float at `this+0x48` |
| 0x004434d0 | CDestroyableCoreSegment__scalar_deleting_dtor | CORRECTED | Core/primary scalar-deleting destructor wrapper |
| 0x004434f0 | CDestroyableCoreSegment__dtor_base | CORRECTED | Core/primary destructor body |
| 0x00443590 | CDestroyableCoreSegment__VFunc_11_RecomputeCoreDamageScaleFields | RECOVERED | Core slot-11 damage-scale recompute helper for fields `+0x0c/+0x10` |
| 0x004435c0 | CDestroyableCoreSegment__VFunc_06_CheckParentBreakGate | RECOVERED | Core slot-6 parent gate using field `+0x4c` and parent vtable slot `+0x18` |
| 0x004435f0 | CDestroyableCoreSegment__VFunc_03_ApplyDamage | CORRECTED | Core/primary damage-style vfunc slot 3 |
| 0x00443660 | CDestroyableCoreSegment__VFunc_08_HandleCoreBreakOrCascade | RECOVERED | Core slot-8 break/cascade helper with event `3002` context |
| 0x00443780 | CDestroyableSwapSegment__VFunc_03_ApplyDamage | CORRECTED | Swap-segment damage-style vfunc slot 3 |
| 0x00443810 | CDestroyableSwapSegment__VFunc_08_HandleSegmentBreak | CORRECTED | Swap-segment break-handler vfunc slot 8 |
| 0x00443830 | CDestroyableSwapSegment__VFunc_04_GetDamageStageIndex | RECOVERED | Standard/swap damage-stage index helper using fields `+0x0c`, `+0x10`, and `+0x40` |
| 0x00443890 | CDestroyableSegmentVariant__VFunc_03_ApplyDamage | RECOVERED | Shared leaf/end damage-style vfunc slot 3 body |
| 0x004439c0 | CDestroyableSegment__SharedVFunc_08_HandleChildBreak | CORRECTED | Shared leaf/end segment break-handler vfunc slot 8 |
| 0x004425a0 | CDestructableSegment__Init | HARDENED | Base segment initialization; stores controller/index/parent/value context, child list, active flag, and global monitor membership |
| 0x00442640 | CDestroyableSegment__scalar_deleting_dtor | CORRECTED | Scalar-deleting destructor wrapper |
| 0x00442660 | CDestroyableSegment__dtor_base | CORRECTED | Destructor body; removes global monitor membership and tears down children |
| 0x00442700 | CDestructableSegment__RegisterChild | CORRECTED | Adds a child segment to the parent child list; not global monitor registration |
| 0x00442710 | CDestroyableSegment__SpawnConfiguredPickup | CORRECTED | Configured pickup helper from segment/controller context; replaces stale `CExplosionInitThing` owner label |
| 0x00442870 | CDestroyableSegment__VFunc_11_RecomputeDamageScaleFields | RECOVERED | Shared slot-11 damage-scale recompute helper using `this+0x34`, `scaleFactor`, and `divisor` |
| 0x00442890 | CDestroyableSegment__SumActiveValueRecursive | HARDENED | Recursively sums active segment values |
| 0x00442900 | CDestructableSegment__GetTotalHealth | HARDENED | Recursively calculate total health/value of segment tree |
| 0x00442960 | CDestroyableSegment__VFunc_03_ApplyDamage | RECOVERED | Base slot-3 damage-style helper that records last damage context |
| 0x00442b00 | CDestroyableSegment__VFunc_06_CheckParentBreakGate | RECOVERED | Parent break-gate helper using parent vtable slot `+0x18` |
| 0x00442b20 | CDestroyableSegment__VFunc_08_HandleSegmentBreak | CORRECTED | Segment break handler; marks state, updates linked entries, dispatches children |
| 0x00442d40 | CDestroyableSegment__VFunc_09_UpdatePickupAndChildSlot09 | RECOVERED | Shared slot-9 update helper with configured-pickup and child-slot dispatch context |
| 0x00442f60 | CDestroyableSegment__VFunc_10_SpawnRubbleEffects | CORRECTED | Rubble/effects helper with mesh/effect, landscape damage, and configured pickup context |
| 0x00443a20 | CDestroyableEndSegment__VFunc_10_SpawnEndRubbleEffects | RECOVERED | End-segment slot-10 effect helper that calls the base rubble/effects path |
| 0x004439f0 | CDestroyableEndSegment__VFunc_11_RecomputeEndDamageScaleFields | RECOVERED | End-segment slot-11 damage-scale recompute helper |
| 0x00443ea0 | CDestroyableSegmentComponent__VFunc_08_HandleComponentBreak | RECOVERED | Component slot-8 break helper with owner-callback context |
| 0x004014a0, 0x004059c0, 0x00405ee0, 0x004bfc60, 0x0055df1f | shared vtable/CRT helpers | RECOVERED | Shared return-value targets and purecall-style CRT handler reached by destructable vtable slots |

## Details

### CDestructableSegmentsController__Init (0x00444660)

- **Purpose**: Initialize the destructible segments controller for a building/structure
- **Xref**: Found via debug path at 0x006287b4 (lines 0x184, 0x1a8)
- **Behavior**:
  - Checks if mesh exists for building, warns if not
  - Allocates segment tracking array based on mesh segment count
  - Iterates through "component" named mesh parts
  - Creates segment handlers for each component
  - Sets up monitor system for damage tracking
  - Calculates initial total health value
- **Warning strings**:
  - "Warning: No mesh for building" (0x006287ec)
  - "Warning: %s only has Primary component" (0x00628768)
  - "Warning: %s Can't find mesh part" (0x006286c0)
  - "Warning: %s Can't find segment" (0x00628714)
  - "ERROR: no behavour for unit" (0x006286a4)

### CDestructableSegmentsController__CreateSegment (0x004449c0)

- **Purpose**: Factory function to create different types of destructible segments
- **Xref**: Found via debug path at 0x006287b4 (lines 0x1e3, 0x1e8, 0x1ed, 0x1f2)
- **Parameters**:
  - param_1: Segment type (0-3)
  - param_2: Mesh/component data pointer
  - param_3: Parent segment (or NULL for root)
  - param_4: Health/scale value
- **Segment Types**:
  - Type 0: Primary component (0x50 bytes, vtable 0x005db06c)
  - Type 1: Standard segment (0x48 bytes, vtable 0x005db148)
  - Type 2: Leaf segment (0x54 bytes, vtable 0x005db114)
  - Type 3: End segment (0x54 bytes, vtable 0x005db0e0)
- **Warning strings**:
  - "WARNING: unknown Destroyable segment type" (0x00628890)

## Wave748 Unwind Continuation Read-Back

Wave748 unwind continuation saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for DestructableSegmentsController.cpp cleanup callbacks at `0x005d2170 Unwind@005d2170`, `0x005d2189 Unwind@005d2189`, `0x005d2191 Unwind@005d2191`, `0x005d21c0 Unwind@005d21c0`, `0x005d21e0 Unwind@005d21e0`, `0x005d21f9 Unwind@005d21f9`, `0x005d2212 Unwind@005d2212`, and `0x005d222b Unwind@005d222b`. The rows have scope-table DATA xrefs from `0x0061b064` through `0x0061b0e4`; observed bodies call `OID__FreeObject_Callback`, `CDestroyableSegment__dtor_base`, or `CGenericActiveReader__dtor`.

The allocation-cleanup rows use the DestructableSegmentsController.cpp debug path at `0x006287b4`, including line `0x1a8` at `0x005d2170` and CreateSegment-adjacent lines `0x1e3`, `0x1e8`, `0x1ed`, and `0x1f2` at `0x005d21e0` through `0x005d222b`. The tranche is tagged `unwind-continuation-wave748` / `wave748-readback-verified` and verified by backup `G:\GhidraBackups\BEA_20260522-183258_post_wave748_unwind_continuation_verified`. Next high-signal queue head is `0x005d2250 Unwind@005d2250`; earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.

This is saved static retail Ghidra evidence only. Exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

### CDestructableSegmentsController__ProcessNode (0x00444c10)

- **Purpose**: Recursively process mesh nodes to build segment hierarchy
- **Behavior**:
  - Traverses mesh hierarchy recursively
  - Determines segment type based on node name prefixes:
    - "CORE" prefix -> Type 0 (primary)
    - Has children -> Type 1 (standard)
    - "LE"/"LN" prefix -> Type 3 (end segment)
    - Otherwise -> Type 2 (leaf segment)
  - Links parent-child segment relationships
  - Accumulates health values up the tree
- **Warning strings**:
  - "Woops: %s Looks like you forgot..." (0x006288fc)
  - "WARNING: %s found second start component" (0x00628934)
  - "Warning: %s Child of CORE1 was..." (0x006288bc)

### CDestroyableCoreSegment__Init (0x00443480)

- **Purpose**: Initialize a primary/core destroyable segment with extra tracking data
- **Behavior**:
  - Calls base CDestructableSegment__Init
  - Initializes additional fields at offsets 0x44-0x4c
  - Sets component index at offset 0x40
  - Sets vtable to 0x005db06c

### CDestructableSegment__Init (0x004425a0)

- **Purpose**: Base initialization for all segment types
- **Behavior**:
  - Sets up initial vtable context and base segment vtable `0x005db02c`
  - Stores controller, segment index, parent segment, and segment value context
  - Initializes default vector/value fields and active flag
  - Initializes the child segment `CSPtrSet`
  - Registers the segment with the global segment monitor at `DAT_00855180`

### CDestroyableSegment__scalar_deleting_dtor (0x00442640)

- **Purpose**: Scalar-deleting destructor wrapper
- **Behavior**:
  - Calls `CDestroyableSegment__dtor_base`
  - Frees `this` through `OID__FreeObject` when flags bit `0` is set
  - Returns `this`

### CDestroyableSegment__dtor_base (0x00442660)

- **Purpose**: Base destroyable-segment destructor body
- **Behavior**:
  - Restores base vtable context
  - Removes the instance from `DAT_00855180`
  - Walks child-list entries at `this+0x24` and invokes their deleting destructors
  - Clears the child `CSPtrSet`
  - Chains to `CMonitor__Shutdown`

### CDestructableSegment__RegisterChild (0x00442700)

- **Purpose**: Register a child segment on a parent segment
- **Behavior**: Adds `childSegment` to the parent child `CSPtrSet` at `this+0x24`. The earlier broad monitor-registration wording was wrong; global monitor membership is handled by `CDestructableSegment__Init`.

### CDestroyableSegment__SpawnConfiguredPickup (0x00442710)

- **Purpose**: Create configured pickup from destroyable segment context
- **Behavior**:
  - Reads owning controller/unit context through `this+0x3c`
  - Checks configured pickup data at the unit/config side (`config+0xe8`)
  - Calls `CWorldPhysicsManager__CreatePickup`
  - Initializes influence/pickup context and dispatches the pickup vfunc
  - Corrects the older stale `CExplosionInitThing` constructor-like owner label

### CDestructableSegment__GetTotalHealth (0x00442900)

- **Purpose**: Calculate total health of segment and all children recursively
- **Behavior**:
  - If segment is active and not destroyed, adds own health
  - Recursively traverses child list (offset 0x24)
  - Sums health values from entire subtree
  - Returns total as float

### CDestroyableSegment__VFunc_08_HandleSegmentBreak (0x00442b20)

- **Purpose**: Destroyable segment break handler
- **Behavior**:
  - Marks the segment broken and clears field `+0x0c`
  - Updates controller state and linked segment/unit entries
  - Dispatches child destruction events

### CDestroyableSegment__VFunc_10_SpawnRubbleEffects (0x00442f60)

- **Purpose**: Rubble/effects helper for destroyable segment break context
- **Behavior**:
  - Resolves generic mesh/rubble context
  - Creates particle effects and periodically applies landscape damage
  - Can call `CDestroyableSegment__SpawnConfiguredPickup`
  - Keeps missing-rubble-data warning context public-safe without claiming runtime behavior

## Segment Hierarchy

```
CDestructableSegmentsController (this)
  +0x04: segment_array*     - Array of segment pointers
  +0x08: segment_count      - Number of segments
  +0x0c: root_segment*      - Root/primary segment
  +0x10: unit_data*         - Parent unit reference
  +0x18: total_health       - Cached total health
  +0x1c: health_scale       - Health scaling factor
  +0x20: component_count    - Number of components found

CDestructableSegment (base class)
  +0x00: vtable*
  +0x04: flags
  +0x08: segment_index
  +0x0c: health_mult_x (1.0)
  +0x10: health_mult_y (1.0)
  +0x14: health_mult_z (-1.0)
  +0x18: unknown
  +0x1c: is_active (1)
  +0x20: parent_segment*
  +0x24: child_list*
  +0x34: health_value
  +0x38: unknown
  +0x3c: controller*
```

## Vtables

| Address | Type | Description |
|---------|------|-------------|
| 0x005db06c | Primary | Core/primary segment (Type 0) |
| 0x005db148 | Standard | Standard segment with children (Type 1) |
| 0x005db114 | Leaf | Leaf segment, no children (Type 2) |
| 0x005db0e0 | End | End/terminal segment (Type 3) |
| 0x005db02c | Base | Base segment class |

Wave 351 vtable-slot read-back records slot `1` at `0x005db0b0` pointing to `CDestroyableSegmentComponent__scalar_deleting_dtor`, and slot `1` at `0x005db0e4`, `0x005db118`, and `0x005db14c` pointing to the recovered shared `CDestroyableSegmentVariant__scalar_deleting_dtor` boundary. The concrete class names for those three variants remain open.

Wave 352 vtable-slot read-back records slot `0` at the base/component/end/leaf/standard vtables resolving to `CDestroyableSegment__VFunc_00_HandleEvent3000Dispatch`, slot `4` at the standard vtable resolving to `CDestroyableSwapSegment__VFunc_04_GetDamageStageIndex`, and slot `3` at the end/leaf vtables resolving to `CDestroyableSegmentVariant__VFunc_03_ApplyDamage`. Other unresolved shared slot targets remain queued for later inspection.

Wave 353 vtable-slot read-back records the remaining base/core/component/end/leaf/standard tail slots now resolved to saved function objects, including base slot `3` at `0x00442960`, parent-gate slot `6` at `0x00442b00`, shared float-zero slot `7` at `0x004bfc60`, shared return helpers at `0x004014a0`, `0x004059c0`, and `0x00405ee0`, core event/break/field helpers from `0x004434c0` through `0x004436d0`, shared slot `9` at `0x00442d40`, shared slot `11` at `0x00442870`, component break slot `8` at `0x00443ea0`, and end-segment slot `10`/`11` helpers at `0x00443a20` and `0x004439f0`.

## Related Systems

- **Monitor System**: CSPtrSet__Init (create), CSPtrSet__AddToHead (register) - tracks active game objects
- **Memory Allocation**: OID__AllocObject - allocator with debug tracking (file/line)
- **String Lookup**: FUN_004aa6b0, FUN_004aa820 - name/component string operations


## Additional Recovered Functions (Headless 2026-02-26)

| Address | Name | Status | Notes |
|---------|------|--------|-------|
| 0x004429a0 | CDestructableSegment__DispatchChildDestructionEvents | RENAMED | Child-destruction dispatch helper: immediate vs delayed event scheduling based on current segment state. |
| 0x00442a80 | CDestructableSegment__SetSubtreeActiveFlagRecursive | RENAMED | Recursively sets active flag (`+0x1C`) on a segment subtree. |
| 0x00442ac0 | CDestructableSegment__PropagateDamageToChildren | RENAMED | Child fanout helper invoking damage-style vfunc (`+0x0C`) with controller context. |
| 0x00443fc0 | CDestructableSegmentsController__Ctor | RENAMED | Constructor-like initialization for controller object (called from `CHiveBoss__Init`). |
| 0x00444000 | CDestructableSegmentsController__Dtor | RENAMED | Controller teardown helper freeing owned arrays and nested objects. |
| 0x004443f0 | CDestructableSegmentsController__TriggerCoreCascadeIfEligible | CORRECTED | Cascade eligibility gate that triggers subtree activation + child damage cascade without overclaiming threshold direction. |
| 0x00444450 | CDestructableSegmentsController__SetSegmentField0CByName | HARDENED | Name/tag-based segment lookup setter for field `+0x0c` with float stack-argument evidence. |
| 0x004444b0 | CDestructableSegmentsController__SetSegmentFields0C10ByName | HARDENED | Name/tag-based segment lookup setter for fields `+0x0c/+0x10` with active-value refresh. |
| 0x00444520 | CDestructableSegmentsController__FindSegmentByName | HARDENED | Returns tracked segment pointer by name/tag (used by `CHiveBoss__Init`). |
| 0x00444580 | CDestructableSegmentsController__SetAllSegmentsField0C | HARDENED | Bulk setter over all tracked segments for field `+0x0c`. |
| 0x004445b0 | CDestructableSegmentsController__SetSegmentActiveFlagByName | HARDENED | Name/tag-based segment lookup setter for active flag `+0x1c` with active-value refresh. |
| 0x00444620 | CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric | CORRECTED | Bulk active-flag setter across all tracked segment pointers and cached active-value refresh; supersedes older `CExplosionInitThing` owner label. |
| 0x004433f0 | CDestroyableCoreSegment__AreCoreChildrenDestroyed | CORRECTED | Core-child status gate; corrected from older controller-owner label because callers pass root/core segment context. |
| 0x00444030 | CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold | RENAMED | Indexed damage dispatch path with shared threshold/callback update. |
| 0x00444160 | CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold | RENAMED | Deduplicated random-damage burst pass with shared threshold update logic. |
| 0x004442d0 | CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex | CORRECTED | Indexed getter for field `+0x14`; damage-style vfuncs write the observed time source here. |
| 0x00444300 | CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex | CORRECTED | Indexed getter for field `+0x18`; damage-style vfuncs write raw damage amount here. |
| 0x00444330 | CDestructableSegmentsController__GetCurrentSubtreeHealthIfAnyActive | RENAMED | Current subtree-health sum when active segments exist (else zero). |
| 0x00444370 | CDestructableSegmentsController__GetRootSubtreeHealthIfAnyActive | RENAMED | Root subtree-health query when active segments exist (else zero). |
| 0x004443b0 | CDestructableSegmentsController__GetCachedTotalHealthIfAnyActive | RENAMED | Cached total-health query when active segments exist (else zero). |
| 0x00444940 | CDestroyableSegmentComponent__scalar_deleting_dtor | CORRECTED | Component scalar-deleting destructor wrapper. |
| 0x00444960 | CDestroyableSegmentComponent__dtor_base | CORRECTED | Component destructor body removes owner-link cell at `this+0x40` and chains directly to `0x00442660`. |
| 0x00444be0 | CDestroyableSegmentVariant__scalar_deleting_dtor | RECOVERED | Recovered shared scalar-deleting destructor boundary for three non-core segment vtable slot-1 entries. |
| 0x00444c00 | CDestroyableSegment__dtor_base_thunk | CORRECTED | Tail thunk jumping to canonical base destructor at `0x00442660`. |
| 0x00443460 | CDestroyableSegment__VFunc_00_HandleEvent3000Dispatch | RECOVERED | Shared event-code-3000 dispatcher for base/component/core/variant vtable slot `0`. |
| 0x00443830 | CDestroyableSwapSegment__VFunc_04_GetDamageStageIndex | RECOVERED | Standard/swap damage-stage index helper that clamps the derived stage index to the observed stage count. |
| 0x00443890 | CDestroyableSegmentVariant__VFunc_03_ApplyDamage | RECOVERED | Shared leaf/end damage-style body that records damage context and dispatches the break handler when needed. |
| 0x00442960 | CDestroyableSegment__VFunc_03_ApplyDamage | RECOVERED | Base slot-3 damage-style helper that records last damage context. |
| 0x00442b00 | CDestroyableSegment__VFunc_06_CheckParentBreakGate | RECOVERED | Parent break gate over parent vtable slot `+0x18`. |
| 0x00442d40 | CDestroyableSegment__VFunc_09_UpdatePickupAndChildSlot09 | RECOVERED | Shared slot-9 update helper with configured-pickup and child-slot recursion context. |
| 0x00442870 | CDestroyableSegment__VFunc_11_RecomputeDamageScaleFields | RECOVERED | Shared slot-11 damage-scale recompute helper. |
| 0x004436d0 | CDestroyableCoreSegment__VFunc_00_HandleEvent3000And3002Dispatch | RECOVERED | Core event dispatcher for `3000` and `3002` paths. |
| 0x004435c0 | CDestroyableCoreSegment__VFunc_06_CheckParentBreakGate | RECOVERED | Core parent gate helper. |
| 0x004434c0 | CDestroyableCoreSegment__VFunc_07_GetCoreField48 | RECOVERED | Core field `+0x48` reader. |
| 0x00443660 | CDestroyableCoreSegment__VFunc_08_HandleCoreBreakOrCascade | RECOVERED | Core break/cascade helper. |
| 0x00443590 | CDestroyableCoreSegment__VFunc_11_RecomputeCoreDamageScaleFields | RECOVERED | Core damage-scale recompute helper. |
| 0x00443ea0 | CDestroyableSegmentComponent__VFunc_08_HandleComponentBreak | RECOVERED | Component break helper with owner callback context. |
| 0x00443a20 | CDestroyableEndSegment__VFunc_10_SpawnEndRubbleEffects | RECOVERED | End-segment effect helper. |
| 0x004439f0 | CDestroyableEndSegment__VFunc_11_RecomputeEndDamageScaleFields | RECOVERED | End-segment damage-scale recompute helper. |

## Wave 353 Vtable Tail Boundary Read-Back (2026-05-12)

Headless dry/apply/read-back recovered and saved names, signatures, comments, and tags for `17` destructable vtable-tail targets. Final read-back verified `21` metadata rows, `21` decompile exports, `2113` xref rows, `4641` instruction rows, `21` tag rows, `72` vtable-slot rows, `17` vtable evidence hits, `10` xref evidence hits, and `17` instruction evidence hits.

Key corrections:

- The remaining base/core/component/end/leaf/standard vtable tail slots now have saved function objects instead of missing-boundary entries.
- `0x00442960` is now the base slot-3 damage-style helper, while `0x00443890` remains the shared leaf/end slot-3 body from Wave 352.
- `0x00442b00` and `0x004435c0` separate base/shared and core parent-gate helpers instead of forcing a single owner.
- `0x00443a20` is bounded as end-segment extra rubble/effects setup and does not prove runtime rubble behavior.
- Shared return-value targets and the purecall-style CRT handler are recorded conservatively because their vtable reachability is broader than this file.

The refreshed live queue reports `5999` functions, `1168` commented functions, `4831` commentless functions, `1951` undefined signatures, and `2075` `param_N` signatures. Current confirmation proxies remain telemetry only: comment-backed `1168/5999 = 19.47%`, strict clean-signature `1105/5999 = 18.42%`. The actual live Ghidra project backup is verified at `G:\GhidraBackups\BEA_20260512_223409_post_wave353_destructable_vtable_tail_verified` with `19` files, `152931207` bytes, and `HashDiffCount=0`.

Claim boundary: this is static retail Ghidra evidence only. It corrects the current saved names, signatures, comments, tags, and recovered boundaries, but it does not prove exact source identity, concrete class layout, local/type recovery, runtime destruction/cascade/pickup/rubble behavior, BEA launch, game patching, or rebuild parity.

## Wave 352 Vtable Boundary Read-Back (2026-05-12)

Headless dry/apply/read-back recovered and saved names, signatures, comments, and tags for `3` destructable vtable targets at `0x00443460`, `0x00443830`, and `0x00443890`. Final read-back verified `3` metadata rows, `3` decompile exports, `8` xref rows, `591` instruction rows, `3` tag rows, `40` vtable-slot rows, `8` vtable evidence hits, `8` xref evidence hits, and `11` instruction evidence hits.

Key corrections:

- `0x00443460` is now `CDestroyableSegment__VFunc_00_HandleEvent3000Dispatch`, a shared slot-0 event-code-3000 dispatcher.
- `0x00443830` is now `CDestroyableSwapSegment__VFunc_04_GetDamageStageIndex`, a standard/swap damage-stage index helper.
- `0x00443890` is now `CDestroyableSegmentVariant__VFunc_03_ApplyDamage`, a shared leaf/end damage-style body.
- The refreshed base-plus-variant vtable export ties those saved functions to slot `0`, slot `4`, and slot `3` respectively while leaving other unresolved shared slots queued.

The refreshed live queue reports `5982` functions, `1151` commented functions, `4831` commentless functions, `1951` undefined signatures, and `2075` `param_N` signatures. Current confirmation proxies remain telemetry only: comment-backed `1151/5982 = 19.24%`, strict clean-signature `1088/5982 = 18.19%`. The actual live Ghidra project backup is verified at `G:\GhidraBackups\BEA_20260512_215540_post_wave352_destructable_vtable_verified` with `19` files, `152931207` bytes, and `HashDiffCount=0`.

Claim boundary: this is static retail Ghidra evidence only. It corrects the current saved names, signatures, comments, tags, and three recovered boundaries, but it does not prove exact source identity, concrete class layout, local/type recovery, runtime destruction/cascade/random-damage/rubble/mesh behavior, BEA launch, game patching, or rebuild parity.

## Wave 351 Bridge Signature / Boundary Read-Back (2026-05-12)

Headless dry/apply/read-back saved names, signatures, comments, and tags for `5` destructable bridge/component/thunk targets from `0x00444620` through `0x00444c00`. Final read-back verified `5` metadata rows, `5` decompile exports, `7` xref rows, `555` instruction rows, `5` tag rows, `20` vtable-slot rows, `4` vtable evidence hits, `7` xref evidence hits, and `8` instruction evidence hits.

Key corrections:

- `0x00444620` is now `CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric`, not an `CExplosionInitThing` helper label.
- `0x00444940` and `0x00444960` are the component scalar-deleting destructor wrapper and component destructor body.
- `0x00444960` chains directly to canonical `CDestroyableSegment__dtor_base` at `0x00442660`; the focused probe corrected the initial over-specific thunk expectation.
- `0x00444be0` is a recovered shared scalar-deleting destructor boundary for three non-core segment vtable slot-1 entries.
- `0x00444c00` is a tail thunk that jumps to canonical `CDestroyableSegment__dtor_base` at `0x00442660`; decompile may render the target body through the thunk.

The refreshed live queue reports `5979` functions, `1148` commented functions, `4831` commentless functions, `1951` undefined signatures, and `2075` `param_N` signatures. Current confirmation proxies remain below `20%`: comment-backed `1148/5979 = 19.20%`, strict clean-signature `1085/5979 = 18.15%`.

Claim boundary: this is static retail Ghidra evidence only. It corrects the current saved names, signatures, comments, tags, and one recovered boundary, but it does not prove exact source identity, concrete class layout, runtime destruction/cascade/random-damage/rubble/mesh behavior, BEA launch, game patching, or rebuild parity.

## Wave 350 Tail Signature / Comment Read-Back (2026-05-12)

Headless dry/apply/read-back saved names, signatures, comments, and tags for `8` destructable controller tail/name-dispatch/lifecycle targets from `0x00444450` through `0x00444c10`. Final read-back verified `8` metadata rows, `8` decompile exports, `10` xref rows, `1816` instruction rows, `8` tag rows, `230` callsite instruction rows, `10` callsite evidence hits, and `8` return-evidence hits.

Key hardening:

- `0x00444450`, `0x004444b0`, `0x00444520`, `0x00444580`, and `0x004445b0` now have saved proof-boundary signatures/comments/tags for the name-dispatch setters/find helper, including float or active-flag stack-argument evidence.
- `0x00444660` now has a saved `CDestructableSegmentsController__Init` signature/comment/tag and caller proof from `CUnit__Init` through the controller pointer at `this+0x178`.
- `0x004449c0` now has a saved `CDestructableSegmentsController__CreateSegment` signature/comment/tag that records segment kinds `0..3` and vtable variants `0x005db148`, `0x005db114`, and `0x005db0e0`.
- `0x00444c10` now has a saved `CDestructableSegmentsController__ProcessNode` signature/comment/tag for recursive mesh-node classification, create/register/map, and child traversal context.

The refreshed live queue reports `5978` functions, `1143` commented functions, `4835` commentless functions, `1951` undefined signatures, and `2078` `param_N` signatures. Current confirmation proxies remain below `20%`: comment-backed `1143/5978 = 19.12%`, strict clean-signature `1080/5978 = 18.07%`.

Claim boundary: this is static retail Ghidra evidence only. It corrects the current saved signatures and comments, but it does not prove exact source identity, concrete class layout, runtime destruction/cascade/random-damage/rubble/mesh behavior, BEA launch, game patching, or rebuild parity.

## Wave 349 Signature / Comment Read-Back (2026-05-12)

Headless dry/apply/read-back saved names, signatures, comments, and tags for `18` destructable controller/core/swap segment targets from `0x004433f0` through `0x004443f0`. Final read-back verified `18` metadata rows, `18` decompile exports, `22` xref rows, `666` instruction rows, `18` tag rows, and `6` vtable evidence hits.

Key corrections:

- `0x004433f0` is now `CDestroyableCoreSegment__AreCoreChildrenDestroyed`, not a controller-owned helper label.
- `0x00443480`, `0x004434d0`, and `0x004434f0` are the core/primary segment init/destructor helpers.
- `0x004435f0`, `0x00443780`, `0x00443810`, and `0x004439c0` are core/swap/shared damage and break vfunc helpers.
- `0x004442d0` and `0x00444300` are indexed last-damage time/amount getters, not generic field getters.
- `0x004443f0` is `CDestructableSegmentsController__TriggerCoreCascadeIfEligible`; the older threshold-exceeded wording overclaimed the threshold direction.

Claim boundary: this is static retail Ghidra evidence only. It corrects the current saved labels and comments, but it does not prove exact source identity, concrete class layout, runtime destruction/cascade/random-damage/rubble behavior, BEA launch, game patching, or rebuild parity.

## Wave 348 Signature / Comment Read-Back (2026-05-12)

Headless dry/apply/read-back saved names, signatures, comments, and tags for `12` base destructable/destroyable segment targets from `0x004425a0` through `0x00442f60`. Final read-back verified `12` metadata rows, `12` decompile exports, `44` xref rows, `996` instruction rows, `12` tag rows, and `6` vtable evidence hits.

Claim boundary: this is static retail Ghidra evidence only. It corrects the current saved labels and comments, including the `CDestructableSegment__RegisterChild` child-list correction and stale `CExplosionInitThing` owner correction, but it does not prove exact source identity, concrete class layout, runtime destruction/rubble behavior, BEA launch, game patching, or rebuild parity.
