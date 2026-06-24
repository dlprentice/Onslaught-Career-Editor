# Unit.cpp Functions

Wave1194 current-risk update: Wave1194 (`wave1194-unit-world-airunit-lifecycle-score17-current-risk-review`) accounts for `9 unit/world/airunit lifecycle score17 current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence and saved comment/tag normalization. The rows are `CUnit__VFunc08_InitAndAddToWorld`, `CUnit__VFunc18_SyncOldVectorAndClampHeight`, `CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk`, `CWorld__RemoveUnitFromOccupancyGrid_Thunk`, `CGroundAttackAircraft__Destructor_VFunc01`, `CDropship__Destructor_VFunc01`, `CPlane__Destructor_VFunc01`, `CDiveBomber__Destructor_VFunc01`, and `CFenrir__Destructor_VFunc01`. Ghidra dry/apply/final-dry reported `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=9 tags_added=132 missing=0 bad=0`, then `updated=9 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=9 tags_added=132 missing=0 bad=0`, then final dry updated=0 skipped=9. No rename, no signature change, no function-boundary change, and no executable-byte change occurred. Codex read-only consult used; no Cursor/Composer. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt; expanded static surface remains `1560/1560 = 100.00%`; Wave1108 current focused accounting is `865/1179 = 73.37%`; current risk candidates: 6166; current focused candidates: 1154; live regenerated current focused candidates: 1154; remaining active focused work: 314; current-risk denominator; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `26 xref rows`, `177 instruction rows`, and `9 decompile rows`. Verified backup: `G:\GhidraBackups\BEA_20260606-193734_post_wave1194_unit_world_airunit_lifecycle_score17_current_risk_review_verified`. Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference; exact CUnit/CWorld/aircraft/grid/set/list layouts, exact source virtual/destructor identity, runtime lifecycle/occupancy/height/aircraft teardown behavior, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof. Probe token anchor: Wave1194; wave1194-unit-world-airunit-lifecycle-score17-current-risk-review; 865/1179 = 73.37%; 9 unit/world/airunit lifecycle score17 current-risk rows; current focused candidates: 1154; live regenerated current focused candidates: 1154; remaining active focused work: 314; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=9 skipped=0; comment_only_updated=9; tags_added=132; final dry updated=0 skipped=9; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consult used; no Cursor/Composer; CUnit__VFunc08_InitAndAddToWorld; CUnit__VFunc18_SyncOldVectorAndClampHeight; CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk; CWorld__RemoveUnitFromOccupancyGrid_Thunk; CGroundAttackAircraft__Destructor_VFunc01; CDropship__Destructor_VFunc01; CPlane__Destructor_VFunc01; CDiveBomber__Destructor_VFunc01; CFenrir__Destructor_VFunc01; 0 / 0 / 0; 6411/6411 = 100.00%; 26 xref rows; 177 instruction rows; 9 decompile rows; G:\GhidraBackups\BEA_20260606-193734_post_wave1194_unit_world_airunit_lifecycle_score17_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.


> Source File: Unit.cpp | Binary: BEA.exe

Wave1168 current-risk update: Wave1168 (`wave1168-unit-target-reader-tail-current-risk-review`) accounts for `12 CUnit / CSquadNormal / SharedUnitAI target-reader tail current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, no runtime-file mutation, and Codex read-only consult used. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `648/1179 = 54.96%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 531; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `191 xref rows` and `618 instruction rows`. Static anchors include `CSquadNormal__IsValidLinkedSupportForTarget`, `CUnit__ForwardAimTransformAndAttachTargetReader`, `CUnit__SetSpawnCooldownState3`, `CUnit__ForwardAttachedNodeVFunc14IfPresent`, `CUnit__VFunc22_ActivateLinkedTargetsAndChildren`, and `SharedUnitAI__UpdateField28TargetReaderGate_004ffbb0`; xref/callee context includes `CSpawnerThng__ProcessSpawnWave` and `OID__UpdateAimTransformAndAttachTargetReader`. Boundary: `CUnit__SetSpawnCooldownState3` is adjacent CUnit tail/spawn-cooldown accounting, not target-reader behavior. Verified backup: `G:\GhidraBackups\BEA_20260606-052300_post_wave1168_unit_target_reader_tail_current_risk_review_verified`. Runtime targeting behavior, runtime squad AI behavior, runtime attached-node behavior, exact CUnit/CSquadNormal/CUnitAI/SharedUnitAI concrete layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1168; wave1168-unit-target-reader-tail-current-risk-review; 648/1179 = 54.96%; 12 CUnit / CSquadNormal / SharedUnitAI target-reader tail current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 531; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult used; 0 / 0 / 0; 6411/6411 = 100.00%; 191 xref rows; 618 instruction rows; CSquadNormal__IsValidLinkedSupportForTarget; CUnit__ForwardAimTransformAndAttachTargetReader; CUnit__SetSpawnCooldownState3; CUnit__ForwardAttachedNodeVFunc14IfPresent; CUnit__VFunc22_ActivateLinkedTargetsAndChildren; SharedUnitAI__UpdateField28TargetReaderGate_004ffbb0; CSpawnerThng__ProcessSpawnWave; OID__UpdateAimTransformAndAttachTargetReader; G:\GhidraBackups\BEA_20260606-052300_post_wave1168_unit_target_reader_tail_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Wave1156 current-risk update: Wave1156 (`wave1156-sharedunitvfunc-current-risk-review`) accounts for `29 SharedUnitVFunc current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, no runtime-file mutation, and Codex read-only consults used for export/backup/map sanity while Codex root made the final judgment. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `453/1179 = 38.42%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 726; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `951 DATA xrefs`, `442 instruction rows`, `wave1083-readback-verified=6`, and `wave1085-readback-verified=23`. Static anchors include `SharedUnitVFunc__WriteVector1cMinus8cToOut_00401550`, `SharedUnitVFunc__TestField17c19cReadiness_004fd440`, `SharedUnitVFunc__CopySourceVectors114120AndRefresh_004fe4a0`, `SharedUnitVFunc__ForwardField208Slot10_004fce00`, and `SharedUnitVFunc__TestField17cEntryNameMatch_004fe310`. Verified backup: `G:\GhidraBackups\BEA_20260605-231547_post_wave1156_sharedunitvfunc_current_risk_review_verified`. Runtime shared-unit vfunc behavior, exact source virtual names, exact concrete layouts, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.

## Overview
> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

Core unit gameplay mechanics for all interactive actors in the game (mechs, vehicles, infantry, emplacements). This file handles initialization, damage calculation, position/rotation updates, and visual/audio effects tied to unit state. Wave1097 re-read the CUnit destructor/thunk/lifecycle cleanup graph with no mutation, including `0x004bfe00 CUnit__dtor_base_Thunk_004bfe00`, `0x004f84c0 CUnit__VFunc01_ScalarDeletingDtor`, `0x004f84e0 CUnit__dtor_base`, `0x0050ee90 CUnit__scalar_deleting_dtor`, `0x004f95d0 CUnit__VFunc02_CleanupWorldLinksAndForward`, `0x004fcfa0 CUnit__ClearSpawnerSet`, `0x004fcfe0 CUnit__ReleaseChildUnits`, `0x004fd040 CUnit__ResetDeploymentGraphAndScheduleEvent`, `0x004fd140 CUnit__MarkDestroyedAndCleanupLinks`, `0x004cb0b0 ParticleEffectLink__SetHandleStateAndClear`, `0x004013d0 CActor__dtor_base`, and `0x004f3f00 CComplexThing__dtor_base`; verified backup `G:\GhidraBackups\BEA_20260604-182217_post_wave1097_cunit_dtor_thunk_lifecycle_review_verified`. Wave1075 recovered `0x004dfa40 CUnit__VFunc08_InitAndAddToWorld` from CUnit-family vtable table `0x005dfd40` slot `0x005dfd60`; raw candidate `0x004dfa47` sits inside the recovered body, which ends at `0x004dfa9a` and does not absorb `0x004dfaa0`, with static calls through `CUnit__Init` and `CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk`; verified backup `G:\GhidraBackups\BEA_20260602-060358_post_wave1075_cunit_vfunc08_boundary_verified`. Wave1072 re-read the OID/target-profile ballistic Unit bridge with no mutation, including `0x005096a0 CUnit__ComputeMinBallisticTravelDistance`, `0x005099a0 CUnit__ComputeMaxBallisticTravelDistance`, `0x0050a0d0 CUnit__HasMaskBitsA8`, and `0x0050a290 CUnit__IsTargetTimeoutBeforeProfileLimit`; verified backup `G:\GhidraBackups\BEA_20260602-035902_post_wave1072_oid_target_profile_ballistic_review_verified`. Wave1067 re-read the destructable-controller lookup/damage bridge tying `CUnit__ApplyDamage`, `CUnit__ApplyRandomDestructibleDamageBurst`, `CUnit__VFunc26_GetRecentSegmentDamageMeter`, `CUnit__GetCurrentHealthOrSubtreeHealth`, `CUnit__GetRootSubtreeHealthIfAnyActive`, and `CUnit__MarkDestroyedAndCleanupLinks` back into the `CDestructableSegmentsController__*` damage/health/cascade helpers. Wave1048 re-read the CUnit tail linked-vfunc cluster with no mutation, confirming `0x004fce40 CUnit__ForwardAttachedNodeVFunc14IfPresent`, `0x004fce80 CUnit__ForwardAttachedNodeVFunc18IfPresent`, `0x004fcec0 CUnit__ForwardAttachedNodeVFunc1CIfPresent`, `0x004fd5e0 CUnit__VFunc26_GetRecentSegmentDamageMeter`, `0x004fd6a0 CUnit__VFunc22_ActivateLinkedTargetsAndChildren`, and `0x004fd700 CUnit__VFunc23_DeactivateLinkedTargetsAndChildren` against fresh metadata/tags/xrefs/instructions/decompile/vtable evidence. Wave1024 re-read the CUnit attached-node forwarding context for CUnitAI door-wing engagement, keeping `0x004fce40 CUnit__ForwardAttachedNodeVFunc14IfPresent` and `0x004fcec0 CUnit__ForwardAttachedNodeVFunc1CIfPresent` under CUnit ownership while CUnitAI door-wing rows stayed in [`UnitAI.cpp`](../UnitAI.cpp/_index.md). Wave830 adds saved static read-back evidence for the CUnit-family vtable slot 64 configured-pickup bridge. Wave835 CUnit ApplyDamage adds saved signature/comment/tag evidence for important shared CUnit damage/lifetime infrastructure at `0x004f9a90 CUnit__ApplyDamage`. Wave836 CUnit Smooth Euler adds saved signature/comment/tag evidence for important shared CUnit motion/orientation infrastructure at `0x004fa4b0 CUnit__SmoothEulerTowardTargetAndBuildMatrix`. Wave837 CUnit Spawn Cooldown corrects stale `CSpawnerThng__SetCooldownState3` metadata to `0x004fc3a0 CUnit__SetSpawnCooldownState3`. Wave838 Unit Attached Node Forwarders corrects/refines three adjacent attached-node/controller forwarding helpers at `0x004fce40`, `0x004fce80`, and `0x004fcec0`.

Wave1154 (`wave1154-unitai-deploy-target-current-risk-review`) re-read the UnitAI deploy/undeploy animation tail with fresh Ghidra evidence and no mutation: `CUnitAI__PlayDeployingAnimationIfState0`, `CUnitAI__PlayUndeployingAnimation`, and `CUnitAI__HandleDeployUndeployAnimationCompletion`. Static evidence keeps these rows tied to the deploy-state animation offsets and the existing `CUnitAI__HandleDeployAndFireAnimationCompletion` neighborhood; runtime deploy/undeploy AI behavior, exact CUnitAI layout, gameplay outcomes, visual QA, and rebuild parity remain separate proof. Verified backup: `G:\GhidraBackups\BEA_20260605-215410_post_wave1154_unitai_deploy_target_current_risk_review_verified`.

Wave1133 (`wave1133-feature-pickup-current-risk-review`) re-read the Unit-side pickup row `0x004fd230 CUnit__SpawnProfileDropPickup` as a primary row and `0x004ef100 CUnit__VFunc64_SpawnConfiguredPickupThreeTimes` as context. `0x004fd230` remains tied to AirUnit support/crash xrefs, `CUnit__ResetDeploymentGraphAndScheduleEvent`, profile field `this+0x164`, height delta gate `HeightDelta__Below025_D0`, and `CWorldPhysicsManager__CreatePickup` with profile field `+0xe8`. `0x004ef100` was already accounted by Wave1120 and remains the CUnit-family slot-64 wrapper that loops three calls to `CUnit__SpawnConfiguredPickupIfAboveWater`, so Wave1133 treats it as context only. Wave1133 covers `6 rows`; current focused accounting is `184/1179 = 15.61%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 995; static debt remains `0 / 0 / 0`; the wave is a read-only review with no mutation. Verified backup: `G:\GhidraBackups\BEA_20260605-100620_post_wave1133_feature_pickup_current_risk_review_verified`. Runtime Unit pickup/drop behavior, exact concrete Unit/profile/pickup layouts, exact source virtual names, gameplay outcomes, BEA patching, visual QA, and rebuild parity remain separate proof.

