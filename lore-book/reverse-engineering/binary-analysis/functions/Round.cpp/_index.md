# Round.cpp Functions

Wave1196 current-risk update: Wave1196 (`wave1196-round-rocket-projectile-vfunc-residual-current-risk-review`) accounts for `4 Round/Rocket projectile vfunc residual score17 current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence and saved comment/tag normalization. The rows are `VFuncSlot_39_004d8ae0`, `VFuncSlot_66_004d8e40`, `VFuncSlot_00_004d9910`, and `CRocket__VFunc_22_CreateBigRocketEngineEffects`. Ghidra dry/apply/final-dry reported `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=47 missing=0 bad=0`, then `updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=47 missing=0 bad=0`, then final dry updated=0 skipped=4. No rename, no signature change, no function-boundary change, and no executable-byte change occurred. Codex read-only consults used; no Cursor/Composer. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt; expanded static surface remains `1560/1560 = 100.00%`; Wave1108 current focused accounting is `881/1179 = 74.72%`; current risk candidates: 6166; current focused candidates: 1142; live regenerated current focused candidates: 1142; remaining active focused work: 298; current-risk denominator; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `7 xref rows`, `1386 instruction rows`, and `4 decompile rows`. Verified backup: `G:\GhidraBackups\BEA_20260606-204237_post_wave1196_round_rocket_projectile_vfunc_residual_current_risk_review_verified`. Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference; exact source virtual names, exact hit/collision/event/effect layouts, concrete CRound/CMissile/CRocket/particle-handle layouts, runtime projectile behavior, runtime engine-effect behavior, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof. Probe token anchor: Wave1196; wave1196-round-rocket-projectile-vfunc-residual-current-risk-review; 881/1179 = 74.72%; 4 Round/Rocket projectile vfunc residual score17 current-risk rows; current focused candidates: 1142; live regenerated current focused candidates: 1142; remaining active focused work: 298; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=4 skipped=0; comment_only_updated=4; tags_added=47; final dry updated=0 skipped=4; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consults used; no Cursor/Composer; VFuncSlot_39_004d8ae0; VFuncSlot_66_004d8e40; VFuncSlot_00_004d9910; CRocket__VFunc_22_CreateBigRocketEngineEffects; 0 / 0 / 0; 6411/6411 = 100.00%; 7 xref rows; 1386 instruction rows; 4 decompile rows; G:\GhidraBackups\BEA_20260606-204237_post_wave1196_round_rocket_projectile_vfunc_residual_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.

Wave1161 current-risk update: Wave1161 (`wave1161-collision-seeking-round-current-risk-review`) accounts for `17 collision-seeking/mesh-collision current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, no runtime-file mutation, and Codex read-only consults used while Codex root made the final judgment. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `533/1179 = 45.21%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 646; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `74 xref rows` and `1567 instruction rows`. Static anchors include `CCollisionSeekingRound__InitCollisionLineAndSound`, `CCollisionSeekingRound__ResolveRoundCollisionResponse`, `CCollisionSeekingRound__ProcessMapWhoCollisionSweep`, `CMeshCollisionVolume__TestSweptSphereAgainstMeshPart`, `CMeshCollisionVolume__ResolveContactNormalAndPlane`, and `CCollisionSeekingRound__ShutdownMonitorAndDestruct`. Verified backup: `G:\GhidraBackups\BEA_20260606-014548_post_wave1161_collision_seeking_round_current_risk_review_verified`. Runtime collision behavior, runtime projectile behavior, exact CCollisionSeekingRound/CMeshCollisionVolume/CLine layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1161; wave1161-collision-seeking-round-current-risk-review; 533/1179 = 45.21%; 17 collision-seeking/mesh-collision current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 646; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; 74 xref rows; 1567 instruction rows; CCollisionSeekingRound__InitCollisionLineAndSound; CCollisionSeekingRound__ResolveRoundCollisionResponse; CCollisionSeekingRound__ProcessMapWhoCollisionSweep; CMeshCollisionVolume__TestSweptSphereAgainstMeshPart; CMeshCollisionVolume__ResolveContactNormalAndPlane; CCollisionSeekingRound__ShutdownMonitorAndDestruct; G:\GhidraBackups\BEA_20260606-014548_post_wave1161_collision_seeking_round_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

> Source File: Round.cpp | Binary: BEA.exe
> Debug Path: 0x00631d38
> Last updated: 2026-05-17

## Current Status

Wave493 hardened the current queue-head CRound constructor/init/destructor core in the live Ghidra project. This is saved static retail-binary evidence only: it does not prove exact source virtual names, concrete `CRound`, `CRoundInitThing`, or `CRoundData` layouts, runtime projectile collision/effect behavior, BEA launch behavior, game patching, or rebuild parity.

Wave494 hardened the adjacent CRound/CMissile shared slot-2 entry and two engine launch-tail helpers while also documenting collision-seeking / CCSRay destructor-tail functions in the neighboring source index. The new Round.cpp evidence remains static saved-Ghidra refinement only.

Wave495 hardened the next projectile/round spawn-tail tranche: target-reader binding/removal, nearby hostile selection, aim-state synchronization, preset scalar/name lookup, configured projectile spawn, trail-effect arming, and the effect transform helper. It also corrected Wave494's `0x004d9ef0` owner from stale `CEngine__...` wording to `CRound__UpdateRoundAndTriggerLaunchEffect`.

Wave1160 (`wave1160-weapon-projectile-targeting-current-risk-review`) re-read the CWeapon/ProjectileBurst/CRound current-risk spine with fresh Ghidra evidence and saved tag-only normalization for `0x00506010 ProjectileBurst__SpawnFromPercentBucketFallback` and `0x005069f0 ProjectileBurst__SpawnFromCurrentPreset`. CRound anchors include `CRound__SpawnConfiguredProjectile`, `CRound__ArmProjectileAndSpawnTrailEffect`, `CRound__SelectBestTargetReaderAndSyncAimState`, and `CRound__UpdateEffectTransformByMode_004d9f30`; exports verified `51 xref rows` and `3272 instruction rows`. Current active accounting is `516/1179 = 43.77%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 663; current risk candidates: 6166; static debt remains `0 / 0 / 0`; closure remains `6411/6411 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260606-011357_post_wave1160_weapon_projectile_targeting_current_risk_review_verified`. This was tag-only normalization (`updated=2 skipped=0 renamed=0`, `tags_added=16`) with no rename, no signature change, no comment change, and no runtime proof. Exact source `CWeapon::Fire`, exact retail `CBattleEngine::WeaponFired`, `weapon_fire_breaks_stealth`, runtime projectile/targeting/stealth behavior, exact layouts, BEA patching, visual QA, and rebuild parity remain separate proof. Probe token anchor: Wave1160; wave1160-weapon-projectile-targeting-current-risk-review; 516/1179 = 43.77%; 19 CWeapon/ProjectileBurst/CRound current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 663; current risk candidates: 6166; fresh Ghidra export; tag-only normalization; updated=2 skipped=0 renamed=0; tags_added=16; no rename; no signature change; no comment change; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; 51 xref rows; 3272 instruction rows; CWeapon__DoesTargetMaskMatchDistanceProfile; ProjectileBurst__SpawnFromPercentBucketFallback; ProjectileBurst__SpawnFromCurrentPreset; CRound__SpawnConfiguredProjectile; CRound__ArmProjectileAndSpawnTrailEffect; G:\GhidraBackups\BEA_20260606-011357_post_wave1160_weapon_projectile_targeting_current_risk_review_verified; weapon_fire_breaks_stealth; exact CBattleEngine::WeaponFired; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Wave920 re-reviewed eight CRound projectile/targeting helpers (`0x004d9ef0`, `0x004daab0`, `0x004daba0`, `0x004dac90`, `0x004db090`, `0x004db150`, `0x004db630`, and `0x004d8410`) with fresh metadata, tag, instruction, and decompile exports. The saved names/signatures/comments remain appropriate for the current evidence; no Ghidra mutation was performed.