Wave1132 (`wave1132-component-ai-current-risk-review`) re-read and tag-normalized the component/active-reader UnitAI residual cluster with fresh Ghidra export evidence and no rename, signature, comment, function-boundary, or executable-byte change. The Unit/UnitAI-facing anchors are `0x00428710 CUnitAI__GetRenderPosFromActorOrCache`, `0x00428770 CUnitAI__GetRenderOrientationFromActorOrCache`, `0x00428c70 CUnitAI__RunSharedStepAndMaybeTriggerFlag4Action`, `0x00428d50 CUnitAI__PlayActivateAnimationOrFinalizeActivated`, and `0x00428e80 CComponentAI__ClearReaderIfTargetDestroyedThenForward`; related Component anchors are `0x00427b80 CComponent__VFunc_09_00427b80`, `0x00427f90 CComponentBomberAI__scalar_deleting_dtor`, `0x00427fb0 CComponentBomberAI__dtor_base`, `0x00428050 CFenrirMainGunAI__scalar_deleting_dtor`, and `0x00428070 CFenrirMainGunAI__dtor_base`. Wave1132 covers `10 rows`; current focused accounting is `178/1179 = 15.10%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 1001; static debt remains `0 / 0 / 0`; the wave is the component/active-reader UnitAI residual cluster; fresh Ghidra export; tag-only normalization; 91 tags. Verified backup: `G:\GhidraBackups\BEA_20260605-093432_post_wave1132_component_ai_current_risk_review_verified`; previous completed backup: `G:\GhidraBackups\BEA_20260605-090018_post_wave1131_heightfield_current_risk_review_verified`. Runtime Component/UnitAI behavior, exact layouts, BEA patching, gameplay outcomes, visual QA, and rebuild parity remain separate proof.

Wave1119 (`wave1119-mixed-score26-current-risk-review`) re-read two Unit-family current-risk anchors with a fresh read-only Ghidra export and no mutation: `0x004fc3c0 SharedUnitVFunc__ResolveField17cVectorContext_004fc3c0` and `0x0050ee90 CUnit__scalar_deleting_dtor`. Fresh DATA xrefs keep `0x004fc3c0` tied to broad unit-family vtable slots including `0x005d8fe0`, while its body checks the `this+0x17c` list and falls back to attachment/origin plus orientation-matrix copies. Fresh DATA xrefs keep `0x0050ee90` tied to unit-family scalar-deleting destructor slots including `0x005dfd40`, with the `CUnit__dtor_base_Thunk_004bfe00` and `CDXMemoryManager__Free` cleanup wrapper intact. Current focused accounting moves to `110/1179 = 9.33%`; verified backup: `G:\GhidraBackups\BEA_20260605-022812_post_wave1119_mixed_score26_current_risk_review_verified`. Runtime unit behavior, exact concrete layouts, exact source virtual names, gameplay outcomes, BEA patching, and rebuild parity remain separate proof.

Wave1121 (`wave1121-mixed-score24-current-risk-review`) re-read `0x004037a0 SharedUnitVFunc__ApplyDamageAndResolveSlot19Vector_004037a0` as part of the score-24 mixed current-risk head. The saved Wave1086 name/signature/comment remain coherent: DATA refs come from shared unit-family vtables, the body forwards to `CUnit__ApplyDamage`, dispatches selector `0x19` through vtable slot `+0x160`, and returns with `RET 0x10`. Wave1121 made no Unit.cpp mutation. Current focused accounting moves to `122/1179 = 10.35%`; verified backup: `G:\GhidraBackups\BEA_20260605-033658_post_wave1121_mixed_score24_current_risk_review_verified`. Runtime damage behavior, exact concrete layouts, exact source virtual names, gameplay outcomes, BEA patching, and rebuild parity remain separate proof.

Wave1127 (`wave1127-mixed-score23-current-risk-review`) re-read and tag-normalized `0x004f9260 SharedUnitVFunc__BuildField164TargetVectorContext_004f9260` as a score-23 current-risk row. Fresh evidence keeps the saved Wave1083 name/signature/comment coherent: DATA refs come from shared unit-family vtables, the body builds context around `this+0x164`, references target/world state including `DAT_008553f8`, and ties into the same broader unit-family target-context surface as `CUnit__ApplyRandomDestructibleDamageBurst` and `CWorldPhysicsManager__CreatePickup` contexts. Wave1127 added tags only; no rename, signature, comment, function-boundary, or executable-byte change was made. Verified backup: `G:\GhidraBackups\BEA_20260605-071212_post_wave1127_mixed_score23_current_risk_review_verified`. Runtime unit target-context behavior, exact concrete layouts, exact source virtual names, gameplay outcomes, BEA patching, and rebuild parity remain separate proof.

Wave1120 (`wave1120-mixed-score25-current-risk-review`) re-read two Unit-family current-risk anchors with a fresh read-only Ghidra export and no mutation: `0x004bfe00 CUnit__dtor_base_Thunk_004bfe00` and `0x004ef100 CUnit__VFunc64_SpawnConfiguredPickupThreeTimes`. Fresh xrefs keep `0x004bfe00` as the jump thunk to `CUnit__dtor_base` reached by unwind cleanup and scalar-deleting destructor paths. DATA xref `0x005e1610` keeps `0x004ef100` tied to the CUnit-family slot-64 configured-pickup wrapper, whose body loops three calls to `CUnit__SpawnConfiguredPickupIfAboveWater`. Current focused accounting moves to `118/1179 = 10.01%`; verified backup: `G:\GhidraBackups\BEA_20260605-025952_post_wave1120_mixed_score25_current_risk_review_verified`. Runtime unit cleanup/pickup behavior, exact concrete layouts, exact source virtual names, gameplay outcomes, BEA patching, and rebuild parity remain separate proof.

Wave1097 (`cunit-dtor-thunk-lifecycle-review-wave1097`) keeps the CUnit cleanup graph read-only and source-bounded. Fresh exports verified `12` metadata rows, `12` tag rows, `190` xref rows, `656` instruction rows, and `12` decompile rows. `0x004bfe00 CUnit__dtor_base_Thunk_004bfe00` is a jump thunk to `0x004f84e0 CUnit__dtor_base`; `0x004f84c0 CUnit__VFunc01_ScalarDeletingDtor` and `0x0050ee90 CUnit__scalar_deleting_dtor` both call the base destructor path and optionally free through `CDXMemoryManager__Free`; `0x004f95d0 CUnit__VFunc02_CleanupWorldLinksAndForward` remains the slot-2 world-link cleanup/forward path; `0x004fcfa0 CUnit__ClearSpawnerSet`, `0x004fcfe0 CUnit__ReleaseChildUnits`, `0x004fd040 CUnit__ResetDeploymentGraphAndScheduleEvent`, and `0x004fd140 CUnit__MarkDestroyedAndCleanupLinks` preserve the active-reader, child-unit, deployment-event, and destroyed-state cleanup map; `0x004cb0b0 ParticleEffectLink__SetHandleStateAndClear` remains a shared owner-link cell helper; and the destructor tail reaches `0x004013d0 CActor__dtor_base` then `0x004f3f00 CComplexThing__dtor_base`. Queue closure remains `6410/6410 = 100.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface progress remains `1560/1560 = 100.00%`; top-500 coverage remains `500/500 = 100.00%`. Runtime destruction, cleanup order, event scheduling, child-unit release, particle/effect behavior, exact CUnit/CActor/CComplexThing/reader/set/owner-link/controller/script layouts, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1097; cunit-dtor-thunk-lifecycle-review-wave1097; 0x004bfe00 CUnit__dtor_base_Thunk_004bfe00; 0x004f84c0 CUnit__VFunc01_ScalarDeletingDtor; 0x004f84e0 CUnit__dtor_base; 0x0050ee90 CUnit__scalar_deleting_dtor; 0x004f95d0 CUnit__VFunc02_CleanupWorldLinksAndForward; 0x004fcfa0 CUnit__ClearSpawnerSet; 0x004fcfe0 CUnit__ReleaseChildUnits; 0x004fd040 CUnit__ResetDeploymentGraphAndScheduleEvent; 0x004fd140 CUnit__MarkDestroyedAndCleanupLinks; 0x004cb0b0 ParticleEffectLink__SetHandleStateAndClear; 0x004013d0 CActor__dtor_base; 0x004f3f00 CComplexThing__dtor_base; 1560/1560 = 100.00%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; G:\GhidraBackups\BEA_20260604-182217_post_wave1097_cunit_dtor_thunk_lifecycle_review_verified; read-only review.

Wave1075 (`cunit-vfunc08-boundary-wave1075`) saved the recovered CUnit-family vtable slot-8 boundary as `void __thiscall CUnit__VFunc08_InitAndAddToWorld(void * this, void * init)` with `cunit-vfunc08-boundary-wave1075` and `wave1075-readback-verified` tags. Fresh evidence ties CUnit-family vtable table `0x005dfd40` slot 8 / slot address `0x005dfd60` to the body; pre-state had `0x004dfa40` and `0x004dfa47` as `INSTRUCTION_NO_FUNCTION`, and `0x004dfa47` has no direct xref. Post read-back verified body end `0x004dfa9a`, next-function boundary `0x004dfaa0`, `CUnit__Init`, and `CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk`. Queue closure is `6248/6248 = 100.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface progress advances to `1359/1560 = 87.12%`; top-500 remains `500/500 = 100.00%`. Exact source virtual name, concrete CUnit/init/world-layout semantics, runtime init/add-to-world/static-shadow behavior, BEA patching, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1075; cunit-vfunc08-boundary-wave1075; 0x004dfa40 CUnit__VFunc08_InitAndAddToWorld; 0x005dfd40; 0x005dfd60; 0x004dfa47; 0x004dfa9a; 0x004dfaa0; CUnit__Init; CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk; 812/1408 = 57.67%; 1359/1560 = 87.12%; 500/500 = 100.00%; 6248/6248 = 100.00%; G:\GhidraBackups\BEA_20260602-060358_post_wave1075_cunit_vfunc08_boundary_verified; boundary recovery.

Wave1072 (`oid-target-profile-ballistic-review-wave1072`) keeps the Unit-side ballistic support rows read-only: `0x005096a0 CUnit__ComputeMinBallisticTravelDistance`, `0x005099a0 CUnit__ComputeMaxBallisticTravelDistance`, `0x0050a0d0 CUnit__HasMaskBitsA8`, and `0x0050a290 CUnit__IsTargetTimeoutBeforeProfileLimit` remain coherent with the OID ballistic and target-profile rows. Fresh primary exports verified `15/15/40/2997/15` rows and context exports verified `16/70/1769/16` rows. Queue closure remains `6246/6246 = 100.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface progress advances to `1334/1560 = 85.51%`; top-500 coverage remains `500/500 = 100.00%`. Runtime targeting/projectile/weapon behavior, exact Unit/target-profile layouts, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