Wave941 (`missile-linked-object-dispatch-review-wave941`) re-reviewed the CMissile linked-object dispatch join back into the CRound base context. The read-only pass used `0x004d8410 CRound__Init`, `0x004d8dc0 VFuncSlot_02_004d8dc0`, `0x004d9ef0 CRound__UpdateRoundAndTriggerLaunchEffect`, and `0x004db630 CRound__ArmProjectileAndSpawnTrailEffect` as context for `0x004baae0 CMissile__Init`, `0x004bac10 CMissile__DispatchLinkedObjectVFunc68AndPostHook`, `0x0050f8b0 CMissile__scalar_deleting_dtor`, and `0x0050f8d0 CMissile__Destructor`. Vtable anchors `0x005e3ba4`, `0x005e3ba8`, `0x005e3bc8`, `0x005e3cb8`, `0x005e3cc0`, `0x005de82c`, and `0x005de850` preserve the CMissile/CRound join; `0x00452da0 SharedVFunc__NoOp_Ret08` remains a shared post-hook. No mutation, rename, signature change, comment change, function-boundary change, or executable-byte change was warranted. Wave911 focused re-audit progress after Wave941 is `179/1408 = 12.71%`; export-contract closure remains `6113/6113 = 100.00%`; verified backup `G:\GhidraBackups\BEA_20260528-034712_post_wave941_missile_linked_object_dispatch_review_verified`.