Wave1067 (`destructable-controller-lookup-damage-review-wave1067`) primary destructable-controller anchors include `0x00443fc0 CDestructableSegmentsController__Ctor`, `0x00444030 CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold`, `0x00444160 CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold`, `0x004442d0 CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex`, `0x00444300 CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex`, `0x004443f0 CDestructableSegmentsController__TriggerCoreCascadeIfEligible`, `0x00444450 CDestructableSegmentsController__SetSegmentField0CByName`, `0x00444520 CDestructableSegmentsController__FindSegmentByName`, `0x004445b0 CDestructableSegmentsController__SetSegmentActiveFlagByName`, and `0x00444620 CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric`. Fresh primary/context exports verified `16/16/17/590/16` and `20/20/142/1757/20` rows; queue closure remains `6246/6246 = 100.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface progress advances to `1248/1560 = 80.00%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260602-003225_post_wave1067_destructable_controller_lookup_damage_review_verified`. Runtime destructable-controller/CUnit damage, health-meter, cascade, and name-dispatch behavior remains separate proof. Probe token anchor: Wave1067; destructable-controller-lookup-damage-review-wave1067; 0x00443fc0 CDestructableSegmentsController__Ctor; 0x00444030 CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold; 0x00444160 CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold; 0x004442d0 CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex; 0x00444300 CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex; 0x004443f0 CDestructableSegmentsController__TriggerCoreCascadeIfEligible; 0x00444450 CDestructableSegmentsController__SetSegmentField0CByName; 0x00444520 CDestructableSegmentsController__FindSegmentByName; 0x004445b0 CDestructableSegmentsController__SetSegmentActiveFlagByName; 0x00444620 CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric; 812/1408 = 57.67%; 1248/1560 = 80.00%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260602-003225_post_wave1067_destructable_controller_lookup_damage_review_verified; read-only review.

Wave906 (`unit-battleengine-gameplay-static-review-wave906`) records a `static-coherent Unit/BattleEngine/gameplay core` after export-contract queue closure `6113/6113 = 100.00%` (static review slice only): `633` rows across `75` families, including `CUnit` `90`, `CUnitAI` `63`, `CBattleEngine` `47`, `CSquadNormal` `31`, `CBattleEngineWalkerPart` `27`, `CBattleEngineJetPart` `23`, `CGeneralVolume` `23`, `CDestructableSegmentsController` `19`, and `CCollisionSeekingRound` `17`; anchors include `CUnit__ApplyDamage`, `CUnitAI__UpdateActivationStateAndSpawnPickup`, `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`, `CBattleEngine__AddProjectile`, `CBattleEngine__Morph`, `CBattleEngine__HandleCloak`, `CBattleEngine__AugmentWeapon`, `CBattleEngineJetPart__WeaponFired`, `CBattleEngineWalkerPart__WeaponFired`, `CWeapon__HandleFireBurstEvent`, `CRound__SpawnConfiguredProjectile`, `CSpawnerThng__DoSpawn`, and `CDestroyableSegment__VFunc_03_ApplyDamage`. Verified backup: `G:\GhidraBackups\BEA_20260526-105331_post_wave906_unit_battleengine_gameplay_static_review_verified`.

Wave927 (`cunit-active-reader-targeting-review-wave927`) re-reviewed the CUnit/CUnitAI active-reader targeting bridge with fresh read-only exports. Primary focused candidates were `0x00428b50 CUnit__SetReaderAndComputeRelativeYaw`, `0x00428bc0 CUnitAI__GetTargetHeadingWithOffset`, `0x00429270 CUnitAI__UpdateHeadingTowardTargetClamped`, `0x004e97e0 CGenericActiveReader__SwapWithCandidateIfFormationCloser`, and `0x004fd3d0 CUnit__IsCandidateSideCompatibleForTargeting`; context helper `0x004fb650 CUnit__ForwardAimTransformAndAttachTargetReader` confirmed the Wave523 aim/reader forwarding bridge. Evidence counts: 5 metadata rows, 5 tag rows, 23 xref rows, 464 instruction rows, and 5 decompile rows for primary targets; 1 metadata row, 1 tag row, 13 xref rows, 9 instruction rows, and 1 decompile row for context. No mutation was needed. Wave911 focused re-audit progress after Wave927 is `103/1408 = 7.32%`; export-contract closure remains `6113/6113 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260527-223748_post_wave927_cunit_active_reader_targeting_review_verified`. Runtime targeting/steering/formation behavior, exact CUnit/CUnitAI/active-reader layouts, exact source-body identity, and rebuild parity remain separate proof.

Wave938 (`cunitai-activation-lifecycle-review-wave938`) re-reviewed the CUnitAI activation/lifecycle cluster and pulled shared CUnit lifecycle helpers into context. Primary CUnitAI targets were `0x00428110 CUnitAI__UpdateActivationStateAndSpawnPickup`, `0x00428500 CUnitAI__RefreshCachedComponentTransform`, `0x00428800 CUnitAI__HandleTriggerEventAndMoveToOffset`, `0x004289b0 CUnitAI__AdvanceActivationAnimationState`, and `0x00428cb0 CUnitAI__PlayHitAnimationAndSetFlag`; CUnit/CUnitAI context anchors were `0x00428d50 CUnitAI__PlayActivateAnimationOrFinalizeActivated`, `0x00428b50 CUnit__SetReaderAndComputeRelativeYaw`, `0x004fa8d0 CUnit__UpdateMotionAttachmentsAndEffects`, `0x004fcfe0 CUnit__ReleaseChildUnits`, `0x004fd040 CUnit__ResetDeploymentGraphAndScheduleEvent`, and `0x004fd140 CUnit__MarkDestroyedAndCleanupLinks`. Fresh xrefs tie `CUnitAI__HandleTriggerEventAndMoveToOffset` to `CUnit__MarkDestroyedAndCleanupLinks`, `CUnit__ResetDeploymentGraphAndScheduleEvent`, and `CUnit__ReleaseChildUnits`, while `CUnitAI__UpdateActivationStateAndSpawnPickup` reaches `CUnit__UpdateMotionAttachmentsAndEffects` and cached transform refresh. Evidence counts: 5 primary metadata rows, 5 primary tag rows, 11 primary xref rows, 726 primary instruction rows, 5 primary decompile rows; 6 context metadata rows, 6 context tag rows, 35 context xref rows, 964 context instruction rows, and 6 context decompile rows. No mutation was needed. Wave911 focused re-audit progress after Wave938 is `166/1408 = 11.79%`; export-contract closure remains `6113/6113 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260528-021545_post_wave938_cunitai_activation_lifecycle_review_verified`. Runtime activation, pickup, trigger, movement, destruction/deploy event behavior, exact CUnit/CUnitAI layouts, exact source-body identity, and rebuild parity remain separate proof.

Wave1024 (`cunitai-doorwing-context-review-wave1024`) re-reviewed the CUnit attached-node forwarders used by the CUnitAI door-wing engagement helpers as context: `0x004fce40 CUnit__ForwardAttachedNodeVFunc14IfPresent` and `0x004fcec0 CUnit__ForwardAttachedNodeVFunc1CIfPresent`. Fresh xrefs tie `0x004fce40` to `0x0044610a CUnitAI__UpdateDoorWingEngagement_MidRange` and tie `0x004fcec0` to `0x00445db5 CUnitAI__UpdateDoorWingEngagement_CloseRange`, `0x0044626e CUnitAI__UpdateDoorWingEngagement_LongRange`, and `0x00446472 CUnitAI__EnterDoorWingOpenTrackingState`. No mutation was needed. Verified backup: `G:\GhidraBackups\BEA_20260601-001008_post_wave1024_cunitai_doorwing_context_review_verified`. Runtime door-wing engagement/attached-node behavior, exact attached-node/controller type, exact argument layout beyond observed stack slots, and rebuild parity remain separate proof.

Wave943 (`unit-weapon-gameplay-review-wave943`) re-reviewed the Unit/CWeapon gameplay bridge as a read-only review. The CUnit-side targets were `0x004f6fd0 CUnit__RenderWithDistanceFade`, `0x004fd230 CUnit__SpawnProfileDropPickup`, and `0x0050ee90 CUnit__scalar_deleting_dtor`, with lifecycle context `0x004bfe00 CUnit__dtor_base_Thunk_004bfe00` and `0x004f84e0 CUnit__dtor_base`. The same evidence pass also pulled in the CWeapon bridge rows `0x00505e00 CWeapon__ctor_base`, `0x005061f0 CWeapon__DoesTargetMaskMatchDistanceProfile`, `0x005068f0 CWeapon__AdvanceChargeProgressIfAnySlotAssigned`, context helper `0x00505f90 CWeapon__DetachFromSetAndShutdownMonitor`, and vtable snapshots `0x005dfc94` and `0x005e1510` so the Unit destructor/render/pickup rows stayed tied to their weapon/targeting surroundings. No mutation, rename, signature change, comment change, function-boundary change, or executable-byte change was needed. Evidence counts: 6 primary metadata rows, 6 primary tag rows, 37 xref rows, 394 instruction rows, and 6 decompile rows; 15 context metadata rows, 15 context tag rows, 133 context xref rows, 1171 context instruction rows, 15 context decompile rows, and 192 vtable rows. Wave911 focused re-audit progress after Wave943 is `186/1408 = 13.21%`; export-contract closure remains `6113/6113 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260528-043815_post_wave943_unit_weapon_gameplay_review_verified`. Runtime render fade, pickup/drop, weapon targeting, weapon charge/fire behavior, exact layouts, source-body identity, and rebuild parity remain separate proof.

Wave977 (`configured-pickup-bridge-review-wave977`) re-reviewed the configured-pickup bridge as a read-only review. The focused target was `0x004ef100 CUnit__VFunc64_SpawnConfiguredPickupThreeTimes`, with context through `CUnit__SpawnConfiguredPickupIfAboveWater`, `CUnit__SpawnProfileDropPickup`, `CUnitAI__UpdateActivationStateAndSpawnPickup`, `CGeneralVolume__SpawnPickupAndDispatch`, `CDestroyableSegment__SpawnConfiguredPickup`, `CDestroyableSegment__VFunc_09_UpdatePickupAndChildSlot09`, and `CWorldPhysicsManager__CreatePickup`. Fresh exports verified `8` metadata rows, `8` tag rows, `85` xref rows, `960` instruction rows, and `8` decompile rows. No mutation was needed. Runtime pickup/drop behavior, exact source virtual names, concrete Unit/profile/init/pickup layouts, BEA patching, and rebuild parity remain separate proof.

Wave928 (`cunitai-deploy-state-review-wave928`) re-reviewed the CUnitAI deploy/lifecycle state quintet with fresh read-only exports. Primary focused candidates were `0x00415140 CUnitAI__HandleLandedStateTransition`, `0x00415780 CUnitAI__PlayDeployingAnimationIfState0`, `0x004157c0 CUnitAI__PlayUndeployingAnimation`, `0x00415970 CUnitAI__HandleDeployUndeployAnimationCompletion`, and `0x00415a50 CUnitAI__CanCompleteDeployUndeployTransition`; context helper `0x004fdeb0 CUnitAI__HandleDeployAndFireAnimationCompletion` confirmed the fallback completion path and kept its separate `+0x244` animation state distinct from the deploy-state `+0x260` helpers. Evidence counts: 5 metadata rows, 5 tag rows, 5 xref rows, 168 instruction rows, and 5 decompile rows for primary targets; 1 metadata row, 1 tag row, 21 xref rows, 144 instruction rows, and 1 decompile row for context. No mutation was needed. Wave911 focused re-audit progress after Wave928 is `108/1408 = 7.67%`; export-contract closure remains `6113/6113 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260527-225215_post_wave928_cunitai_deploy_state_review_verified`. Runtime deploy/undeploy AI behavior, exact CUnitAI field names/layout, exact animation table structure, exact source-body identity, and rebuild parity remain separate proof.

Wave929 (`cunitai-doorwing-animation-review-wave929`) re-reviewed the CUnitAI open/close animation focused trio with fresh read-only exports and tightened the door-wing boundary. Primary focused candidates were `0x00445570 CUnitAI__PlayOpenAnimationIfState1Or3`, `0x004455c0 CUnitAI__PlayCloseAnimationIfState0Or2`, and `0x00445610 CUnitAI__AdvanceOpenCloseShootAnimationState`; context helpers `0x00445ad0 CUnitAI__UpdateDoorWingEngagement_CloseRange`, `0x00445f40 CUnitAI__UpdateDoorWingEngagement_MidRange`, `0x00446150 CUnitAI__UpdateDoorWingEngagement_LongRange`, and `0x00446400 CUnitAI__EnterDoorWingOpenTrackingState` confirmed the close-range, long-range, mid-range, and open-tracking surrounding paths. Evidence counts: 3 metadata rows, 3 tag rows, 5 xref rows, 121 instruction rows, and 3 decompile rows for primary targets; 4 metadata rows, 4 tag rows, 4 xref rows, 770 instruction rows, and 4 decompile rows for context; 1 metadata/tag/xref/decompile row and 100 instruction rows for comparison target `0x00447fa0 CUnitAI__AdvanceDoorWingAnimationState`; and 256 vtable-slot rows across `0x005e11b0` and `0x005e1e7c`. String dumps verified `0x00623bb4=open`, `0x006289e4=close`, `0x006289ec=shoot`, and `0x0062359c=fly`. The vtable comparison keeps `0x00445610` at `0x005e11b0` slot `94` separate from `0x00447fa0` at `0x005e1e7c` slot `18`; fresh evidence does not merge the `+0x280` open/close/shoot helper with the broader `+0x27c` door/wing animation state machine. No mutation was needed. Wave911 focused re-audit progress after Wave929 is `111/1408 = 7.88%`; export-contract closure remains `6113/6113 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260527-231046_post_wave929_cunitai_doorwing_animation_review_verified`. Runtime door-wing animation/targeting behavior, exact CUnitAI field names/layout beyond observed offsets, exact source-body identity, whether `0x00445610` and `0x00447fa0` share higher-level runtime state-machine ownership, and rebuild parity remain separate proof.

Wave930 (`cunitai-doorwing-state-review-wave930`) re-reviewed the CUnitAI `+0x27c` door-wing state focused quintet with fresh read-only exports while keeping cached-anchor helpers context-only. Primary focused candidates were `0x00447a40 CUnitAI__SetDoorWingState2AndClampYawDelta`, `0x00447ac0 CUnitAI__PlayWingFoldedAnimationAndSetState3`, `0x00447fa0 CUnitAI__AdvanceDoorWingAnimationState`, `0x00448110 CUnitAI__SetDoorWingState6`, and `0x00448120 CUnitAI__SetDoorWingState7AndMirrorYawOffset`; context helpers `0x00447b10 CUnitAI__PlayWingUnfoldedAnimationAndSetState5`, `0x00447b60 CUnitAI__HasReachedCachedAnchorPoint`, `0x00447bb0 CUnitAI__GetOrGenerateCachedAnchorPoint`, `0x00447d50 CUnitAI__IsCachedAnchorPointValid`, and `0x004480c0 CUnitAI__CanContinueDoorWingTransition` covered the adjacent wing-unfolded, cached-anchor, and transition-predicate path. Evidence counts: 5 metadata rows, 5 tag rows, 5 xref rows, 164 instruction rows, and 5 decompile rows for primary targets; 5 metadata rows, 5 tag rows, 7 xref rows, 355 instruction rows, and 5 decompile rows for context; 1 metadata/tag/xref/decompile row and 73 instruction rows for comparison target `0x00445610 CUnitAI__AdvanceOpenCloseShootAnimationState`; and 256 vtable-slot rows across `0x005e11b0` and `0x005e1e7c`. String dumps verified `0x00628a98=dooropening`, `0x00628a8c=doorclosing`, `0x00628a80=doorclosed`, `0x00628aa4=wingfolded`, `0x00628ab0=wingunfolded`, `0x00628a74=wingflat`, `0x00628ac0=dooropen`, plus comparison strings `open`, `close`, `shoot`, and `fly`. No mutation was needed. Wave911 focused re-audit progress after Wave930 is `116/1408 = 8.24%`; export-contract closure remains `6113/6113 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260527-233937_post_wave930_cunitai_doorwing_state_review_verified`. Runtime door-wing behavior, exact CUnitAI field names/layout beyond observed address-qualified offsets, exact source-body identity, a unified door-wing animation/state FSM spanning `0x00445610` and `0x00447fa0`, and rebuild parity remain separate proof.

## Wave1048 CUnit Tail Linked-VFunc Review

Wave1048 (`cunit-tail-linked-vfunc-review-wave1048`) re-read six CUnit tail helpers with no mutation: `0x004fce40 CUnit__ForwardAttachedNodeVFunc14IfPresent`, `0x004fce80 CUnit__ForwardAttachedNodeVFunc18IfPresent`, `0x004fcec0 CUnit__ForwardAttachedNodeVFunc1CIfPresent`, `0x004fd5e0 CUnit__VFunc26_GetRecentSegmentDamageMeter`, `0x004fd6a0 CUnit__VFunc22_ActivateLinkedTargetsAndChildren`, and `0x004fd700 CUnit__VFunc23_DeactivateLinkedTargetsAndChildren`. Fresh primary exports verified `6` metadata rows, `6` tag rows, `116` xref rows, `175` function-body instruction rows, and `6` decompile rows; context exports verified `10` metadata rows, `10` tag rows, `78` xref rows, `596` function-body instruction rows, and `10` decompile rows; vtable export verified `4` vtable anchors and `528` slot rows. Vtable confirmations include `0x005d8d1c` slot `98` -> `0x004fd5e0`, slot `124` -> `0x004fd6a0`, slot `125` -> `0x004fd700`, plus `0x005e0b30`, `0x005e297c`, and `0x005e32d4` slots `22`/`23` pointing at the activation/deactivation helpers. The recent-damage meter remains tied to `CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex` and `CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex`; activation/deactivation remains tied to linked target/reader dispatch through `+0x58` / `+0x5c`. Queue closure is `6246/6246 = 100.00%`; Wave911 focused progress is `744/1408 = 52.84%`; expanded static surface progress is `1002/1509 = 66.40%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260601-131919_post_wave1048_cunit_tail_linked_vfunc_review_verified`. Runtime activation/deactivation behavior, linked-reader side effects, recent segment-damage meter behavior, exact `CUnit` / attached-node / linked-reader / destructible-segment layouts, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1048; cunit-tail-linked-vfunc-review-wave1048; 0x004fce40 CUnit__ForwardAttachedNodeVFunc14IfPresent; 0x004fce80 CUnit__ForwardAttachedNodeVFunc18IfPresent; 0x004fcec0 CUnit__ForwardAttachedNodeVFunc1CIfPresent; 0x004fd5e0 CUnit__VFunc26_GetRecentSegmentDamageMeter; 0x004fd6a0 CUnit__VFunc22_ActivateLinkedTargetsAndChildren; 0x004fd700 CUnit__VFunc23_DeactivateLinkedTargetsAndChildren; CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex; CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex; 0x005d8d1c; 0x005e0b30; 0x005e297c; 0x005e32d4; 744/1408 = 52.84%; 1002/1509 = 66.40%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260601-131919_post_wave1048_cunit_tail_linked_vfunc_review_verified; no mutation.

## Wave838 Unit Attached Node Forwarders

Wave838 Unit Attached Node Forwarders (`unit-attached-node-forwarders-wave838`, `wave838-readback-verified`) saved three adjacent CUnit-tail attached-node/controller forwarding rows:

| Address | Saved name/signature | Static read-back evidence |
| --- | --- | --- |
| `0x004fce40` | `int __thiscall CUnit__ForwardAttachedNodeVFunc14IfPresent(void * this, int node_arg0, int node_arg1, int node_arg2, int node_arg3)` | Corrects stale `CUnitAI__CallAttachedNodeVFunc14IfPresent`; loads `this+0x208`, null-gates it, copies four stack dwords into a 16-byte call frame, dispatches vfunc `+0x14`, returns with `RET 0x10` at `0x004fce71`, and has xref `0x0044610a CUnitAI__UpdateDoorWingEngagement_MidRange`. |
| `0x004fce80` | `int __thiscall CUnit__ForwardAttachedNodeVFunc18IfPresent(void * this, int node_arg0, int node_arg1, int node_arg2, int node_arg3)` | Refines stale broad `CUnit__ForwardControllerQuery18`; uses the same `this+0x208` attached-node pattern, dispatches vfunc `+0x18`, returns with `RET 0x10` at `0x004fceb1`, and has static callers including `0x0047a38a`, `0x0048a113`, `0x004ef404`, `0x004fecda`, and `0x004feda1`. |
| `0x004fcec0` | `int __thiscall CUnit__ForwardAttachedNodeVFunc1CIfPresent(void * this, int node_arg0, int node_arg1, int node_arg2, int node_arg3)` | Corrects stale `CUnitAI__GetAttachedNodeReadyState`; uses the same `this+0x208` attached-node pattern, dispatches vfunc `+0x1c`, returns with `RET 0x10` at `0x004fcef1`, and has `CSquadNormal__BuildAttackFormation` xrefs at `0x004e8ba9/0x004e8c06` plus CUnitAI door-wing xrefs at `0x00445db5/0x0044626e/0x00446472`. |

Exact Wave838 anchors: `0x004fce40 CUnit__ForwardAttachedNodeVFunc14IfPresent`, `0x004fce80 CUnit__ForwardAttachedNodeVFunc18IfPresent`, and `0x004fcec0 CUnit__ForwardAttachedNodeVFunc1CIfPresent`.

Verified backup: `G:\GhidraBackups\BEA_20260525-021158_post_wave838_unit_attached_node_forwarders_verified`. Post-Wave838 strict clean-signature proxy is `5662/6098 = 92.85%`; next raw commentless row is `0x004fde70 CWarspite__TransitionToUndeploying`. This wave covers important CUnit connective/static infrastructure; exact attached-node/controller type, exact argument layout beyond four observed dword stack slots, return-value semantics, runtime behavior, BEA patching, and rebuild parity remain deferred.

## Wave837 CUnit Spawn Cooldown

Wave837 CUnit Spawn Cooldown (`cunit-spawn-cooldown-wave837`, `wave837-readback-verified`) corrected the saved Ghidra row at `0x004fc3a0` from stale `CSpawnerThng__SetCooldownState3` metadata to `CUnit__SetSpawnCooldownState3` with signature `void __thiscall CUnit__SetSpawnCooldownState3(void * this, float cooldown_delay)`. `RET 0x4` at `0x004fc3ba` and `FADD [ESP+0x4]` at `0x004fc3b0` prove one explicit float argument after the ECX receiver, replacing the old `int cooldown_ticks, float unused_scale` shape.

Static evidence ties the helper to sole caller `0x004e430f CSpawnerThng__ProcessSpawnWave`: after `CWorldPhysicsManager__CreateThingByType` and the spawned object's vfunc `+0x24` init, the caller sets `ECX` to the created object and pushes spawner config `+0x1c`. The callee writes state literal `3` to `this+0x168` and `DAT_00672fd0 + cooldown_delay` to `this+0x16c` as an absolute spawn-cooldown/ready-time value. Verified backup: `G:\GhidraBackups\BEA_20260525-013914_post_wave837_cunit_spawn_cooldown_verified`. Post-Wave837 strict clean-signature proxy is `5659/6098 = 92.80%`; next raw commentless row is `0x004fce40 CUnitAI__CallAttachedNodeVFunc14IfPresent`. Exact Unit.cpp source-body identity, exact state enum meaning, concrete CUnit field names/layout, runtime spawn activation/cooldown behavior, BEA patching, and rebuild parity remain deferred.

## Wave836 CUnit Smooth Euler

Wave836 CUnit Smooth Euler (`cunit-smooth-euler-wave836`, `wave836-readback-verified`) corrected the saved Ghidra signature for `0x004fa4b0 CUnit__SmoothEulerTowardTargetAndBuildMatrix` to `void __thiscall CUnit__SmoothEulerTowardTargetAndBuildMatrix(void * this, float * current_euler_xyz, float * target_euler_xyz, float * max_step_xyz, float * out_matrix3x4)`. `RET 0x10` at `0x004fa7fc` and the direct caller stub at `0x00428c15-0x00428c21` prove four explicit stack arguments after the ECX receiver. Thirty DATA slot refs point at the body, including `0x005d8af8`, `0x005d8fe8`, `0x005dd8bc`, `0x005dfacc`, `0x005e31a8`, and `0x005e38ac`.

This is important shared CUnit motion/orientation infrastructure with lower direct source-body evidence density, not low-importance code. Static evidence ties the body to `30 DATA` slot refs, receiver `vfunc +0x60`, constants including `0x005d85c0`, `0x005d85dc`, `0x005d85e0`, `0x005d85e4`, and `0x005d85e8`, per-axis Euler smoothing, angle wrapping across the +/- pi-like boundary, sin/cos generation, and twelve-float `out_matrix3x4` output. Verified backup: `G:\GhidraBackups\BEA_20260525-010821_post_wave836_cunit_smooth_euler_verified`. Post-Wave836 strict clean-signature proxy is `5658/6098 = 92.78%`; next raw commentless row was `0x004fc3a0 CSpawnerThng__SetCooldownState3`, later corrected by Wave837 to `CUnit__SetSpawnCooldownState3`. Exact Unit.cpp source-body identity, exact angle units, exact matrix row/column convention, concrete CUnit layout, runtime motion/orientation behavior, BEA patching, and rebuild parity remain deferred.

## Wave835 CUnit ApplyDamage

Wave835 CUnit ApplyDamage (`cunit-apply-damage-wave835`, `wave835-readback-verified`) corrected the saved Ghidra signature for `0x004f9a90 CUnit__ApplyDamage` to `void __thiscall CUnit__ApplyDamage(void * this, float damage_amount, void * damage_source, int apply_shields, int mesh_part_index)`. `RET 0x10` at `0x004fa4a7` and direct callsite pushes at `0x004037be`, `0x00417a16`, `0x0048006d`, and `0x004898b0` prove four explicit stack arguments after the ECX receiver. Nineteen DATA slot refs point at the body, including `0x005dd828`, `0x005dfa38`, `0x005e1530`, `0x005e3114`, and `0x005e4298`.

Static evidence ties the body to `19 DATA` slot refs, `CUnit__ResetDamageCooldownTimer`, profile/state damage scaling, health-like `this+0xf8`, shield-like `this+0x100`, nexus and weakpoint mesh-part gates using `s_nexus_00633af4` and `s_weakpoint_00633ae8`, destructible-segment forwarding, death/cleanup dispatch, particle effect creation, and profile/Tara/Billy damage text queued through `CMessageBox` with Unit.cpp debug allocation path `0x00633b6c`, line `0x44d`. Verified backup: `G:\GhidraBackups\BEA_20260525-003658_post_wave835_cunit_apply_damage_verified`. Post-Wave835 strict clean-signature proxy is `5657/6098 = 92.77%`; next raw commentless row is `0x004fa4b0 CUnit__SmoothEulerTowardTargetAndBuildMatrix`. Exact source body identity, concrete layouts, exact player/god-mode behavior, runtime damage/shield/death/message behavior, BEA patching, and rebuild parity remain deferred.

## Wave742 unwind continuation callbacks

Wave742 unwind continuation saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for the Unit/BattleEngine-adjacent cleanup callbacks from `0x005d1170 Unwind@005d1170` through `0x005d11d2 Unwind@005d11d2`. The saved comments record scope-table DATA xrefs `0x00619fcc` through `0x0061a004` and cleanup calls through `CSPtrSet__Clear`, `CGenericActiveReader__dtor`, and `CParticleManager__RemoveFromGlobalList_Thunk` on object fields `+0x2a4`, `+0x4c8`, `+0x4cc`, `+0x4e0`, `+0x574`, `+0x5e8`, `+0x5f8`, and `+0x620`. The full Wave742 tranche spans through `0x005d13b3 Unwind@005d13b3`; the wave also documents later pointer-set cleanup rows from `0x005d12c0 Unwind@005d12c0` through `0x005d1340 Unwind@005d1340`. The next high-signal queue row after the pass is `0x005d13d0 Unwind@005d13d0`, while the earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.

Tags include `unwind-continuation-wave742` and `wave742-readback-verified`; verified backup is `G:\GhidraBackups\BEA_20260522-153147_post_wave742_unwind_continuation_verified`. This is saved static retail Ghidra evidence only. Exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Wave759 unit/object unwind continuation callbacks

Wave759 unwind continuation saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for adjacent unit/object teardown callbacks from `0x005d3cc6 Unwind@005d3cc6` through `0x005d3d5a Unwind@005d3d5a`. The saved comments record DATA scope-table xrefs `0x0061c97c` through `0x0061c9d4` and cleanup calls through `CUnit__dtor_base`, `CSPtrSet__Clear`, `CGenericActiveReader__dtor`, and `CParticleManager__RemoveFromGlobalList_Thunk` on object fields `+0x250`, `+0x264`, `+0x284`, `+0x294`, `+0x2a4`, `+0x4c8`, `+0x4cc`, `+0x4e0`, `+0x574`, `+0x5e8`, and `+0x5f8`.

Tags include `unwind-continuation-wave759` and `wave759-readback-verified`; verified backup is `G:\GhidraBackups\BEA_20260523-130827_post_wave759_unwind_continuation_verified`. Exact anchors include `0x005d3cc6 Unwind@005d3cc6`, `0x005d3d14 Unwind@005d3d14`, and `0x005d3d5a Unwind@005d3d5a`. This is saved static retail Ghidra evidence only. Exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Wave769 Unit.cpp unwind continuation callbacks

Wave769 unwind continuation saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for the Unit.cpp allocation-cleanup callbacks `0x005d5500 Unwind@005d5500` and `0x005d5519 Unwind@005d5519`. DATA scope-table xrefs `0x0061ddb4` and `0x0061ddbc` point at the bodies; instruction/decompile evidence calls `OID__FreeObject_Callback` on `*(EBP-0x70)` and `*(EBP-0x6c)` with Unit.cpp debug path `0x00633b6c`, line tokens `0xc0` and `0x139`, and allocation/type value `0x61`.

Tags include `unwind-continuation-wave769` and `wave769-readback-verified`; verified backup is `G:\GhidraBackups\BEA_20260523-174151_post_wave769_unwind_continuation_verified`. This is saved static retail Ghidra evidence only. Exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Wave770 Unit.cpp unwind continuation callbacks

Wave770 unwind continuation saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for the continued Unit.cpp cleanup callbacks from `0x005d5532 Unwind@005d5532` through `0x005d560e Unwind@005d560e`, plus adjacent device-helper callbacks at `0x005d5630 Unwind@005d5630` and `0x005d5650 Unwind@005d5650`. DATA scope-table xrefs `0x0061ddc4` through `0x0061debc` point at the bodies.

Evidence includes Unit.cpp debug path `0x00633b6c`, `OID__FreeObject_Callback` rows with line tokens `0x15b`, `0x164`, `0x16f`, `0x44d`, and `0xc1b`, a stack-local `CLine__SetBaseVtable_00426360` cleanup at `0x005d5590 Unwind@005d5590`, `CMonitor__Shutdown` at `0x005d55f0 Unwind@005d55f0`, `CGenericActiveReader__dtor` at `0x005d55f8 Unwind@005d55f8`, `0x005d5603 Unwind@005d5603`, and `0x005d560e Unwind@005d560e`, and two bounded `DeviceObject__ctor_like_00512d50` jumps where exact helper semantics remain unproven. Tags include `unwind-continuation-wave770` and `wave770-readback-verified`; verified backup is `G:\GhidraBackups\BEA_20260523-180835_post_wave770_unwind_continuation_verified`. This is saved static retail Ghidra evidence only. Exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004dfa40 | CUnit__VFunc08_InitAndAddToWorld | Wave1075 recovered CUnit-family vtable slot-8 init/add-to-world boundary from table `0x005dfd40` slot `0x005dfd60`; body calls `CUnit__Init` and `CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk` | read-back documented |
| 0x004f84c0 | CUnit__VFunc01_ScalarDeletingDtor | Wave526 scalar-deleting destructor wrapper over `CUnit__dtor_base`; `RET 0x4` delete-flags argument | read-back documented |
| 0x004f86d0 | [CUnit__Init](./CUnit__Init.md) | Wave526 init-pointer signature correction; core Unit setup from `this` plus one `init` argument | read-back documented |
| 0x004f9430 | CUnit__ApplyRandomDestructibleDamageBurst | Wave526 ECX-only destructible damage-burst helper | read-back documented |
| 0x004f9490 | CUnit__SpawnConfiguredPickupIfAboveWater | Wave526 owner correction for profile-configured pickup spawn gated by water/height context | read-back documented |
| 0x004f95d0 | CUnit__VFunc02_CleanupWorldLinksAndForward | Wave526 cleanup wrapper that drains Unit links/effects/controllers before forwarding shutdown | read-back documented |
| 0x004f9820 | CUnit__HandleEvent | Wave526 `RET 0x4` event handler that forwards default cases to `CActor__HandleEvent` | read-back documented |
| 0x004f99b0 | CUnit__PlayRespawnVoiceCueIfAvailable | Wave526 ECX-only respawn voice-cue helper | read-back documented |
| 0x004f99f0 | CUnit__GetCurrentHealthOrSubtreeHealth | Wave526 x87 health/subtree-health query; stale non-Unit owner corrected | read-back documented |
| 0x004f9a40 | CUnit__GetRootSubtreeHealthIfAnyActive | Wave526 adjacent root/subtree health query | read-back documented |
| 0x004f9a60 | CUnit__RemoveLinkedObjectFromSpawnerSet | Wave526 `RET 0x4` linked-object removal helper for `this+0x18c` | read-back documented |
| 0x004f9a90 | [CUnit__ApplyDamage](./CUnit__ApplyDamage.md) | Wave835 `RET 0x10` damage/lifetime handler with damage source, shield flag, mesh-part index, segment forwarding, weakpoint/nexus gates, and message/effect dispatch | read-back documented |
| 0x004fa4b0 | CUnit__SmoothEulerTowardTargetAndBuildMatrix | Wave836 `RET 0x10` smooth-Euler/matrix helper over current/target/max-step/out-matrix buffers, 30 DATA slots, vfunc `+0x60`, angle wrapping, and twelve-float output | read-back documented |
| 0x004fa800 | CUnit__UpdateClosingAndUnshuttingState | Wave526 ECX-only closing/unshutting state helper | read-back documented |
| 0x004fa8d0 | CUnit__UpdateMotionAttachmentsAndEffects | Wave526 ECX-only motion attachment and effect-link maintenance helper | read-back documented |
| 0x004fc4e0 | [CUnit__UpdateTransform](./CUnit__UpdateTransform.md) | Wave524 emitter-transform/cache output helper; not a general movement/terrain update | read-back documented |
| 0x004fe030 | [CUnit__TriggerEffect](./CUnit__TriggerEffect.md) | Wave528 trigger/message helper with one `trigger_context` argument; older broad damage-effect wording corrected | read-back documented |
| 0x0040eeb0 | [CBattleEngine__FinishedPlayingCurrentAnimation](../BattleEngine.cpp/CBattleEngine__FinishedPlayingCurrentAnimation.md) | Superseded prior CUnit owner label; BattleEngine transition animation completion helper | read-back documented |
| 0x00428710 | CUnitAI__GetRenderPosFromActorOrCache | Wave 325 saved render-position virtual-slot signature/comment/tag state | read-back documented |
| 0x00428770 | CUnitAI__GetRenderOrientationFromActorOrCache | Wave 325 saved render-orientation virtual-slot signature/comment/tag state | read-back documented |
| 0x00428800 | CUnitAI__HandleTriggerEventAndMoveToOffset | Wave 325 saved trigger/event and movement-offset helper signature/comment/tag state | read-back documented |
| 0x00428500 | CUnitAI__RefreshCachedComponentTransform | Refreshes cached component transform state used by AI heading/activation updates | ~140 bytes |
| 0x004289b0 | CUnitAI__AdvanceActivationAnimationState | Advances AI activation animation state and returns transition result | ~528 bytes |
| 0x00428b50 | CUnit__SetReaderAndComputeRelativeYaw | Wave 325 saved active-reader setter / relative-yaw signature/comment/tag state | read-back documented |
| 0x00428bc0 | CUnitAI__GetTargetHeadingWithOffset | Computes target heading with runtime offset bias | ~704 bytes |
| 0x00428cb0 | CUnitAI__PlayHitAnimationAndSetFlag | Wave 325 corrected prior caller-derived ExplosionInitThing owner label | read-back documented |
| 0x00428d50 | CUnitAI__PlayActivateAnimationOrFinalizeActivated | Wave 325 corrected prior generic virtual-slot label | read-back documented |
| 0x00428e80 | CComponentAI__ClearReaderIfTargetDestroyedThenForward | Wave 325 corrected prior generic virtual-slot label using Component-AI vtable context | read-back documented |
| 0x00429270 | CUnitAI__UpdateHeadingTowardTargetClamped | Wave 325 boundary correction moved true entry from stale `0x00429280` to `0x00429270` | read-back documented |
| 0x004d36c0 | [CUnit__InitBallisticAimState](./CUnit__BallisticAimState.md) | Wave486 ballistic aim target-vector initialization and height sampling helper | read-back documented |
| 0x004d3730 | [CUnit__ComputeBallisticLaunchVelocity](./CUnit__BallisticAimState.md) | Wave486 ballistic launch-vector computation helper | read-back documented |
| 0x004d38c0 | CUnit__TryDestroyedCleanupAndResetDeploymentGraph | Wave455 corrected stale InfluenceMap owner label using vtable data xref context | read-back documented |
| 0x004e43d0 | CUnit__CanProvideSupportNow | Wave508 support/deploy readiness predicate over observed support profile and timing fields | read-back documented |
| 0x004e4420 | CUnit__IsInBlockedSupportState | Wave508 blocked support-state predicate used by Unit/UnitAI/CSquadNormal support paths | read-back documented |
| 0x004e4480 | CUnit__IsSupportTargetMaskCompatible | Wave508 corrected stale CSquadNormal ownership; checks CUnit support mask fields against `target+0x34` | read-back documented |
| 0x004e6660 | CUnit__ResetDamageCooldownTimer | Wave508 CUnit damage-cooldown timer reset helper reached from CUnit damage handling | read-back documented |
| 0x004e66e0 | CUnit__RenderWithIdentityWorldAndShadowProbe | Wave508 render wrapper using identity world matrix and static-shadow height sampling | read-back documented |
| 0x004eb9a0 | CUnit__InitDefaultTuningBlock | Wave543 ECX-only tuning-block default initializer over offsets `+0x00..+0x84`, reached by a raw thunk loading global `0x0083d248` | read-back documented |
| 0x004ef000 | CUnit__SetTransitionState1AndNotifyChildren | Wave512 transition helper: writes `this+0x250` from state `2`/`3` to `1`, then notifies children through vfunc `+0x5c` | read-back documented |
| 0x004ef050 | CUnit__SetTransitionState3_IfState0Or1 | Wave512 narrow transition-state setter: writes `this+0x250 = 3` only from prior state `0`/`1` | read-back documented |
| 0x004ef0f0 | CUnit__SetTransitionState2 | Wave512 narrow transition-state setter: writes `this+0x250 = 2` | read-back documented |
| 0x004ef100 | CUnit__VFunc64_SpawnConfiguredPickupThreeTimes | Wave830 CUnit-family vtable slot 64 helper that calls `CUnit__SpawnConfiguredPickupIfAboveWater` three times | read-back documented |
| 0x004f1220 | CUnit__GetSpeedScaleByFlag30C | Wave515 compact speed-scale selector: returns one of two global float constants based on `this+0x30c` | read-back documented |
| 0x004f6fd0 | CUnit__RenderWithDistanceFade | Wave545 one-argument render fade helper used by `OID__RenderWithState1BOverride`; writes a rounded temporary value to global `0x0063012c`, calls `CThing__Render`, restores `0x0063012c` to `0xff`, and returns handled/not-handled | read-back documented |
| 0x004fb280 | CUnit__UpdateFireControlYawAndQueueEvent | Wave523 fire-control pitch/yaw refresh plus event `0xfa1` scheduler; `RET 0x4` proves one explicit event-context argument | read-back documented |
| 0x004fb500 | CUnit__CanFireAtTarget_BallisticArcA | Wave523 ballistic firing gate A over target range classification, target height sampling, and active ballistic profile window | read-back documented |
| 0x004fb5a0 | CUnit__CanFireAtTarget_BallisticArcB | Wave523 ballistic firing gate B with alternate target-height path and one target argument | read-back documented |
| 0x004fb650 | CUnit__ForwardAimTransformAndAttachTargetReader | Wave523 owner correction from stale Warspite-specific label to generic CUnit-family `this+0x140` aim/reader forwarder | read-back documented |
| 0x004fb670 | CUnit__ClassifyTargetRangeBand | Wave523 range classifier returning `0` in range, `1` beyond range, and `2` invalid/too close | read-back documented |
| 0x004fbcb0 | CUnit__UpdateDeployStateAndChargeEffects | Wave524 deploy/support state helper over reader/profile state, profile sounds/effects, charge particles, and deploying animation dispatch | read-back documented |
| 0x004fc000 | CUnit__CanDeployNow | Wave524 deploy readiness predicate over blocked support candidates, profile flag `+0x110`, mounted unit state, and Wave554 `TargetProfileContext__IsEligibleByDistanceBucketOrRange` distance/range eligibility | read-back documented |
| 0x004fc220 | CUnit__SpawnComponentEffectsRecursive | Wave524 recursive component-effect spawner over profile effect handles, component handles, child units, and mesh-renderer basis refresh | read-back documented |
| 0x004fc3a0 | CUnit__SetSpawnCooldownState3 | Wave837 corrected stale spawner-owner label; spawned-object helper writes state literal `3` at `this+0x168` and `DAT_00672fd0 + cooldown_delay` at `this+0x16c`; sole xref from `0x004e430f CSpawnerThng__ProcessSpawnWave` | read-back documented |
| 0x004fc4e0 | [CUnit__UpdateTransform](./CUnit__UpdateTransform.md) | Wave524 emitter-transform/cache resolver that writes output position and basis buffers | read-back documented |
| 0x004fc6e0 | CUnit__FindEmitterIndexBySlotTag | Wave524 emitter slot-tag switch mapping `SpawnerA-E`, `WaypointA-E`, `Component`, `Engine`, `Trail`, `Smoke`, `Thruster`, `Doorstop`, `Activation`, and `Charge` names | read-back documented |
| 0x004fcdc0 | CUnit__SetCollisionAndDamageFlags | Wave525 `RET 0x4` helper that writes base collision/damage flags plus observed constants to `this+0x34` | read-back documented |
| 0x004fce40 | CUnit__ForwardAttachedNodeVFunc14IfPresent | Wave838 attached-node forwarder; corrects stale `CUnitAI__CallAttachedNodeVFunc14IfPresent`, loads `this+0x208`, dispatches attached-node vfunc `+0x14`, and returns with `RET 0x10` | read-back documented |
| 0x004fce80 | CUnit__ForwardAttachedNodeVFunc18IfPresent | Wave838 attached-node forwarder; refines stale broad `CUnit__ForwardControllerQuery18`, loads `this+0x208`, dispatches attached-node vfunc `+0x18`, and returns with `RET 0x10` | read-back documented |
| 0x004fcec0 | CUnit__ForwardAttachedNodeVFunc1CIfPresent | Wave838 attached-node forwarder; corrects stale `CUnitAI__GetAttachedNodeReadyState`, loads `this+0x208`, dispatches attached-node vfunc `+0x1c`, and returns with `RET 0x10` | read-back documented |
| 0x004fcf00 | CUnit__ResetKinematicsAndNotifyController | Wave525 register-this helper zeroing observed kinematic blocks and forwarding vfunc `+0x20` through `this+0x208` | read-back documented |
| 0x004fcfa0 | CUnit__ClearSpawnerSet | Wave525 active-reader clear and `+0x18c` spawner/support set drain helper | read-back documented |
| 0x004fcfe0 | CUnit__ReleaseChildUnits | Wave525 `+0x19c` child-reader release helper with destroyed-flag-dependent child dispatch | read-back documented |
| 0x004fd040 | CUnit__ResetDeploymentGraphAndScheduleEvent | Wave525 cleanup/reset helper that clears child/spawner readers, calls script event id 3/reset, and schedules event `2000` | read-back documented |
| 0x004fd140 | CUnit__MarkDestroyedAndCleanupLinks | Wave525 destroyed-state helper that marks flag bit 2, updates observed counters, triggers segment/script cleanup, and drains `+0x18c` | read-back documented |
| 0x004fd230 | CUnit__SpawnProfileDropPickup | Wave540 profile-driven pickup spawner through `CWorldPhysicsManager__CreatePickup` using profile field `+0xe8` | read-back documented |
| 0x004fd380 | CUnit__GetGridMapByType | Wave525 query mapping profile/type field `+0xfc` values `1`, `2`, and `3/4` to global grid/map pointers | read-back documented |
| 0x004fd3d0 | CUnit__IsCandidateSideCompatibleForTargeting | Wave540 candidate side/team targeting filter over `this+0x138` and profile side filter `+0x128` | read-back documented |
| 0x004fd500 | CUnit__ApplyRenderPositionDeltaToVector | Wave540 HUD marker/world-sprite helper that adds render-position delta into an output vector | read-back documented |
| 0x004fd570 | CSquadNormal__HasAnyLinkedUnitWithField94 | Wave540 linked-unit-list query over `this+0x17c` used by CSquadNormal prune/build-formation paths | read-back documented |
| 0x004fd5b0 | CUnit__IsActiveAndNotInState12 | Wave525 `RET 0x4` predicate requiring non-null unit, destroyed flag clear, and state `+0x244` not `1`/`2` | read-back documented |
| 0x004fd5e0 | CUnit__VFunc26_GetRecentSegmentDamageMeter | Wave540 CUnit-family vtable slot 26 destructible-segment recent-damage meter query | read-back documented |
| 0x004fd6a0 | CUnit__VFunc22_ActivateLinkedTargetsAndChildren | Wave540 CUnit-family vtable slot 22 activation helper over linked target and child list | read-back documented |
| 0x004fd700 | CUnit__VFunc23_DeactivateLinkedTargetsAndChildren | Wave540 CUnit-family vtable slot 23 deactivation helper over linked target and child list | read-back documented |
| 0x004fd760 | CUnit__HasAnyLinkedUnitBeforeTargetTimeout | Wave540 linked-unit-list timeout predicate through `CUnit__IsTargetTimeoutBeforeProfileLimit` | read-back documented |
| 0x00504a50 | CWarspiteDome__UpdatePitchStateAndBlendTracks | Wave541 stale CVBufTexture owner correction; WarspiteDome state/pitch/effect-track helper | read-back documented |
| 0x00504b40 | CWarspiteDome__UpdateTrackedPitchWithClamp | Wave541 stale CVBufTexture owner correction; WarspiteDome tracked pitch solver/clamp helper | read-back documented |
| 0x00504cf0 | CWarspiteDome__ShouldSkipUpdateByStateFlags | Wave541 stale CVBufTexture owner correction; WarspiteDome state/flag skip predicate | read-back documented |
| 0x00504d30 | CWarspiteDome__IsTransitionAllowedByState | Wave541 stale CVBufTexture owner correction; WarspiteDome transition-state predicate | read-back documented |
| 0x00507ab0 | OID__CanFireAtTarget_BallisticArcA | Wave553 target-body hardening for the CUnit ballistic-arc A fire-eligibility wrapper | read-back documented |
| 0x005088b0 | OID__CanFireAtTarget_BallisticArcB | Wave553 target-body hardening for the CUnit ballistic-arc B fire-eligibility wrapper | read-back documented |
| 0x00509140 | OID__UpdateAimTransformAndAttachTargetReader | Wave553 target-body hardening for aim transform/vector copy plus active-reader registration | read-back documented |
| 0x005094b0 | OID__SolveBallisticPitchToTarget | Wave553 four-dword target-vector pitch solver used by CUnit and WarspiteDome callers | read-back documented |
| 0x005096a0 | CUnit__ComputeMinBallisticTravelDistance | Wave553 four-dword target-vector min ballistic travel-distance helper | read-back documented |
| 0x005099a0 | CUnit__ComputeMaxBallisticTravelDistance | Wave553 four-dword target-vector max ballistic travel-distance helper | read-back documented |
| 0x00509f70 | TargetProfileContext__IsEligibleByDistanceBucketOrRange | Wave554 owner-neutral shared target/profile distance-bucket or range-time gate used by Unit deploy/support and other projectile paths | read-back documented |
| 0x0050a0d0 | CUnit__HasMaskBitsA8 | Wave554 one-argument support-mask helper; `RET 0x4` removes older phantom parameter | read-back documented |
| 0x0050a0e0 | OID__ComputeForwardProjectedPointTowardTarget | Wave554 target-body projection helper; `RET 0x8` proves `out_point` plus `target_unit` arguments | read-back documented |
| 0x0050a290 | CUnit__IsTargetTimeoutBeforeProfileLimit | Wave554 ECX-only timeout/profile predicate used by target-set, linked-unit, and squad support scans | read-back documented |
| 0x004fd7a0 | CUnit__HasAnyReadySpawner | Wave525 linked-entry predicate over `+0x18c`; saved name predates stricter read-back of `CUnit__IsInBlockedSupportState` semantics | read-back documented |
| 0x004fd830 | CUnit__SetFactionForHierarchy | Wave527 `RET 0x4` faction-state propagation helper over Unit hierarchy state | read-back documented |
| 0x004fd8d0 | CUnit__FindChildReaderByField270 | Wave527 stale destructable-controller owner correction; scans Unit child readers at `this+0x19c` for field `+0x270` | read-back documented |
| 0x004fd910 | CUnit__FindNearestFactionAnchor | Wave527 `RET 0x4` helper scanning global anchor list `DAT_00855160` into an output position buffer | read-back documented |
| 0x004fda10 | CUnit__GetProfileState120 | Wave527 stale CUnitAI owner correction; reads profile/state pointer `this+0x164 -> +0x120` | read-back documented |
| 0x004fda20 | CUnit__PropagateTargetUnitToHierarchy | Wave527 `RET 0x4` target-unit propagation helper reached from script attack paths | read-back documented |
| 0x004fdad0 | CUnit__TrySpawnMembersForTarget | Wave527 support/spawner target gate over Unit-linked spawn members | read-back documented |
| 0x004fdc20 | CUnit__UpdateSpawnCountAccounting | Wave527 ECX-only vtable target adjusting global spawn count accounting and spawner entries | read-back documented |
| 0x004fdcb0 | CUnit__SetEngagementModeAndMaybeClearTargetReader | Wave527 `RET 0x4` engagement-mode setter with target-reader clearing path | read-back documented |
| 0x004fde30 | CUnit__BeginDeployAnimationIfIdle | Wave525 deploy-animation starter for state `+0x244 == 0`, resolving `"deploying"` and dispatching vfunc `+0xf0` | read-back documented |
| 0x004dfce0 | CUnit__TryActivateAndEnableShadows | Wave507 unit-family static-shadow activation predicate/update helper | read-back documented |
| 0x004dfd10 | CUnit__VFunc18_SyncOldVectorAndClampHeight | Wave507 unit-family vfunc-slot-18 old-vector sync and height clamp helper | read-back documented |
| 0x004f84e0 | CUnit__dtor_base | Wave460 corrected the CUnit destructor-base cleanup body | read-back documented |
| 0x0050ee90 | CUnit__scalar_deleting_dtor | Wave460 corrected a DATA-vtable-referenced CUnit scalar-deleting destructor wrapper | read-back documented |

## Wave741 unwind head callbacks

Wave741 unwind head saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for the unit/object cleanup tail callbacks `0x005d1130 Unwind@005d1130`, `0x005d1138 Unwind@005d1138`, `0x005d1146 Unwind@005d1146`, `0x005d1154 Unwind@005d1154`, and `0x005d1162 Unwind@005d1162`. The saved comments record scope-table DATA xrefs `0x00619fa4` through `0x00619fc4`; the bodies call `CUnit__dtor_base`, `CSPtrSet__Clear`, and `CGenericActiveReader__dtor` on object fields `+0x250`, `+0x264`, `+0x284`, and `+0x294`.

This is saved static retail Ghidra metadata only. Exact parent source-body identity, runtime unit cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Wave 543 CUnit Default-Tuning Block Helper (2026-05-18)

## Wave554 Target/Profile Gate Helpers (2026-05-18)

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x00509f70 | TargetProfileContext__IsEligibleByDistanceBucketOrRange | Owner-neutral register-context helper. Broad callers from BattleEngine auto-targeting, Unit deploy/support, Sentinel flamethrowers, and projectile-burst boundaries show a shared target/profile context rather than a CUnit-only method. Active `+0xa0` profiles are range-time gated by `+0x64`; otherwise the body resolves percent-bucket entries through the `+0xa4` table and `DAT_008553ec`. |
| 0x0050a0d0 | CUnit__HasMaskBitsA8 | `RET 0x4` proves one `mask_bits` argument after `ECX`, removing the older phantom second parameter. The body returns `this+0xa8 & mask_bits`; checked caller is `CSquadNormal__SelectBestSupportOrEscort`. |
| 0x0050a0e0 | OID__ComputeForwardProjectedPointTowardTarget | `RET 0x8` and both OID ballistic fire-check callsites prove two stack arguments: `out_point` and `target_unit`. Active profile path samples target transform vfunc `+0x168`, target velocity vfunc `+0x6c`, profile speed/forward-vector fields, and `DAT_005d857c`; fallback copies the target transform vector into the output. |
| 0x0050a290 | CUnit__IsTargetTimeoutBeforeProfileLimit | ECX-only predicate used by `TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit`, `CUnit__HasAnyLinkedUnitBeforeTargetTimeout`, and `CSquadNormal__SelectBestSupportOrEscort`. Returns true only when `unit+0xa0` has a profile, `unit+0x6c` is nonzero, and the timeout is below profile `+0x44`. |

This pass saved names, signatures, comments, and tags only. Exact target/profile/burst-context/OID/Unit/Squad layouts, timeout units, vector width, runtime targeting/projectile/squad behavior, local names, structure types, and rebuild parity remain unproven.

## Wave 543 CUnit Default-Tuning Block Helper (2026-05-18)

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x004eb9a0 | CUnit__InitDefaultTuningBlock | Register-only helper that initializes the tuning block passed in `ECX` with fixed dword defaults across offsets `+0x00..+0x84`. Observed constants include `1.0` at `+0x00/+0x04/+0x08/+0x0c/+0x1c/+0x50/+0x60`, `0.1` at `+0x40`, `0.8` at `+0x54/+0x58/+0x5c`, and zero elsewhere. Raw thunk `0x004eb1d0` loads `ECX` with `0x0083d248` and jumps here, indicating at least one global-default instance. |

This pass saved the signature, comment, and tags only. Exact tuning-block field names, exact source identity, runtime tuning behavior, concrete global ownership beyond the observed raw thunk, local names, structure types, and rebuild parity remain unproven.

## Wave 545 CUnit Render Distance-Fade Helper (2026-05-18)

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x004f6fd0 | CUnit__RenderWithDistanceFade | `bool __thiscall` helper with one `render_flags` stack argument. `OID__RenderWithState1BOverride` calls it only when `this+0x48` is non-null and returns early if this helper reports handled. The body reads `*(this+0x48)+0xbc`, computes a clamped time delta using `DAT_00672fd0` and constants `0x005d856c/0x005d85d8/0x005d8c68/0x005d8c70`, writes the rounded value to global `0x0063012c` for a nested `CThing__Render(this, render_flags)`, restores `0x0063012c` to `0xff`, and returns true; the nonpositive/NaN path returns false. |

This pass saved the signature, comment, and tags only. Exact fade field meaning, exact `0x0063012c` render-state/global meaning, runtime rendering behavior, source identity, local names, structure types, and rebuild parity remain unproven.

## Wave 540 Unit Support-Tail Helpers (2026-05-18)

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x004fd230 | CUnit__SpawnProfileDropPickup | Profile-driven pickup spawner through `CWorldPhysicsManager__CreatePickup`; copies side and position context from `this+0x138` and `this+0x1c..0x28`, and uses profile field `+0xe8`. |
| 0x004fd3d0 | CUnit__IsCandidateSideCompatibleForTargeting | `RET 0x4` side/team filter for target-selection callers; compares `candidate_side` against Unit side field `this+0x138` and profile side filter `this+0x164->0x128`. |
| 0x004fd500 | CUnit__ApplyRenderPositionDeltaToVector | `RET 0x4` HUD marker/world-sprite helper that adjusts an `inout_position` vector using render-position delta context from virtual calls and `CActor__GetRenderPos`. |
| 0x004fd570 | CSquadNormal__HasAnyLinkedUnitWithField94 | Linked-list query at `this+0x17c` used by CSquadNormal prune/build-formation paths; returns true if any linked unit/object has field `+0x94` nonzero. |
| 0x004fd5e0 | CUnit__VFunc26_GetRecentSegmentDamageMeter | CUnit-family slot 26 helper with one `segment_index` argument; reads destructible segment last-damage context and returns a clamped decaying `0..100` meter. |
| 0x004fd6a0 | CUnit__VFunc22_ActivateLinkedTargetsAndChildren | CUnit-family slot 22 activation helper that writes `this+0x214=1` and dispatches linked target/children through vfunc `+0x58`. |
| 0x004fd700 | CUnit__VFunc23_DeactivateLinkedTargetsAndChildren | CUnit-family slot 23 deactivation helper that clears `this+0x214` and dispatches linked target/children through vfunc `+0x5c`. |
| 0x004fd760 | CUnit__HasAnyLinkedUnitBeforeTargetTimeout | Corrects stale CVBufTexture owner context; scans `this+0x17c` and calls `CUnit__IsTargetTimeoutBeforeProfileLimit` on linked units. |

This pass saved names, signatures, comments, and tags only. Runtime pickup spawning, targeting/faction behavior, HUD marker behavior, squad formation behavior, activation/deactivation behavior, damage-meter behavior, exact source-body identity, concrete layouts, local names, structure types, and rebuild parity remain unproven.

## Wave 541 CWarspiteDome State-Tail Helpers (2026-05-18)

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x00504a50 | CWarspiteDome__UpdatePitchStateAndBlendTracks | Corrects stale `CVBufTexture__UpdatePitchStateAndBlendTracks` ownership. Calls linked-effect height-clearance update, then the adjacent tracked-pitch helper, updates state fields around `+0x260/+0x280/+0x284`, and blends six entries around `+0x268/+0x288`. |
| 0x00504b40 | CWarspiteDome__UpdateTrackedPitchWithClamp | Corrects stale `CVBufTexture__UpdateTrackedPitchWithClamp` ownership. Uses target/profile context and `OID__SolveBallisticPitchToTarget`, refreshes `+0xec`, and clamps the tracked pitch unless flag `+0x2c` bit 2 blocks the path. |
| 0x00504cf0 | CWarspiteDome__ShouldSkipUpdateByStateFlags | Corrects stale `CVBufTexture__ShouldSkipUpdateByStateFlags` ownership. Calls `CUnit__HasAnyLinkedUnitBeforeTargetTimeout` and combines that result with observed state/flag checks at `+0x168`, `+0x214`, and `+0x2c`. |
| 0x00504d30 | CWarspiteDome__IsTransitionAllowedByState | Corrects stale `CVBufTexture__IsTransitionAllowedByState` ownership. Calls `CUnit__HasAnyLinkedUnitBeforeTargetTimeout` and otherwise falls back to state `+0x168 == 0`. |

This pass saved names, signatures, comments, and tags only. Runtime WarspiteDome pitch tracking, transition behavior, linked-effect behavior, exact source-body identity, concrete layouts, local names, structure types, and rebuild parity remain unproven.

## Headless Semantic Wave108 Promotions (2026-02-26)

| Address | Name | Notes |
|---------|------|-------|
| 0x0042ee90 | CUnitAI__CreateAndRegisterByName | Allocates/initializes a `0x1ac` AI object by name and registers it in the global AI set. |
| 0x0042efd0 | CUnitAI__InitDefaults | Constructor-style defaults initializer for CUnitAI runtime fields, thresholds, and owned key string (`\"m_b_rubble\"`). |