Wave991 (`round-config-bridge-review-wave991`) re-exported `0x004d8410 CRound__Init` as round/projectile configuration bridge context for the saved `0x00426150 CCollisionSeekingRound__Init` comment/tag normalization. The Wave991 context ties `CRound__Init` to `CCollisionSeekingRound__Init`, `0x00430210 CRoundStatement__LoadFromMemBuffer`, and `0x00437490 CPhysicsScriptStatements__CreateStatementType5`; no `CRound__Init` mutation, rename, signature change, comment/tag change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation was performed. Queue closure remains `6222/6222 = 100.00%`; Wave911 focused re-audit progress is `445/1408 = 31.61%`; expanded static surface progress is `525/1478 = 35.52%`. Verified backup: `G:\GhidraBackups\BEA_20260531-045300_post_wave991_round_config_bridge_review_verified`.

Wave1011 (`round-vtable-boundary-wave1011`, `wave1011-readback-verified`) followed the raw caller from `0x004d8d07` into `0x0040ac50 CBattleEngine__Rearm` and recovered two shared CRound / CMissile-style vtable boundaries: `0x004d8ac0 VFuncSlot_16_004d8ac0` and `0x004d8ae0 VFuncSlot_39_004d8ae0`. The pass also re-read adjacent `0x004d8dc0 VFuncSlot_02_004d8dc0` context and deliberately deferred the larger separate `0x004d8e40` DATA-backed target. Queue closure is `6236/6236 = 100.00%`; Wave911 focused progress remains `505/1408 = 35.87%`; expanded static surface progress is `705/1491 = 47.28%`; top-500 coverage remains `409/500 = 81.80%`. Verified backup: `G:\GhidraBackups\BEA_20260531-172337_post_wave1011_round_vtable_boundary_verified`. Runtime projectile/hit/collision/rearm/impact-sound/event behavior, exact source virtual names, concrete layouts, BEA patching, and rebuild parity remain separate proof.

Wave1012 (`round-vtable-boundary-wave1012`, `wave1012-readback-verified`) recovered the deferred shared CRound / CMissile-style slot-66 body and the table-base slot-0 body: `0x004d8e40 VFuncSlot_66_004d8e40` and `0x004d9910 VFuncSlot_00_004d9910`. The pass verified `0x004d9d10` is not a standalone function and preserved the separate `0x004d9d60 CEngine__InitRoundLaunchStateDefaults` boundary. Slot 66 uses DATA refs `0x005de934` and `0x005e3cac`, touches `this+0xe0/+0xe4/+0xe8/+0xec/+0xf0/+0x120`, and calls the active-reader/effect/transform helpers. Slot 0 uses DATA refs `0x005de82c` and `0x005e3ba4`, reads an event record, switches on `event_record+4`, and calls the target-selection, configured-projectile, launch-state default, and effect-transform helpers. Queue closure is `6238/6238 = 100.00%`; Wave911 focused progress remains `505/1408 = 35.87%`; expanded static surface progress is `707/1493 = 47.35%`; top-500 coverage remains `409/500 = 81.80%`. Verified backup: `G:\GhidraBackups\BEA_20260531-183252_post_wave1012_round_vtable_slot66_verified`. Runtime projectile/event/effect/active-reader/transform/dispatch behavior, exact source virtual names, concrete layouts, BEA patching, and rebuild parity remain separate proof.

Wave1020 (`projectile-burst-spawn-spine-review-wave1020`) re-read `0x004d9f30 CRound__UpdateEffectTransformByMode_004d9f30` and `0x004db150 CRound__SpawnConfiguredProjectile` as part of the projectile-burst spawn spine. The prior Wave495 effect-transform helper remains coherent with calls from `CRound__UpdateRoundAndTriggerLaunchEffect`, `VFuncSlot_39_004d8ae0`, `VFuncSlot_66_004d8e40`, and `VFuncSlot_00_004d9910`; the context spawn row still carries the configured projectile math/dispatch body. Wave1020 made no mutation and verified backup `G:\GhidraBackups\BEA_20260531-214433_post_wave1020_projectile_burst_spawn_spine_review_verified`. Runtime projectile behavior, exact CRound/round-config layouts, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

Wave1126 (`wave1126-projectile-collision-targeting-current-risk-review`, `wave1126-readback-verified`) re-read the score-23 projectile collision targeting current-risk cluster and tag-normalized the existing Wave495 CRound helper `0x004daba0 CRound__FindNearbyHostileWithinProjectileRadius` alongside `0x00425c60 CCollisionSeekingRound__FilterCollisionCandidateByTrajectory` and `0x00426920 CCollisionSeekingRound__ComputeScaledMapCellChebyshevDistance`. Fresh evidence preserves the Wave495 static body claim: this helper scans `CMapWho` around `this+0x1c/0x20/0x24`, uses radius from round-config `this+0xf0+0x90`, rejects the current target reader at `this+0xe8`, filters candidate flag bit `0x10` and excludes bit `0x04`, samples target world position, and returns the first candidate inside radius squared. The fresh Ghidra export evidence verified `3 rows`: `3` metadata rows, `3` tag rows, `7` xref rows, `291` instruction rows, and `3` decompile rows; dry/apply/final-dry added `19 tags` and updated two CollisionSeekingRound comments with no rename, signature, function-boundary, or executable-byte change. Current focused accounting is `138/1179 = 11.70%` of current focused candidates: 1179; live regenerated focused candidates: 1178; remaining active focused work: 1041; static closure remains `6410/6410 = 100.00%` with `0 / 0 / 0` debt. Verified backup: `G:\GhidraBackups\BEA_20260605-061135_post_wave1126_projectile_collision_targeting_current_risk_review_verified`; previous completed backup: `G:\GhidraBackups\BEA_20260605-053504_post_wave1125_carver_targeting_current_risk_review_verified`. Probe anchor: Wave919; Wave920; Wave1059; Wave495; comment/tag normalization; score-23 projectile collision targeting current-risk cluster. Runtime collision behavior, runtime targeting behavior, runtime projectile behavior, exact CRound/round-config/CMapWho/target layouts, exact source-body identity, BEA patching, visual QA, and rebuild parity remain separate proof.

Probe token anchor: Wave941; `missile-linked-object-dispatch-review-wave941`; `0x004baae0 CMissile__Init`; `0x004bac10 CMissile__DispatchLinkedObjectVFunc68AndPostHook`; `0x0050f8b0 CMissile__scalar_deleting_dtor`; `0x0050f8d0 CMissile__Destructor`; `0x0050f7a0 CWorldPhysicsManager__CreateProjectile`; `0x004d8410 CRound__Init`; `0x00452da0 SharedVFunc__NoOp_Ret08`; `0x005e3ba4`; `0x005e3ba8`; `0x005e3bc8`; `0x005e3cb8`; `0x005e3cc0`; `0x005de82c`; `0x005de850`; read-only review; `179/1408 = 12.71%`; `6113/6113 = 100.00%`; `G:\GhidraBackups\BEA_20260528-034712_post_wave941_missile_linked_object_dispatch_review_verified`.