## Headless Semantic Wave109 Promotions (2026-02-26)

| Address | Name | Notes |
|---------|------|-------|
| 0x00415140 | CUnitAI__HandleLandedStateTransition | Wave 311 correction supersedes the address-suffixed label; emits `"landed"` trace once, clears transient field `+0x12c`, dispatches landing-related vfuncs, and sets landed-state flag `+0x264` to `1`. |
| 0x00415970 | CUnitAI__HandleDeployUndeployAnimationCompletion | Handles deploy/undeploy animation completion transition and returns completion status to caller state flow. |
| 0x00424a20 | CUnitAI__UpdateDeployAimAndScheduleEvent | Updates deploy-aim progression and schedules follow-up deploy timing event. |
| 0x00424be0 | CUnitAI__AdvanceDeployAnimationPhase | Advances deploy animation phase state machine to the next phase. |
| 0x00425760 | Mat34__OrthonormalizeAxes | Wave 321 corrected the older CUnitAI owner label to an owner-neutral Mat34 basis orthonormalization helper. |
| 0x0042f280 | CUnitAI__ComputeRecursiveNodeSize_Base8 | Computes recursive node-size totals using base element size 8 bytes. |

## Headless Semantic Wave110 Promotions (2026-02-26)

| Address | Name | Notes |
|---------|------|-------|
| 0x00415780 | CUnitAI__PlayDeployingAnimationIfState0 | Wave 311 signature/comment hardening: if transition state `+0x260` is `0`, plays `"deploying"` animation through vfunc slot `+0xf0` and sets state to `1`. |
| 0x004157c0 | CUnitAI__PlayUndeployingAnimation | Wave 311 signature/comment hardening: clears deploy timer/state field `+0x1f0`, resolves `"undeploying"`, and plays it through vfunc slot `+0xf0`. |
| 0x00445570 | CUnitAI__PlayOpenAnimationIfState1Or3 | Gate on states `1/3`, then plays `"open"` animation and sets state to `2`. |
| 0x004455c0 | CUnitAI__PlayCloseAnimationIfState0Or2 | Gate on states `0/2`, then plays `"close"` animation and sets state to `3`. |
| 0x00445610 | CUnitAI__AdvanceOpenCloseShootAnimationState | Animation-state stepper that transitions between `"open"`, `"close"`, and `"shoot"` phases by current index checks. |