Wave765 added saved static read-back comments/tags/signatures for adjacent Round.cpp unwind cleanup callbacks in the `0x005d4970 Unwind@005d4970` through `0x005d4a10 Unwind@005d4a10` range. Verified backup: `G:\GhidraBackups\BEA_20260523-155528_post_wave765_unwind_continuation_verified`. This remains static Ghidra evidence only; exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

Wave906 (`unit-battleengine-gameplay-static-review-wave906`) records a `static-coherent Unit/BattleEngine/gameplay core` after export-contract queue closure `6113/6113 = 100.00%` (static review slice only): `633` rows across `75` families, including `CUnit` `90`, `CUnitAI` `63`, `CBattleEngine` `47`, `CSquadNormal` `31`, `CBattleEngineWalkerPart` `27`, `CBattleEngineJetPart` `23`, `CGeneralVolume` `23`, `CDestructableSegmentsController` `19`, and `CCollisionSeekingRound` `17`; anchors include `CUnit__ApplyDamage`, `CUnitAI__UpdateActivationStateAndSpawnPickup`, `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`, `CBattleEngine__AddProjectile`, `CBattleEngine__Morph`, `CBattleEngine__HandleCloak`, `CBattleEngine__AugmentWeapon`, `CBattleEngineJetPart__WeaponFired`, `CBattleEngineWalkerPart__WeaponFired`, `CWeapon__HandleFireBurstEvent`, `CRound__SpawnConfiguredProjectile`, `CSpawnerThng__DoSpawn`, and `CDestroyableSegment__VFunc_03_ApplyDamage`. Verified backup: `G:\GhidraBackups\BEA_20260526-105331_post_wave906_unit_battleengine_gameplay_static_review_verified`.

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

`CRound` is the base projectile/round class used by the retail projectile creation path and by CMissile-derived paths. The current evidence ties it to the `CWorldPhysicsManager__CreateProjectile` allocation path, vtable `0x005de82c`, Round.cpp debug-path allocation sites, launch/effect scheduling, active-reader teardown, targeting/aim-state synchronization, projectile spawn chaining, trail-effect arming, and collision/heightfield setup.

## Vtable

Primary CRound vtable observed at `0x005de82c`:

| Slot | Address | Saved Ghidra function | Current status |
| ---: | --- | --- | --- |
| 0 | `0x004d9910` | `VFuncSlot_00_004d9910` | Wave1012 boundary recovery; shared by CRound vtable base `0x005de82c` and CMissile-style vtable base `0x005e3ba4`; SEH-framed event/switch dispatch body with exact source virtual name still unproven. |
| 1 | `0x004d8350` | `CRound__scalar_deleting_dtor` | Wave493 scalar-deleting destructor wrapper; calls shutdown helper, optional free by `flags & 1`, returns `this`. |
| 2 | `0x004d8dc0` | `VFuncSlot_02_004d8dc0` | Wave494 signature/comment hardening only; shared by CRound vtable `0x005de82c` and CMissile-style vtable `0x005e3ba4`; exact source virtual name remains unproven. |
| 9 | `0x004d8410` | `CRound__Init` | Wave493 init-slot hardening; copies CRoundInitThing-like fields, mutates init flags, allocates collision helpers, calls `CActor__Init`, schedules events/effects. |
| 15 | `0x004d82a0` | `VFuncSlot_15_004d82a0` | Wave493 signature/comment hardening only; shared by CRound vtable `0x005de82c` and CMissile-style vtable `0x005e3ba4`; exact source virtual name and scalar meaning remain unproven. |
| 16 | `0x004d8ac0` | `VFuncSlot_16_004d8ac0` | Wave1011 boundary recovery; shared by CRound vtable `0x005de82c` and CMissile-style vtable `0x005e3ba4`; scalar helper reads `this+0xf0` round-config fields and globals `0x005d8584` / `0x005d85ec`. |
| 39 | `0x004d8ae0` | `VFuncSlot_39_004d8ae0` | Wave1011 boundary recovery; shared by CRound vtable `0x005de82c` and CMissile-style vtable `0x005e3ba4`; hit/rearm/impact-sound/effect-transform/event-scheduling bridge. |
| 66 | `0x004d8e40` | `VFuncSlot_66_004d8e40` | Wave1012 boundary recovery; shared by CRound vtable `0x005de82c` and CMissile-style vtable `0x005e3ba4`; clears effect/reader links and updates transform/effect state before the separate slot-0 body starts. |

Additional Wave495 data/vtable-adjacent evidence:

| Table/ref | Address | Saved Ghidra function | Current status |
| --- | --- | --- | --- |
| `0x005de940` slot 0 | `0x004d9ef0` | `CRound__UpdateRoundAndTriggerLaunchEffect` | Wave495 corrected owner and comment after the downstream arm/trail helper proved CRound-local context. |
| `0x005e3cb8` slot 0 | `0x004d9ef0` | `CRound__UpdateRoundAndTriggerLaunchEffect` | Same update/launch-effect entry is shared by the adjacent CMissile-style table context. |

## Saved Functions

| Address | Saved Ghidra name | Signature / purpose |
| --- | --- | --- |
| `0x004d81e0` | `CRound__ctor` | `void * __thiscall CRound__ctor(void * this, void * init)`; called by `CWorldPhysicsManager__CreateProjectile` after `0x134`-byte allocation, installs CRound vtable/render-position table, stores init at `this+0xf0`, and seeds projectile state. |
| `0x004d82a0` | `VFuncSlot_15_004d82a0` | `double __fastcall ... (void * this)`; calls virtual slot `+0xb4`, returns a global `1.0`-like scalar when nonzero, otherwise returns round-config float at `this+0xf0 + 0x2c`. |
| `0x004d8350` | `CRound__scalar_deleting_dtor` | `void * __thiscall ... (void * this, int flags)`; scalar-deleting destructor wrapper. |
| `0x004d8370` | `CRound__ShutdownAndDetachReaders` | `void __fastcall ... (void * this)`; removes active-reader cells at `this+0xec` and `this+0xe8`, removes particle/effect link rooted at `this+0xe0`, then calls `CActor__dtor_base`. |
| `0x004d8410` | `CRound__Init` | `void __thiscall ... (void * this, void * init)`; init-slot implementation for base rounds, also called by `CMissile__Init`. |
| `0x004d8ac0` | `VFuncSlot_16_004d8ac0` | `double __fastcall ... (void * this)`; Wave1011 recovered boundary for shared slot 16 scalar/config helper. |
| `0x004d8ae0` | `VFuncSlot_39_004d8ae0` | `void __thiscall ... (void * this, void * other_thing, void * collision_report)`; Wave1011 recovered boundary for shared slot 39 hit/rearm/impact/effect/event bridge. |
| `0x004d8dc0` | `VFuncSlot_02_004d8dc0` | `void __fastcall ... (void * this)`; Wave494 shared CRound/CMissile slot-2 helper with source virtual name still unproven. |
| `0x004d8e40` | `VFuncSlot_66_004d8e40` | `void __fastcall ... (void * this)`; Wave1012 recovered boundary for shared slot 66 reader/effect/transform helper. |
| `0x004d9910` | `VFuncSlot_00_004d9910` | `void __thiscall ... (void * this, void * event_record)`; Wave1012 recovered boundary for shared slot 0 event/switch dispatch helper. |
| `0x004d9d60` | `CEngine__InitRoundLaunchStateDefaults` | `void __fastcall ... (void * this)`; Wave494 adjacent launch-state default initializer. |
| `0x004d9ef0` | `CRound__UpdateRoundAndTriggerLaunchEffect` | `void __fastcall ... (void * this)`; Wave495 corrected the stale owner and documented launch-effect dispatch through `CRound__ArmProjectileAndSpawnTrailEffect`. |
| `0x004d9f30` | `CRound__UpdateEffectTransformByMode_004d9f30` | `void __thiscall ... (void * this, int effectMode, void * context, void * targetOrOwner)`; effect transform helper with mode-dispatch and CInitThing/CExplosionInitThing-like stack payload construction. |
| `0x004daa20` | `CEngine__FindPresetIndexByName` | `int __cdecl ... (char * presetName)`; adjacent preset-list ordinal lookup through `DAT_008553f8`. |
| `0x004daab0` | `CRound__SetTargetReaderIfAllowed` | `void __thiscall ... (void * this, void * targetReader, int replaceExisting)`; active-reader target binding helper. |
| `0x004dab50` | `CRound__RemoveActiveReaderById` | `void __fastcall ... (void * this)`; active-reader removal/clear helper. |
| `0x004daba0` | `CRound__FindNearbyHostileWithinProjectileRadius` | `void * __fastcall ... (void * this)`; CMapWho radius query for candidate hostile target readers. |
| `0x004dac90` | `CRound__SelectBestTargetReaderAndSyncAimState` | `void __thiscall ... (void * this, void * eventPayload, void * unusedContext)`; aim-space target selection and event `0xfa3` scheduling helper. |
| `0x004db090` | `CRound__GetPresetScalarByConfigName` | `double __fastcall ... (void * this)`; round-config name lookup returning preset scalar `+0x38`. |
| `0x004db150` | `CRound__SpawnConfiguredProjectile` | `void __fastcall ... (void * this)`; configured projectile spawn helper that builds a CRoundInitThing-like payload. |
| `0x004db630` | `CRound__ArmProjectileAndSpawnTrailEffect` | `void __fastcall ... (void * this)`; launch-state, velocity, and configured trail-effect arming helper. |