## Headless Semantic Wave111 Promotions (2026-02-26)

| Address | Name | Notes |
|---------|------|-------|
| 0x00415a50 | CUnitAI__CanCompleteDeployUndeployTransition | Wave 311 signature/comment hardening: blocks while vfunc slot `+0x10c` is active, then checks target/flag gates at `+0x168`, `+0x214`, and `+0x2c` before allowing completion. |
| 0x00424ca0 | CUnitAI__UpdateDeployTrackingTransformTowardTarget | Updates deploy tracking transform toward target orientation with clamped angular adjustments. |
| 0x004250f0 | CUnitAI__DecayDeployTrackingTransformToNeutral | Relaxes tracking angles toward neutral and rebuilds orientation transform from decayed values. |
| 0x00430b30 | CUnitAI__ComputeRecursiveNodeSize_NodeTreeA | Recursive node-tree size accumulator (`node + 0xC + child`). |
| 0x00431470 | CUnitAI__ComputeRecursiveNodeSize_NodeTreeB | Recursive node-tree size accumulator variant for adjacent tree chain. |

## Headless Semantic Wave112 Promotions (2026-02-26)

| Address | Name | Notes |
|---------|------|-------|
| 0x004015e0 | CUnit__IntegrateVelocityAndResolveGroundCollision | Integrates velocity, resolves ground collision response, and updates map-entry position records. |
| 0x00403690 | CUnit__ReleaseAllAttachedParticleNodes | Releases both attached particle-node sets and frees each node object. |
| 0x00408120 | CUnitAI__IsState2AndBelowHeightDeltaThreshold_00408120 | Boolean state/timestamp predicate using mode `+0x260`, timestamp `+0xcc`, and a global threshold; source identity/layout remain deferred. |
| 0x00408150 | CUnit__ProcessStateSwapAndDeathChecks | Runs state-swap helper and applies flag/altitude-driven death/pickup checks before shared post-step helper call; saved `void * unit` signature on 2026-05-09. |
| 0x004097a0 | CUnit__PushTransformHistoryAndSetCurrent | Copies transform-history rows and refreshes timestamp-like `+0xac`; saved one-stack-argument signature on 2026-05-09, with concrete layout/runtime behavior still deferred. |
| 0x004318c0 | CUnitAI__ComputeRecursiveNodeSize_NodeTreeC | Third recursive node-tree size accumulator variant (`node + 0xC + child`). |

## Headless Semantic Wave113 Promotions (2026-02-26)

| Address | Name | Notes |
|---------|------|-------|
| 0x004178a0 | CBuilding__ProcessClosingAndUnshuttingAnimations | Wave 314 supersedes the older CUnit owner label; handles closing/unshutting animation transitions in CBuilding vtable context. |
| 0x004239f0 | CUnitAI__InitDefaults_AutoConfigTestPath | Constructor-style defaults initializer that stores `c:\\beaautoconfigtest\\` path in object state. |
| 0x00428c70 | CUnitAI__RunSharedStepAndMaybeTriggerFlag4Action | Wave 325 signature/comment/tag hardening: shared step helper resets field-D0 context and conditionally invokes flag-4 action callback. |
| 0x00428cf0 | CUnitAI__ForwardCommandToAttachedNodeThenDispatch | Wave 325 signature/comment/tag hardening: forwards command when eligible and keeps EDI-sourced score/caller-context recovery open. |

## Wave 325 UnitAI Activation / Boundary Correction (2026-05-12)

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x00428710 | CUnitAI__GetRenderPosFromActorOrCache | Saved `__thiscall` signature with output buffer and unused stack argument. |
| 0x00428770 | CUnitAI__GetRenderOrientationFromActorOrCache | Saved `__thiscall` signature with output matrix buffer and unused stack argument. |
| 0x00428800 | CUnitAI__HandleTriggerEventAndMoveToOffset | Saved `bool __fastcall` trigger/event and movement-offset helper signature. |
| 0x004289b0 | CUnitAI__AdvanceActivationAnimationState | Saved `bool __fastcall` activation animation state-machine signature. |
| 0x00428b50 | CUnit__SetReaderAndComputeRelativeYaw | Saved active-reader setter signature with `reader`, `readerContext`, and currently unused stack argument. |
| 0x00428bc0 | CUnitAI__GetTargetHeadingWithOffset | Saved `double __fastcall` active-reader heading/offset helper signature. |
| 0x00428c70 | CUnitAI__RunSharedStepAndMaybeTriggerFlag4Action | Saved shared-step and flag-bit-4 dispatch signature/comment/tag state. |
| 0x00428cb0 | CUnitAI__PlayHitAnimationAndSetFlag | Corrects prior `CExplosionInitThing__TriggerHitAnimationAndSetFlag` owner label. |
| 0x00428cf0 | CUnitAI__ForwardCommandToAttachedNodeThenDispatch | Saved command-forwarding signature while leaving caller-context score recovery open. |
| 0x00428d50 | CUnitAI__PlayActivateAnimationOrFinalizeActivated | Corrects prior `VFuncSlot_22_00428d50` generic label. |
| 0x00428e80 | CComponentAI__ClearReaderIfTargetDestroyedThenForward | Corrects prior `VFuncSlot_04_00428e80` generic label using `CComponentBomberAI` / `CFenrirMainGunAI` vtable context. |
| 0x00429270 | CUnitAI__UpdateHeadingTowardTargetClamped | Boundary correction from stale `0x00429280`; includes the prologue that loads the UnitAI pointer from the turn context. |

This pass saved signatures/comments/tags only. Runtime UnitAI activation, steering, movement, render-cache, command-forwarding, Component-AI cleanup behavior, exact source-body identity, concrete layouts, local names, structure types, and rebuild parity remain unproven.

## Wave 354 UnitAI Indexed Entry / Motion Controller Boundary Tranche (2026-05-12)

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x00444f00 | CUnitAI__CallIndexedEntryVFunc10 | Wave 354 signature hardening: one `entryIndex` stack argument, indexed entry lookup, and vfunc slot `+0x10` dispatch when present. |
| 0x00444f20 | CUnitAI__CanUseIndexedSegmentEntry | Wave 354 signature hardening: one `entryIndex` stack argument with linked segment/core-child gates and active segment value context. |
| 0x00494fa0 | SharedMotionController__VFunc_UpdateUnitAIIndexedEntryFlag | Recovered boundary shared by `CMCBuggy` slot `17` and `CMCHiveBoss` slot `6`; updates output bit `0` through the indexed-segment predicate path. |
| 0x00494ff0 | SharedMotionController__VFunc_CallUnitAIIndexedEntryVFunc10 | Recovered boundary shared by `CMCBuggy` slot `18` and `CMCHiveBoss` slot `7`; dispatches `CUnitAI__CallIndexedEntryVFunc10` when the state-context gate permits it. |
| 0x00495020 | CMCBuggy__VFunc_GetUnitAIEntryTableRoot | Recovered `CMCBuggy` slot `19` getter that follows the controller-owned entry-table root pointer. |

This pass saved signatures/comments/tags plus three function boundaries. Runtime UnitAI or motion-controller behavior, exact source virtual names, concrete layouts, local names, structure types, and rebuild parity remain unproven.