## Partial Layout Signals

Observed fields are layout clues, not final structures:

| Offset | Observed role |
| --- | --- |
| `this+0xe0` | Particle/effect link root removed during shutdown and used for launch effect creation. |
| `this+0xe8` | Active-reader cell removed during shutdown. |
| `this+0xec` | Active-reader/candidate cell removed during shutdown. |
| `this+0xf0` | Stored init/round-config pointer used by slot 15 and `CRound__Init`. |
| `this+0xf4` | Timestamp/current-time seed from `DAT_00672fd0`. |
| `this+0x108..0x118` | Destination/jump/lifespan-style state copied from `init+0x3bc..0x3cc`. |
| `this+0x108..0x114` | Wave495 aim/target position state written by `CRound__SelectBestTargetReaderAndSyncAimState`; overlaps with destination-style state depending call path, exact layout remains open. |
| `this+0x12c` | Launch/armed flag set by `CRound__ArmProjectileAndSpawnTrailEffect`. |
| `this+0x130` | Constructor-seeded flag also checked by target-reader selection. |
| `this+0x120`, `this+0x124`, `this+0x12c`, `this+0x130` | Constructor-seeded state flags/counters; exact field names remain unproven. |

## Source / Header Bridge

The available source snapshot does not currently include the full `Round.cpp` body. `references/Onslaught/InitThing.h` does expose `CRoundInitThing` with `mDest`, `mJumpsPerformed`, `mRoundData`, `mInitialDelay`, and `mLifeSpan`, which matches the kind of init payload used by the retail `CRound__Init` reads. Retail Ghidra evidence remains the authority for offsets and behavior.

## Wave493 Evidence

- Apply script: `tools/ApplyRoundWave493.java`
- Probe: `tools/ghidra_round_wave493_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave493-round-core-004d81e0/`
- Dry/apply/verify summaries:
  - Dry: `updated=0 skipped=5 created=0 would_create=0 renamed=0 would_rename=2 missing=0 bad=0`
  - Apply: `updated=5 skipped=0 created=0 would_create=0 renamed=2 would_rename=0 missing=0 bad=0`
  - Verify dry: `updated=0 skipped=5 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post-readback verified `9` metadata rows, `9` tag rows, decompile/xref/instruction/vtable exports, focused probe PASS, npm probe PASS, queue refresh PASS, and Ghidra backup `G:\GhidraBackups\BEA_20260517-090622_post_wave493_round_verified`.

## Wave494 Evidence

- Apply script: `tools/ApplyCollisionRoundTailWave494.java`
- Probe: `tools/ghidra_collision_round_tail_wave494_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave494-collision-round-tail-004d8a50/`
- Dry/apply/verify summaries:
  - Dry: `updated=0 skipped=7 created=0 would_create=0 renamed=0 would_rename=3 missing=0 bad=0`
  - Apply: `updated=7 skipped=0 created=0 would_create=0 renamed=3 would_rename=0 missing=0 bad=0`
  - Verify dry: `updated=0 skipped=7 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post-readback verified CRound vtable `0x005de82c` slot 2 -> `0x004d8dc0`, CMissile-style vtable `0x005e3ba4` slot 2 -> `0x004d8dc0`, `0x004d9ef0` data refs at `0x005de940` and `0x005e3cb8`, focused probe PASS, npm probe PASS, queue refresh PASS, and Ghidra backup `G:\GhidraBackups\BEA_20260517-093427_post_wave494_collision_round_tail_verified`.