## Wave 486 CUnit Ballistic Aim State Helpers (2026-05-17)

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x004d36c0 | CUnit__InitBallisticAimState | `RET 0x10` helper that copies a four-dword target vector, samples terrain/shadow height through `CStaticShadows__SampleShadowHeightBilinear`, calls the compute helper, and marks ballistic aim state active. |
| 0x004d3730 | CUnit__ComputeBallisticLaunchVelocity | ECX-only helper that scans launch-angle candidates, builds orientation through `CSquadNormal__BuildOrientationMatrixFromEuler`, and writes the chosen launch vector into `this+0x7c/0x80/0x84` plus `this+0x88`. |

This pass saved signatures/comments/tags only. Exact constants, ballistic-state layout, source identity, runtime projectile/aim behavior, concrete types, local names, and rebuild parity remain unproven.

## Wave 507 CUnit Static-Shadow / Height-Clamp Tail Helpers (2026-05-17)

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x004dfce0 | CUnit__TryActivateAndEnableShadows | ECX-only predicate/update helper. Calls `CUnit__MarkDestroyedAndCleanupLinks(this)`, returns false on failure, otherwise calls `CStaticShadows__UpdateVisibility` with global static-shadow manager `0x009c8010`, `this`, and enable flag `1` before returning true. Vtable evidence includes table `0x005dfe04` slot 0 and CUnit-family table `0x005dfd84` slot 32. |
| 0x004dfd10 | CUnit__VFunc18_SyncOldVectorAndClampHeight | Corrects stale `VFuncSlot_18_004dfd10` naming. Calls `CActor__StickToGround(this)`, then clamps current Z at `this+0x24` and old/render Z at `this+0x94` down to global ceiling `0x006fbdfc` when that global is below current Z. Vtable evidence includes unit-family tables `0x005d8efc` and `0x005dfd84` slot 0. |

This pass saved names, signatures, comments, and tags only. Exact source virtual names, concrete height/ceiling semantics, runtime shadow or movement behavior, concrete layouts, local names, structure types, and rebuild parity remain unproven.

Wave912 follow-up: `0x004dfd10` now calls the source-backed `CActor__StickToGround` name at `0x00402030`; the unit override remains a separate provisional height-clamp vfunc until its exact source virtual name is proven.

## Wave 508 CUnit Support / Render Helpers (2026-05-17)

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x004e43d0 | CUnit__CanProvideSupportNow | ECX-only predicate over observed support fields `this+0x3f4`, `this+0x3ec`, profile timing offsets, and global time `DAT_00672fd0`. Xrefs include deploy/support selection paths. |
| 0x004e4420 | CUnit__IsInBlockedSupportState | ECX-only blocked-state predicate over `this+0x3ec`; xrefs stay in Unit, UnitAI, and CSquadNormal support/deploy contexts. |
| 0x004e4480 | CUnit__IsSupportTargetMaskCompatible | Corrects stale `CSquadNormal__IsTargetMaskCompatible` ownership. The body reads CUnit-style support fields and tests `target+0x34`; it returns with `RET 0x4`. |
| 0x004e6660 | CUnit__ResetDamageCooldownTimer | Called by `CUnit__ApplyDamage`; writes `DAT_00672fd0` plus the observed static cooldown constant into `this+0x88`. |
| 0x004e66e0 | CUnit__RenderWithIdentityWorldAndShadowProbe | Resets the world matrix through `CDXEngine__SetWorldMatrixElements`, dispatches render vtable slot `+0x40`, then samples height/shadow through `CStaticShadows__SampleShadowHeightBilinear`. |

This pass saved names, signatures, comments, and tags only. Concrete support profile fields, faction/target-mask semantics, exact source identity, runtime support/deploy/render behavior, structure layouts, local names, and rebuild parity remain unproven.

## Wave 512 CUnit Transition-State Helpers (2026-05-17)

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x004ef000 | CUnit__SetTransitionState1AndNotifyChildren | ECX-only helper that changes `this+0x250` from `2` or `3` to `1`, walks the child/list field at `this+0x19c`, and dispatches child vfunc `+0x5c` when present. |
| 0x004ef050 | CUnit__SetTransitionState3_IfState0Or1 | ECX-only helper that writes `this+0x250 = 3` only when the prior value is `0` or `1`. |
| 0x004ef0f0 | CUnit__SetTransitionState2 | ECX-only helper that writes `this+0x250 = 2`; a nearby state-machine body calls it from the state-3 path after height/position checks. |

This pass saved signatures/comments/tags only. Exact state enum names, source identity, runtime transition behavior, concrete layouts, local names, and rebuild parity remain unproven.

## Wave 830 CUnit VFunc64 Pickup Bridge (2026-05-24)

Probe anchor: Wave830 CUnit vfunc64 pickup.

Wave830 corrected stale `0x004ef100 CUnit__RunTransitionStepThreeTimes` to `0x004ef100 CUnit__VFunc64_SpawnConfiguredPickupThreeTimes` with the `cunit-vfunc64-pickup-wave830` and `wave830-readback-verified` tags. This is hard-to-identify connective CUnit code, not low-importance code: the function body is tiny, but vtable evidence ties it to a CUnit-family virtual slot that bridges transition/lifecycle context into configured pickup spawning.

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x004ef100 | CUnit__VFunc64_SpawnConfiguredPickupThreeTimes | `void __fastcall CUnit__VFunc64_SpawnConfiguredPickupThreeTimes(void * this)`. DATA xref from CUnit-family vtable slot address `0x005e1610` in vtable `0x005e1510`; slot index 64. The body preserves the ECX receiver, initializes a count of `3`, and calls `CUnit__SpawnConfiguredPickupIfAboveWater(this)` three times. |
| 0x004f9490 | CUnit__SpawnConfiguredPickupIfAboveWater | Existing Wave526 helper evidence: builds a local CInitThing-style record, resolves position from the unit, copies side/team field `this+0x138`, and creates the profile-configured pickup from profile field `+0xec` when height is above `DAT_006fbdfc`. |

Queue after Wave830: `6098` total, `5651` commented, `447` commentless, `0` exact-undefined signatures, `0` `param_N`, strict proxy `5651/6098 = 92.67%`, next raw commentless row `0x004f2660 CText__CopyFrom`. Verified backup: `G:\GhidraBackups\BEA_20260524-220229_post_wave830_cunit_vfunc64_pickup_verified`.

This pass saved the name, signature, comments, and tags only. Exact source virtual name, reason for the three pickup-spawn passes, concrete CUnit/profile/init/vtable layouts, runtime pickup/transition behavior, BEA patching, and rebuild parity remain deferred.

## Wave 515 CUnit Speed-Scale Helper (2026-05-17)

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x004f1220 | CUnit__GetSpeedScaleByFlag30C | ECX-only selector returning global float constant `0x005dbe34` when `this+0x30c` is nonzero, otherwise global float constant `0x005df464`. |

This pass saved signature/comment/tag only. Exact flag meaning, source identity, runtime movement behavior, concrete layout, local names, and rebuild parity remain unproven.

## Wave 523 Unit / Squad Targeting Cleanup (2026-05-18)

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x004fb280 | CUnit__UpdateFireControlYawAndQueueEvent | `RET 0x4` helper called from `CUnit__Init` and `VFuncSlot_00_004f9820`; refreshes fire-control pitch/yaw context and schedules event `0xfa1` through `CEventManager__AddEvent_AtTime`. |
| 0x004fb500 | CUnit__CanFireAtTarget_BallisticArcA | `RET 0x8` firing gate that classifies target range, samples target-relative height, checks active ballistic profile window offsets `+0x6c/+0x70`, and forwards `target_unit` plus `ballistic_context` to `OID__CanFireAtTarget_BallisticArcA`. |
| 0x004fb5a0 | CUnit__CanFireAtTarget_BallisticArcB | `RET 0x4` firing gate that shares the range classifier, handles an alternate target vfunc `+0x10c` height path, checks the active ballistic profile window, and forwards to `OID__CanFireAtTarget_BallisticArcB`. |
| 0x004fb650 | CUnit__ForwardAimTransformAndAttachTargetReader | Corrects stale `CWarspite__UpdateAimTransformAndAttachTargetReader` ownership. The generic body tests `this+0x140` and forwards two stack arguments to `OID__UpdateAimTransformAndAttachTargetReader`; xrefs include `CGillMHeadAI__UpdateAimTransformAndTargetReader` and `CWarspite__Update`. |
| 0x004fb670 | CUnit__ClassifyTargetRangeBand | `RET 0x4` target-range classifier. Returns `2` for null/too-close/invalid targets, `1` for beyond-range targets, and `0` for usable in-range targets; ballistic owners use min/max travel-distance helpers and fallback units use profile range fields `+0x2c/+0x30`. |

This pass saved names, signatures, comments, and tags only. Runtime targeting behavior, runtime weapon behavior, exact source-body identity, concrete Unit/OID/target layouts, exact enum names, local names, and rebuild parity remain unproven.

## Wave 553 Monitor/OID Ballistic Vector Cleanup (2026-05-18)

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x00507ab0 | OID__CanFireAtTarget_BallisticArcA | `RET 0x8` and the `CUnit__CanFireAtTarget_BallisticArcA` callsite prove `target_unit` plus `ballistic_context` after `ECX`; the older third explicit parameter was register carryover. The body checks attachment/origin height, fear-grid clearance, target yaw/pitch windows, ballistic-arc statement state, optional trace context, and `OID__TraceLineAndSelectBestTargetHit`. |
| 0x005088b0 | OID__CanFireAtTarget_BallisticArcB | `RET 0x4` and the `CUnit__CanFireAtTarget_BallisticArcB` callsite prove one `target_unit` argument after `ECX`; the older second explicit parameter was register carryover. The body covers alternate target-relative pitch/profile windows, static-shadow fallback behavior, and optional CLine visibility. |
| 0x00509140 | OID__UpdateAimTransformAndAttachTargetReader | `RET 0x8` proves two explicit stack arguments. Target-body read-back uses `target_transform` to compute/copy target-vector state at `this+0x84..+0x90`, sets dirty flag `+0x80`, and registers `target_reader` through `CGenericActiveReader__SetReader`; exact higher-level wrapper argument order remains open. |
| 0x005094b0 | OID__SolveBallisticPitchToTarget | `RET 0x10` proves four target-vector dwords after `ECX`; the first three are used as target coordinates and `target_w` is retained by the copied 16-byte vector convention. |
| 0x005096a0 | CUnit__ComputeMinBallisticTravelDistance | `RET 0x10` vector-target helper. Non-ballistic statements return owner `+0xa0` field `+0x74`; ballistic statements derive minimum reachable travel distance from target height, launch speed, gravity, and active pitch-window fields. |
| 0x005099a0 | CUnit__ComputeMaxBallisticTravelDistance | `RET 0x10` vector-target helper. Non-ballistic statements return owner `+0xa0` field `+0x78`; ballistic statements derive maximum reachable travel distance from target height, launch speed, gravity, and active pitch-window fields. |

This pass saved signatures, comments, and tags only. Runtime targeting/projectile behavior, exact boolean contracts, exact range semantics, concrete Unit/OID/profile/target/vector layouts, local names, structure types, and rebuild parity remain unproven.

## Wave 524 Unit Deploy / Component Effects / Emitter Transform Cleanup (2026-05-18)

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x004fbcb0 | CUnit__UpdateDeployStateAndChargeEffects | ECX-only deploy/support state helper. It gates active support readers at `+0x144` and mounted unit profiles at `+0x140`, updates state/timer fields `+0x168/+0x16c/+0x1e8/+0x1ec`, plays profile sound/effects, emits charge attachment particles, and starts `"deploying"` animation when profile state permits. |
| 0x004fc000 | CUnit__CanDeployNow | ECX-only deploy-readiness predicate. Reader-backed support is allowed unless blocked support candidates appear under profile flag `+0x110`; mounted support requires `+0x1e8` and `CUnit__IsEligibleByDistanceBucketOrRange(this+0x140)`. |
| 0x004fc220 | CUnit__SpawnComponentEffectsRecursive | ECX-only recursive component-effect spawner. It walks component/effect handles at `+0x1c4` when the profile effect at `this+0x164+0x1c` exists, creates particle effects, copies transform/basis data into spawned renderers, refreshes mesh-renderer time, then recurses through child units at `+0x19c`. |
| 0x004fc4e0 | CUnit__UpdateTransform | Corrects older docs that over-described movement/terrain updates. `RET 0x10` proves four explicit stack arguments after ECX; the body resolves/creates a cached emitter transform keyed by slot tag/cache key, calls `CUnit__FindEmitterIndexBySlotTag`, and writes transformed output position/basis buffers. |
| 0x004fc6e0 | CUnit__FindEmitterIndexBySlotTag | `RET 0x18` proves six explicit stack arguments after ECX. The switch maps emitter slot tags `1..0x1d` to attachment names including `SpawnerA-E`, `WaypointA-E`, `Component`, `Engine`, `Trail`, `Smoke`, `Thruster`, `Doorstop`, `Activation`, and `Charge`, then forwards through the mesh/profile vfunc `+0x1c`. |

This pass saved signatures/comments/tags only. Runtime deploy behavior, runtime component/particle behavior, exact source-body identity, concrete Unit/profile/cache layouts, exact slot enum names, local names, and rebuild parity remain unproven.

## Wave 528 Unit / Warspite Command Tail Helpers (2026-05-18)

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x004fe030 | CUnit__TriggerEffect | `RET 0x4` proves one explicit `trigger_context` argument. Current evidence shows a trigger/message helper that gates through `CBattleEngine__IsWeaponModeCompatibleWithMountState`, selects pilot text IDs, allocates `CMessage`, and queues it through the global message box when present. |
| 0x004fe390 | CEngine__EnableThingByNameFlag | `RET 0x4` proves one script-provided `thing_name` argument. The body walks `this+0x18c`, compares profile/name pointers, and sets matched field `+0x3f4` to `1`. |
| 0x004fe3f0 | CEngine__DisableThingByNameFlag | `RET 0x4` proves one script-provided `thing_name` argument. The body clears matched field `+0x3f4`, clears active-reader state when it points at the matched entry, and refreshes support selection when present. |
| 0x004fe480 | CEngine__DispatchBoundCallbackIfPresent | ECX-only callback/controller forwarder over `this+0x208` and vfunc `+0x24`. |
| 0x004fe500 | CSquadNormal__SetReaderAndUnregisterFromFactionSets | `RET 0x4` proves one `reader` argument. The body writes `this+0x148` and removes this squad from global faction sets when reader is non-null. |
| 0x004fe540 | CUnitAI__AccumulateForwardedCommandScore | `RET 0x4` proves one `score_delta` argument. The body schedules event `0xfa5`, accumulates a scaled score into `this+0x218`, and writes field `+0x21c` to `10`. |
| 0x004ffdd0 | CSquadNormal__SetReaderAndRefreshSupportSelection | `RET 0x8` proves `reader` and `selection_context` arguments. The body writes active-reader/support-selection state and stores the selection context into `this+0x10`. |

This pass saved signatures/comments/tags only. Runtime trigger/message behavior, script command behavior, support selection behavior, exact source-body identity, concrete Unit/Engine/SquadNormal/UnitAI layouts, local names, and rebuild parity remain unproven.

## Wave 527 CUnit Faction / Spawn Helpers (2026-05-18)

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x004fd830 | CUnit__SetFactionForHierarchy | `RET 0x4` proves one explicit `faction_state` argument. The body writes faction-like state and walks child readers under `this+0x19c`; exact enum names remain open. |
| 0x004fd8d0 | CUnit__FindChildReaderByField270 | Corrects stale `CDestructableSegmentsController__FindMemberByField270` ownership. `CDestructableSegmentsController__Init` passes its owner Unit pointer at `this+0x10`, and the target body scans Unit child-reader entries at `this+0x19c` for field `+0x270`. |
| 0x004fd910 | CUnit__FindNearestFactionAnchor | `RET 0x4` proves one output-position argument. The body scans global anchor list `DAT_00855160`, compares position/distance state, and writes the selected anchor position into the caller-provided buffer. |
| 0x004fda10 | CUnit__GetProfileState120 | Corrects stale `CUnitAI__GetWeaponNodeState120` ownership. Named callers pass attached Unit pointers from AI objects, and the body reads `this+0x164 -> +0x120`. |
| 0x004fda20 | CUnit__PropagateTargetUnitToHierarchy | `RET 0x4` target-unit propagation helper reached from `IScript__Attack`; it walks Unit hierarchy/reader state rather than taking a second explicit stack argument. |
| 0x004fdad0 | CUnit__TrySpawnMembersForTarget | `RET 0x4` support/spawner target gate over linked spawn-member entries, including a raw callsite at `0x004ff68c` outside a named function boundary. |
| 0x004fdc20 | CUnit__UpdateSpawnCountAccounting | ECX-only vtable target that adjusts global spawn-count accounting through `DAT_008a9b8c` and forwards `this+0x18c` entries to `CSpawnerThng__UpdateSpawnCount`. |
| 0x004fdcb0 | CUnit__SetEngagementModeAndMaybeClearTargetReader | `RET 0x4` engagement-mode setter that writes the observed mode field and clears/updates target-reader state when the current target is no longer compatible. |
| 0x00511510 | CUnit__GetTypePriorityWeight | Wave560 queue-tail reference resolver tranche helper. `CSpawnerThng__UpdateSpawnCount`, `CUnit__MarkDestroyedAndCleanupLinks`, and `CUnit__UpdateSpawnCountAccounting` pass a unit/profile definition pointer; the body switches on field `+0xe0` and returns spawn/destroy accounting weights `1`, `5`, `10`, `20`, `100`, or `0`. |

This pass saved names, signatures, comments, and tags and corrected two stale owner labels only. Wave560 additionally saved the `CUnit__GetTypePriorityWeight` signature/comment while the same queue-tail reference resolver tranche saved `CWorldPhysicsManager__ResolveThingOrComponentDefinitionRefs` in the WorldPhysicsManager index. Runtime faction behavior, runtime support/spawn behavior, exact source-body identity, concrete Unit/profile/reader/spawner layouts, exact enum names, local names, and rebuild parity remain unproven.

## Wave 526 CUnit Core Tail / Init Helpers (2026-05-18)

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x004f84c0 | CUnit__VFunc01_ScalarDeletingDtor | `RET 0x4` wrapper that calls `CUnit__dtor_base`, conditionally frees `this` when delete flag bit 0 is set, and returns `this`. |
| 0x004f86d0 | CUnit__Init | Corrects the older no-stack-argument signature to `void __thiscall CUnit__Init(void * this, void * init)` from focused `RET 0x4` instruction read-back. |
| 0x004f9430 | CUnit__ApplyRandomDestructibleDamageBurst | ECX-only destructible damage-burst helper; exact runtime destructible behavior remains deferred. |
| 0x004f9490 | CUnit__SpawnConfiguredPickupIfAboveWater | Corrects stale explosion-owner labeling; profile-configured pickup spawn is gated by observed water/height context. |
| 0x004f95d0 | CUnit__VFunc02_CleanupWorldLinksAndForward | Kills sounds, drains observed Unit reader/link/effect/controller state, and forwards to `CComplexThing__Shutdown`. |
| 0x004f9820 | CUnit__HandleEvent | `RET 0x4` event handler with a single event record argument; default cases forward to `CActor__HandleEvent`. |
| 0x004f99b0 | CUnit__PlayRespawnVoiceCueIfAvailable | ECX-only respawn voice-cue helper; exact runtime cue selection remains open. |
| 0x004f99f0 | CUnit__GetCurrentHealthOrSubtreeHealth | Corrects a stale non-Unit owner label; x87 return helper reads direct or subtree health-like state. |
| 0x004f9a40 | CUnit__GetRootSubtreeHealthIfAnyActive | Adjacent x87 root/subtree health query when active data exists. |
| 0x004f9a60 | CUnit__RemoveLinkedObjectFromSpawnerSet | `RET 0x4` helper that removes a linked object from `this+0x18c` and dispatches linked-object vfunc `+0x4`. |
| 0x004fa800 | CUnit__UpdateClosingAndUnshuttingState | ECX-only closing/unshutting state helper; exact enum names and runtime transition behavior remain open. |
| 0x004fa8d0 | CUnit__UpdateMotionAttachmentsAndEffects | ECX-only motion attachment/effect-link update helper; concrete attachment/effect layouts remain deferred. |

This pass saved signatures/comments/tags and eight owner/name corrections only. Runtime init/event/pickup/health/motion/effect behavior, exact source-body identity, concrete Unit/init/profile/effect layouts, exact enum names, local names, and rebuild parity remain unproven.

## Wave 525 Unit Tail Deploy / Cleanup Helpers (2026-05-18)

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x004fcdc0 | CUnit__SetCollisionAndDamageFlags | `RET 0x4` proves one explicit `base_flags` argument after ECX. The body writes `base_flags | 0x80200013` when `this+0x164 -> +0x104` exists, otherwise `base_flags | 0x80000013`, into `this+0x34`. |
| 0x004fcf00 | CUnit__ResetKinematicsAndNotifyController | Register-this helper that zeroes four-word blocks at `+0x14c` and `+0x7c`, copies `+0x114` to `+0x120`, and calls attached controller/node vfunc `+0x20` through `this+0x208` when present. |
| 0x004fcfa0 | CUnit__ClearSpawnerSet | Clears active reader `+0x144`, drains linked set `+0x18c`, removes each value, and invokes value vfunc `+0x8`. |
| 0x004fcfe0 | CUnit__ReleaseChildUnits | Drains child reader nodes at `+0x19c`, dispatching child vfunc `+0x8` or `+0xc8` based on destroyed flag bit 2 at `this+0x2c`, then destructs/frees each active-reader node. |
| 0x004fd040 | CUnit__ResetDeploymentGraphAndScheduleEvent | Releases child and spawner/support readers, clears `+0x144`, calls `CExplosionInitThing__ctor_like_004fd230`, calls script event id 3/reset on `+0x74`, and schedules event `2000`. |
| 0x004fd140 | CUnit__MarkDestroyedAndCleanupLinks | Returns 0 if destroyed flag bit 2 is already set; otherwise kills sounds, marks the destroyed flag, adjusts observed type/side counters, triggers destructible-segment cascade, calls script event id 5, clears `+0x144`, drains `+0x18c`, and returns 1. |
| 0x004fd380 | CUnit__GetGridMapByType | Register-this query returning global grid/map pointers `DAT_00855290`, `DAT_00855294`, or `DAT_00855298` for profile/type field `+0xfc` values `1`, `2`, or `3/4`. |
| 0x004fd5b0 | CUnit__IsActiveAndNotInState12 | `RET 0x4` predicate requiring non-null unit, destroyed flag bit 2 clear, and state field `+0x244` not equal to `1` or `2`. |
| 0x004fd7a0 | CUnit__HasAnyReadySpawner | Walks linked entries at `+0x18c` and returns true when any entry satisfies `CUnit__IsInBlockedSupportState`. The saved name predates this stricter read-back, so exact ready/blocked semantics remain open. |
| 0x004fde30 | CUnit__BeginDeployAnimationIfIdle | Starts the `"deploying"` animation only when state field `+0x244` is `0`, then sets state `3`, resolves the animation index, and dispatches vfunc `+0xf0`. |

This pass saved signatures/comments/tags only. Runtime deploy behavior, runtime animation/destruction/collision behavior, exact source-body identity, concrete Unit/profile/active-reader layouts, exact enum names, local names, and rebuild parity remain unproven.

## Headless Semantic Wave114 Promotions (2026-02-26)

| Address | Name | Notes |
|---------|------|-------|
| 0x0040e8e0 | CUnit__IsNearGroundByTerrainProbe | Terrain/shadow-height probe gate that returns boolean-like near-ground state from height-threshold comparison. |
| 0x0040eeb0 | CBattleEngine__FinishedPlayingCurrentAnimation | Supersedes the prior `CUnit__FinishedPlayingCurrentAnimation` owner label; checks `flytowalk`/`walktofly` animation indices and dispatches the corresponding next-mode set call. |

## Headless Semantic Wave115 Promotions (2026-02-26)

| Address | Name | Notes |
|---------|------|-------|
| 0x00447ac0 | CUnitAI__PlayWingFoldedAnimationAndSetState3 | Plays `"wingfolded"` animation, resets cached-anchor enable flag, and sets door/wing state machine to state `3`. |
| 0x00447b10 | CUnitAI__PlayWingUnfoldedAnimationAndSetState5 | Plays `"wingunfolded"` animation and sets door/wing state machine to state `5`. |
| 0x00447b60 | CUnitAI__HasReachedCachedAnchorPoint | Returns true when XY distance to cached anchor point (`+0x280/+0x284`) is below arrival threshold. |
| 0x00447bb0 | CUnitAI__GetOrGenerateCachedAnchorPoint | Returns cached anchor point or generates one via bounded randomized search until validity check passes. |
| 0x00447fa0 | CUnitAI__AdvanceDoorWingAnimationState | Advances door/wing animation chain (`dooropening/dooropen/doorclosing/doorclosed/wing*`) and dispatches transition callbacks. |

## Headless Semantic Wave116 Promotions (2026-02-26)

| Address | Name | Notes |
|---------|------|-------|
| 0x00445ad0 | CUnitAI__UpdateDoorWingEngagement_CloseRange | Close-range engagement updater that toggles open/close animation paths and movement offsets around target proximity thresholds. |
| 0x00445f40 | CUnitAI__UpdateDoorWingEngagement_MidRange | Mid-range engagement updater that evaluates planar distance/angle and chooses direct reposition vs helper-driven tracking update. |
| 0x00446150 | CUnitAI__UpdateDoorWingEngagement_LongRange | Long-range engagement updater that applies standoff thresholds, executes open/close transitions, and updates movement target. |
| 0x00446400 | CUnitAI__EnterDoorWingOpenTrackingState | Enters/maintains open-tracking mode, randomizes follow distance threshold, and triggers open-animation path when target exists. |

## Headless Semantic Wave117 Promotions (2026-02-26)

| Address | Name | Notes |
|---------|------|-------|
| 0x00444f00 | CUnitAI__CallIndexedEntryVFunc10 | Resolves indexed entry pointer and calls entry vfunc slot `+0x10` when present. |
| 0x00447a40 | CUnitAI__SetDoorWingState2AndClampYawDelta | Enters state `2` and clamps yaw-delta field around configured bounds when transition gating passes. |
| 0x004480c0 | CUnitAI__CanContinueDoorWingTransition | Returns true when anchor/target/state gates allow door-wing transition continuation. |
| 0x00448110 | CUnitAI__SetDoorWingState6 | Writes door-wing state field `+0x27c` to state `6`. |
| 0x00448120 | CUnitAI__SetDoorWingState7AndMirrorYawOffset | Writes state `7` and mirrors yaw-offset field around a constant pivot. |

## Headless Semantic Wave118 Promotions (2026-02-27)

| Address | Name | Notes |
|---------|------|-------|
| 0x0044d1f0 | CUnitAI__RunHelper2000AndDispatchVFunc0x38IfFlag4 | Runs shared helper `0x00402000` then dispatches vfunc slot `+0x38` when bit-flag `0x4` is set. |
| 0x0044d210 | CUnitAI__RenderWithStaticShadowVisibilityUpdate | Updates static-shadow visibility gate (`CStaticShadows__UpdateVisibility`) then forwards to `CThing__Render`. |

## Headless Semantic Wave119 Promotions (2026-02-27)

| Address | Name | Notes |
|---------|------|-------|
| 0x00444f20 | CUnitAI__CanUseIndexedSegmentEntry | Indexed segment-entry eligibility predicate that resolves per-index pointers and enforces segment/core-child gates before permitting continuation. |
| 0x0044cd20 | CUnitAI__DecayEngagementMetricAndMaybeTriggerVFunc200 | Decays engagement metric field, dispatches vfunc slot `+0x200` under threshold/flag conditions, and clamps against profile maximum. |
| 0x00440b70 | CDamage__ctor_clear_head_and_init_flag | Wave 364 supersedes the stale CUnitAI owner label; this is damage-system initialization context, not UnitAI state. |

## Headless Semantic Wave122 Promotions (2026-02-27)

| Address | Name | Notes |
|---------|------|-------|
| 0x0047c040 | CGroundAttackAircraft__AdvanceCloseShootAnimationState | Wave 391 owner correction: GroundAttackAircraft function table `0x005e2bf0` slot `50`; advances open/shoot/close/idle animation transition state by current animation index and writes bay state field `+0x27c`. The older broad `CUnitAI` label is stale. |

## Wave 455 CUnit Cleanup Owner Correction (2026-05-16)

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x004d38c0 | CUnit__TryDestroyedCleanupAndResetDeploymentGraph | Corrected older InfluenceMap ownership. Static body calls `CUnit__MarkDestroyedAndCleanupLinks`, returns `0` on failure, otherwise calls `CUnit__ResetDeploymentGraphAndScheduleEvent` and returns `1`; the only observed xref is vtable data at `0x005e0054`. |

This pass saved name/signature/comment/tag only. Runtime unit lifecycle behavior, exact virtual name, concrete layout, locals/types, and rebuild parity remain unproven.

## Wave 460 CUnit Destructor Correction (2026-05-16)

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x004bfe00 | CUnit__dtor_base_Thunk_004bfe00 | Jump thunk to `CUnit__dtor_base` at `0x004f84e0`; reached by the Wave460 scalar-deleting wrapper and unwind cleanup paths. |
| 0x004f84e0 | CUnit__dtor_base | Destructor-base body resets CUnit vtable pointers, tears down observed particle/effect owner-link cells through `ParticleEffectLink__SetHandleStateAndClear`, clears pointer-set style lists, removes owner links, and delegates to `CActor__dtor_base`. |
| 0x0050ee90 | CUnit__scalar_deleting_dtor | DATA-vtable-referenced slot-1 scalar-deleting wrapper. Calls `CUnit__dtor_base_Thunk_004bfe00`, optionally frees `this` when `flags & 1`, returns `this`, and ends with `RET 0x4`. |

Wave477 refreshed the saved `CUnit__dtor_base` comment after correcting `0x004cb0b0` to owner-neutral `ParticleEffectLink__SetHandleStateAndClear`; the helper is not CUnit-specific and is also reached from Mine, BattleEngine, raw cleanup, projectile, and other contexts.

This pass saved name/signature/comment/tag only. The adjacent `0x004f84c0` CUnit slot-1 wrapper remains queued, and runtime cleanup behavior, exact CUnit/owner-link layouts, exact source identity, locals/types, and rebuild parity remain unproven.

## Key Observations

- **CUnit is base class** for all interactive actors - player mech, enemies, vehicles, infantry, etc.
- **Damage system** uses shield/armor subsystem with character-specific multipliers
- **Transform system** integrates with collision and physics
- **Effects system** is data-driven - health state triggers visual/audio events
- **Weapons integration** - each unit may have multiple weapons, turrets, targeting

## Related Files

- Career.cpp - Kill tracking (TK_AIRCRAFT, TK_VEHICLES, TK_MECHS, TK_INFANTY (typo), TK_EMPLACEMENTS)
- Mech.cpp - Player mech subclass (extends CUnit with cockpit/camera/targeting)
- Player.cpp - Player-specific god mode and vulnerability flags
- BattleEngine.cpp - SetVulnerable(), SetInfinateEnergy() calls from units

---
*Migrated from ghidra-analysis.md (Dec 2025)*