## Wave495 Evidence

- Apply script: `tools/ApplyProjectileSpawnTailWave495.java`
- Probe: `tools/ghidra_projectile_spawn_tail_wave495_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave495-projectile-spawn-tail-004d9f30/`
- Dry/apply/verify summaries:
  - Initial dry: `updated=0 skipped=9 created=0 would_create=0 renamed=0 would_rename=6 missing=0 bad=0`
  - Initial apply: `updated=9 skipped=0 created=0 would_create=0 renamed=6 would_rename=0 missing=0 bad=0`
  - Initial verify dry: `updated=0 skipped=9 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
  - Corrective dry: `updated=0 skipped=10 created=0 would_create=0 renamed=0 would_rename=1 missing=0 bad=0`
  - Corrective apply: `updated=1 skipped=9 created=0 would_create=0 renamed=1 would_rename=0 missing=0 bad=0`
  - Corrective verify dry: `updated=0 skipped=10 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post-readback verified `13` context metadata rows, `13` tag rows, `28` xref rows, `16` vtable rows, `13` decompile exports, focused probe PASS, npm probe PASS, queue refresh PASS, and Ghidra backup `G:\GhidraBackups\BEA_20260517-101321_post_wave495_projectile_spawn_tail_verified`.

## Wave765 Unwind Continuation

Wave765 static read-back (`unwind-continuation-wave765`, `wave765-readback-verified`) hardened Round.cpp-adjacent compiler-generated SEH unwind callbacks as `void __cdecl Unwind@...(void)` without renames or boundary changes.

| Address | Evidence |
| --- | --- |
| `0x005d4970 Unwind@005d4970` | DATA xref `0x0061d1e4`; `OID__FreeObject_Callback(*(EBP-0x8c))` with Round.cpp debug path `0x00631d38`, line token `0x62`, allocation/type value `0x0d`. |
| `0x005d4989 Unwind@005d4989` | DATA xref `0x0061d1ec`; `OID__FreeObject_Callback(*(EBP-0x8c))`, line token `0x6c`, allocation/type value `0x0b`. |
| `0x005d49a2 Unwind@005d49a2` | DATA xref `0x0061d1f4`; `CCollisionSeekingRound__Destructor(*(EBP-0x8c))`. |
| `0x005d49ad Unwind@005d49ad` | DATA xref `0x0061d1fc`; `CLine__SetBaseVtable_00426360(EBP-0x40)`. |
| `0x005d49c0 Unwind@005d49c0` | DATA xref `0x0061d224`; `CCollisionSeekingRound__Destructor(*(EBP-0x10))`. |
| `0x005d49e0 Unwind@005d49e0` | DATA xref `0x0061d24c`; `CLine__SetBaseVtable_00426360(EBP-0x78)`. |
| `0x005d49e8 Unwind@005d49e8` | DATA xref `0x0061d254`; `OID__FreeObject_Callback(*(EBP-0x7c))`, line token `0x213`, allocation/type value `0x0b`. |
| `0x005d4a10 Unwind@005d4a10` | DATA xref `0x0061d27c`; `CLine__SetBaseVtable_00426360(EBP-0x40)`. |

## Remaining Gaps

- Exact source virtual names and full `Round.cpp` source-body identity.
- Concrete `CRound`, `CRoundInitThing`, `CRoundData`, active-reader, preset-list, and effect/trail layouts.
- Meaning of slot 15 scalar return, slot 2 source identity, launch/update table ownership, and adjacent still-unrecovered vtable slots.
- Runtime projectile spawn, targeting, collision, trail/effect behavior, BEA launch behavior, game patching, and rebuild parity.
