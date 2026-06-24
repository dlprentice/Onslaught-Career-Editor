# ParticleManager.cpp Functions

Wave1172 current-risk update: Wave1172 (`wave1172-message-particle-global-list-cleanup-current-risk-review`) re-read `0x004cb040 ParticleEffectLink__PushGlobalList` and `0x004cb050 CParticleManager__RemoveFromGlobalList` from the active current-risk denominator with fresh Ghidra export evidence and no mutation. The same wave also covers `CMessage__scalar_deleting_dtor` and `CMessage__dtor_base`; it accounts for `4 message/particle global-list current-risk rows`. Current focused accounting is `672/1179 = 57.00%`, remaining active focused work: 507, current focused candidates: 1178, live regenerated current focused candidates: 1178, current risk candidates: 6166. Fresh exports verified `90 xref rows` and `64 instruction rows`; Codex read-only consult used; backup `G:\GhidraBackups\BEA_20260606-071000_post_wave1172_message_particle_global_list_cleanup_current_risk_review_verified`. Runtime particle/global-list behavior, exact particle/manager/link-node layout, exact source-body identity, and rebuild parity remain separate proof.

Wave1150 current-risk update: Wave1150 (`wave1150-particle-set-render-tail-current-risk-review`) accounts for `11 current-risk rows` from the Wave1108 current focused current-risk denominator as a particle set/render tail current-risk review. It uses fresh Ghidra export evidence for particle parent-transform/link, simple-sprite vfunc 10/23, selector child vfunc dispatch, ParticleSet destructor/type init/load/name lookup, and manager offset +0x3c/+0x40 unlink helper, and is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, and no Codex subagent. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused remains `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `355/1179 = 30.11%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 824; focused threshold `15`; not Wave911 reconstruction. Verified backup: `G:\GhidraBackups\BEA_20260605-194926_post_wave1150_particle_set_render_tail_current_risk_review_verified`; previous completed backup: `G:\GhidraBackups\BEA_20260605-192706_post_wave1149_particle_effects_score20_current_risk_review_verified`. Runtime particle behavior, runtime effect/render behavior, runtime particle descriptor loading, runtime ParticleSet loading, exact particle/descriptor/manager/handle/set layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof. Probe token anchor: Wave1150; wave1150-particle-set-render-tail-current-risk-review; 355/1179 = 30.11%; 11 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 824; current risk candidates: 6166; particle set/render tail current-risk review; fresh Ghidra export; particle parent-transform/link, simple-sprite vfunc 10/23, selector child vfunc dispatch, ParticleSet destructor/type init/load/name lookup, and manager offset +0x3c/+0x40 unlink helper; read-only review; no mutation; no Codex subagent; 0 / 0 / 0; 6411/6411 = 100.00%; CParticle__ApplyParentTransformOrStoreLink; CPDSimpleSprite__VFunc_10_004c14f0; CPDSimpleSprite__VFunc_23_004c8040; CParticleSet__shared_scalar_deleting_dtor; CPDSelector__DispatchChildVFunc20; CParticleSet__InitType11; CParticleSet__InitType12; CParticleSet__InitType13; CParticleSet__FindByNameAndTrackLinkSlot; CParticleSet__LoadParticleSetFile; CParticleManager__UnlinkNodeByOffset3C40; G:\GhidraBackups\BEA_20260605-194926_post_wave1150_particle_set_render_tail_current_risk_review_verified; G:\GhidraBackups\BEA_20260605-192706_post_wave1149_particle_effects_score20_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Wave1149 current-risk update: Wave1149 (`wave1149-particle-effects-score20-current-risk-review`) accounts for `15 current-risk rows` from the Wave1108 current focused current-risk denominator as a particle/effects score20 current-risk review. It uses fresh Ghidra export evidence for particle descriptor update/load, engine burst/tint, particle manager handles/effects/update/distance/list, and ParticleSet factory/init helpers, and is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, and no Codex subagent. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused remains `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `344/1179 = 29.18%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 835; focused threshold `15`; not Wave911 reconstruction. Verified backup: `G:\GhidraBackups\BEA_20260605-192706_post_wave1149_particle_effects_score20_current_risk_review_verified`; previous completed backup: `G:\GhidraBackups\BEA_20260605-185756_post_wave1148_battleengine_walker_control_score20_current_risk_review_verified`. Runtime particle behavior, runtime effect/render behavior, runtime particle descriptor loading, runtime ParticleSet loading, exact particle/descriptor/manager/handle/set layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof. Probe token anchor: Wave1149; wave1149-particle-effects-score20-current-risk-review; 344/1179 = 29.18%; 15 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 835; current risk candidates: 6166; particle/effects score20 current-risk review; fresh Ghidra export; particle descriptor update/load, engine burst/tint, particle manager handles/effects/update/distance/list, and ParticleSet factory/init helpers; read-only review; no mutation; no Codex subagent; 0 / 0 / 0; 6411/6411 = 100.00%; CEngine__ConfigureParticleBurstForDistance; CParticleDescriptor__Update; CParticleDescriptor__Load; CEngine__ComputeSpriteTintByDistance; CParticleManager__SetParticleResource; CParticleManager__CleanupHandles; ParticleEffectLink__SetHandleStateAndClear; CParticleManager__InterpolatePositions; CParticleManager__CreateEffect; CParticleManager__UpdateParticleAndRecycleIfDead; CParticleManager__ProjectPointToTerrainWithRadiusClamp; CParticleManager__ComputeMinCameraDistanceSqForParticle; CParticleManager__DestroyParticleList; CParticleSet__CreateByType; CParticleSet__Init; G:\GhidraBackups\BEA_20260605-192706_post_wave1149_particle_effects_score20_current_risk_review_verified; G:\GhidraBackups\BEA_20260605-185756_post_wave1148_battleengine_walker_control_score20_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

> Source File: ParticleManager.cpp | Binary: BEA.exe
> Debug Path: `0x00630e60`

## Overview

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

ParticleManager owns the runtime visual-effect particle pool, active-particle lists, effect handles, terrain projection helper, and camera-distance LOD helper. Wave463 refreshed the saved Ghidra signatures/comments/tags for the core manager cluster from retail static evidence, Wave477 corrected the nearby owner-link helper that writes effect-handle state, Wave478 hardened the global nonempty-manager list link/unlink pair at offsets `+0x3c/+0x40`, Wave822 hardened the owner-link cleanup/push/prune/render-node tail, and Wave994 corrected the stale `unused_context` parameter on the core per-particle update/recycle helper.

Source-body identity remains limited: the current `references/Onslaught` snapshot does not include ParticleManager source files, so these names are behavior-backed retail-binary labels rather than source-parity proof.

Wave905 static review (`mesh-motion-world-particle-static-review-wave905`) records a `static-coherent mesh/motion/world/particle core` after export-contract queue closure `6113/6113 = 100.00%` (static review slice only): `506` rows across `41` families, including `CMeshPart` `54`, `CMesh` `40`, `CWorld` `38`, `CWorldPhysicsManager` `32`, `CThing` `28`, `CParticleManager` `23`, and `CMeshCollisionVolume` `21`; anchors include `CThing__InitRenderThingFromInitMeshName`, `CMesh__LoadByNameWithStatus`, `CMeshPart__PopulatePoseCacheRecursive`, `CWorld__InitOccupancyBitplanes`, `CWorldPhysicsManager__CreateThingByType`, `CParticleManager__Update`, `CParticleSet__LoadFromArchive`, and `CParticleDescriptor__Load`; mesh bridge counts include `213/213` loose meshes, `139/139` embedded meshes, and `352/352` model material/texture-binding rows. Verified backup: `G:\GhidraBackups\BEA_20260526-103409_post_wave905_mesh_motion_world_particle_static_review_verified`.

Wave1118 (`wave1118-particle-message-current-risk-review`) re-read the particle-manager current-risk head with a fresh read-only Ghidra export and no mutation: `0x004cae50 CParticle__Destroy`, `0x004cb0e0 CParticleManager__Init`, `0x004cb1b0 CParticleManager__Shutdown`, `0x004cb210 CParticleManager__Update`, `0x004cb5c0 CParticleManager__AllocateParticle`, `0x004cbca0 CParticleManager__UpdateParticles`, and `0x004cbe30 CParticleManager__PruneDeadParticles`. Fresh evidence preserves the Wave463 pool/list/lifetime contracts, including the `0x200` entry pool, `0xd8` byte particle nodes, active-list update/prune handoffs, `CParticle__Destroy`, and manager `+0x1c/+0x8` live/free counts. Current focused accounting moves to `100/1179 = 8.48%`; verified backup `G:\GhidraBackups\BEA_20260605-021103_post_wave1118_particle_message_current_risk_review_verified`. Runtime particle behavior, exact manager/particle/handle/list layouts, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

Wave1120 (`wave1120-mixed-score25-current-risk-review`) re-read `0x00405d80 CParticleManager__RemoveFromGlobalList_Thunk` with a fresh read-only Ghidra export and no mutation. The row remains a jump thunk to `0x004cb050 CParticleManager__RemoveFromGlobalList`; xrefs include many compiler unwind cleanup callbacks plus CWeapon/OID/CFEPDebriefing DATA contexts. The saved tag row is still empty on this older function, so Wave1120 documents that tag gap rather than normalizing it. Current focused accounting moves to `118/1179 = 10.01%`; verified backup `G:\GhidraBackups\BEA_20260605-025952_post_wave1120_mixed_score25_current_risk_review_verified`. Runtime particle/list behavior, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

## Functions

| Address | Name | Purpose | Evidence |
| --- | --- | --- | --- |
| `0x004c0510` | `CParticleManager__AppendNodeToActiveList` | Appends a particle/list node to the manager active list, linking the manager into the global nonempty-manager chain when the list was empty. | Wave468 |
| `0x004c0560` | `CParticleManager__UnlinkNodeFromActiveList` | Unlinks a selected active-list node, clears neighbor links/current-node state, and removes the manager from the global nonempty-manager chain when the active list empties. | Wave468 |
| `0x004cae50` | `CParticle__Destroy` | Frees a particle's `+0x88` resource block, dispatches the observed resource vfunc `+0x38`, and unlinks owner handle state at `+0x58`. | Wave463 |
| `0x004caed0` | `CParticleManager__SetParticleResource` | Replaces the particle resource allocation at `+0x88` with an `OID__AllocObject(..., 0xc2)` allocation sized by the caller. | Wave463 |
| `0x004caf60` | `CParticleManager__CleanupHandles` | Walks `DAT_0082b3e4`, advances handle state at `+0xb4`, and frees handles whose activity flag at `+0xa4` is clear. | Wave463 |
| `0x004cb0e0` | `CParticleManager__Init` | Allocates the `0x1b004` backing block, links `0x200` `0xd8`-byte particles into the free list, links the manager globally, and increments `DAT_0082b3ec`. | Wave463 |
| `0x004cb1b0` | `CParticleManager__Shutdown` | Destroys the particle array with callback cleanup, frees the backing allocation, releases the next manager pointer, and decrements `DAT_0082b3ec`. | Wave463 |
| `0x004cb210` | `CParticleManager__Update` | Clamps/stores delta time, clears handle activity/backlinks, updates active particles, dispatches render-node callbacks, prunes dead particles, clears stale owner links, and runs handle cleanup. | Wave463 |
| `0x004cb300` | `CParticleManager__InterpolatePositions` | Walks active effect handles from `DAT_0082b3e8`, handles the `10000.0` sentinel, and updates render interpolation state through `DAT_008a9e44`. | Wave463 |
| `0x004cb3d0` | `CParticleManager__CreateEffect` | Allocates a particle, stores spawn vector fields, optionally creates a `0xb8` effect handle, links it into `DAT_0082b3e4`, and sets looping/high-priority flags. | Wave463 |
| `0x004cb5c0` | `CParticleManager__AllocateParticle` | Allocates/recycles a particle from the manager pool, applies observed LOD skip thresholds, dispatches particle-set vfunc `+0x24`, and links active/free lists. | Wave463 |
| `0x004cb920` | `CParticleManager__UpdateParticleAndRecycleIfDead` | Updates one particle, refreshes attached-handle activity/backlink fields, dispatches particle vfunc `+0x28`, and recycles dead particles; Wave994 corrected the signature to `void __thiscall CParticleManager__UpdateParticleAndRecycleIfDead(void * this, void * particle)`. | Wave463, Wave994 |
| `0x004cba30` | `CParticleManager__ProjectPointToTerrainWithRadiusClamp` | Samples static-shadow terrain height and writes a clamped output point when the source point is within the radius threshold. | Wave121, Wave463 |
| `0x004cba90` | `CParticleManager__ComputeMinCameraDistanceSqForParticle` | Computes minimum camera-distance-squared for a particle, including multiplayer camera 0/1 handling and attachment offset at `+0x58`. | Wave121, Wave463 |
| `0x004cbca0` | `CParticleManager__UpdateParticles` | Walks an active particle list, maintains handle state/backlinks, dispatches vfunc `+0x54`, updates lifetime/position, and observes the death flag under `DAT_009c63fc`. | Wave463 |
| `0x004cbe30` | `CParticleManager__PruneDeadParticles` | Recounts live particles at manager `+0x1c`, unlinks death-flagged particles, calls `CParticle__Destroy`, and recycles nodes to the free list at manager `+0x8`. | Wave463 |
| `0x004cbff0` | `CParticleManager__DestroyParticleList` | Repeatedly destroys every node in a head-linked particle list by preserving the next pointer and dispatching vfunc slot 0 with delete flag `1`. | Wave120, Wave463 |

## Related Helpers

| Address | Name | Purpose |
| --- | --- | --- |
| `0x004caf30` | `CParticleManager__ClearParticleOwnerBacklinks` | Iterates effect handles and clears owner activity/backlink fields at `+0xa4/+0xa8`. Wave822 particle manager owner links saved `void __cdecl CParticleManager__ClearParticleOwnerBacklinks(void)`. |
| `0x004cb040` | `ParticleEffectLink__PushGlobalList` | Wave822 corrected old `CWorldPhysicsManager__PushNodeGlobalList` to a shared ECX-node fastcall helper that pushes an effect/owner-link node into `DAT_0082b3e8`: `void __fastcall ParticleEffectLink__PushGlobalList(void * link_node)`. |
| `0x004cb050` | `CParticleManager__RemoveFromGlobalList` | Removes a manager from the global manager list. |
| `0x004cb080` | `CParticleManager__PruneDeadOwnerLinks` | Walks the effect/owner-link list and nulls link pointers whose linked activity flag has cleared. Wave822 saved `void __cdecl CParticleManager__PruneDeadOwnerLinks(void)`. |
| `0x004cb0b0` | `ParticleEffectLink__SetHandleStateAndClear` | Reads an owner-link cell's handle at `this+0x4`, writes handle state `+0xb4` to `1` or `2`, and clears the link cell; reached from CUnit, BattleEngine, Mine, raw cleanup, and projectile contexts. |
| `0x004cbc60` | `CParticleManager__UpdateRenderNodesAndResetState` | Runs render-node update callbacks on observed type `0xb` entries and restores render-state slot `0xf`. Wave822 saved `void __cdecl CParticleManager__UpdateRenderNodesAndResetState(void)`. |
| `0x004cdba0` | `CParticleManager__LinkNodeByOffset3C40` | Appends a manager/list node into an owner list's head/tail fields at `+0x4/+0x8` using node links at `+0x3c/+0x40`; observed from `CParticleManager__AppendNodeToActiveList` with ECX set to global owner `0x0082b400`. |
| `0x004cdbe0` | `CParticleManager__UnlinkNodeByOffset3C40` | Unlinks a manager/list node from the owner head/tail fields at `+0x4/+0x8` through node links at `+0x3c/+0x40`, then clears the node links; observed from `CParticleManager__UnlinkNodeFromActiveList`. |

## Wave1014 ParticleSet Load Lifecycle Read-Back

Wave1014 static re-audit (`particle-set-load-lifecycle-review-wave1014`) re-read the ParticleSet load/factory/lifecycle spine with ParticleManager context. For this file, the focused bridge rows are `0x004cdba0 CParticleManager__LinkNodeByOffset3C40` and `0x004cdbe0 CParticleManager__UnlinkNodeByOffset3C40`, with context `0x004c0510 CParticleManager__AppendNodeToActiveList`, `0x004c0560 CParticleManager__UnlinkNodeFromActiveList`, `0x004cb0e0 CParticleManager__Init`, `0x004cb1b0 CParticleManager__Shutdown`, `0x004cb210 CParticleManager__Update`, `0x004cb5c0 CParticleManager__AllocateParticle`, `0x004cb920 CParticleManager__UpdateParticleAndRecycleIfDead`, and `0x004cbff0 CParticleManager__DestroyParticleList`.

Fresh target exports verified `13` metadata rows, `13` tag rows, `79` xref rows, `997` body-instruction rows, and `13` decompile rows across the Wave1014 target set. Context exports verified `16` metadata rows, `54` xref rows, `1206` body-instruction rows, and `16` decompile rows. The xrefs still tie `CParticleManager__LinkNodeByOffset3C40` to `CParticleManager__AppendNodeToActiveList` and `CParticleManager__UnlinkNodeByOffset3C40` to `CParticleManager__UnlinkNodeFromActiveList`; no rename or signature change was justified.

No mutation, rename, signature change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation was needed. Export-contract closure remains `6238/6238 = 100.00%`; Wave911 focused progress remains `505/1408 = 35.87%`; expanded static surface progress is `729/1493 = 48.83%`; Wave911 top-500 risk-ranked coverage is `431/500 = 86.20%`. Verified backup: `G:\GhidraBackups\BEA_20260531-191245_post_wave1014_particle_set_load_lifecycle_review_verified`. Probe token anchor: Wave1014; particle-set-load-lifecycle-review-wave1014; 0x004cc020 CParticleSet__CreateByType; 0x004cc850 CParticleSet__Init; 0x004ccb40 CParticleSet__shared_scalar_deleting_dtor; 0x004ccc50 CPDSelector__DispatchChildVFunc20; 0x004cd290 CParticleSet__InitType11; 0x004cd2d0 CParticleSet__InitType12; 0x004cd3c0 CParticleSet__InitType13; 0x004cd7f0 CParticleSet__LoadFromArchive; 0x004cda60 CParticleSet__LoadParticleSetFile; 0x004cdbe0 CParticleManager__UnlinkNodeByOffset3C40; 505/1408 = 35.87%; 729/1493 = 48.83%; 431/500 = 86.20%; 6238/6238 = 100.00%; G:\GhidraBackups\BEA_20260531-191245_post_wave1014_particle_set_load_lifecycle_review_verified; no mutation.

This is static retail Ghidra evidence only. Runtime particle/effect behavior, exact manager/particle/handle/list layouts, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

## Wave994 Core Update/Recycle Read-Back

Wave994 ParticleManager core review (`particle-manager-core-review-wave994`, `wave994-readback-verified`) saved one signature/comment/tag correction at `0x004cb920 CParticleManager__UpdateParticleAndRecycleIfDead`: the saved signature is now `void __thiscall CParticleManager__UpdateParticleAndRecycleIfDead(void * this, void * particle)`, removing the stale `unused_context` parameter from the Wave463 signature. Instruction evidence at `0x004cb924` reads the single stack argument after local stack setup and `PUSH ESI`, ECX is copied to the manager receiver, and the body returns with `RET 0x4` at `0x004cba27`.

Read-back evidence: dry/apply/final dry reported `updated=0 skipped=1 signature_updated=1 comment_only_updated=0 tags_added=3 missing=0 bad=0`, then `updated=1 skipped=0 signature_updated=1 comment_only_updated=0 tags_added=3 missing=0 bad=0`, then `updated=0 skipped=1 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`. Post exports verified `14` metadata rows, `14` tag rows, `120` xref rows, `1130` body-instruction rows, and `14` decompile rows. Queue closure remains `6222/6222 = 100.00%`; Wave911 focused re-audit progress is `461/1408 = 32.74%`; expanded static surface progress is `563/1478 = 38.09%`; verified backup `G:\GhidraBackups\BEA_20260531-070007_post_wave994_particle_manager_core_review_verified`.

This is static retail Ghidra evidence only. Runtime particle behavior, exact manager/particle/handle layouts, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

## Wave822 Read-Back

Wave822 particle manager owner links (`particle-manager-owner-links-wave822`, `wave822-readback-verified`) saved comments/tags/signatures for `0x004caf30 CParticleManager__ClearParticleOwnerBacklinks`, `0x004cb040 ParticleEffectLink__PushGlobalList`, `0x004cb080 CParticleManager__PruneDeadOwnerLinks`, and `0x004cbc60 CParticleManager__UpdateRenderNodesAndResetState`. The pass corrected the old `CWorldPhysicsManager__PushNodeGlobalList` name/signature at `0x004cb040`: instruction/decompile evidence shows ECX carries `link_node`, the body writes the old `DAT_0082b3e8` head to `link_node+0`, and no stack parameter is read. It made no function-boundary changes and no executable-byte changes.

Read-back evidence: dry `updated=0 skipped=4 renamed=0 would_rename=1 signature_updated=4 comment_only_updated=0 missing=0 bad=0`; apply `updated=4 skipped=0 renamed=1 would_rename=0 signature_updated=4 comment_only_updated=0 missing=0 bad=0`; final dry `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`. Post exports verified 4 metadata rows, 4 tag rows, 46 xref rows, 1684 target instruction rows, 2353 helper instruction rows, 13 helper metadata rows, and 4 decompile rows. Queue after Wave822: `6098` total, `5626` commented, `472` commentless, `0` exact-undefined signatures, `0` `param_N`, strict proxy `5626/6098 = 92.26%`; next raw commentless row `0x004cd7a0 CWorldPhysicsManager__FindNodeByNameGE`; verified backup `G:\GhidraBackups\BEA_20260524-180249_post_wave822_particle_manager_owner_links_verified`.

This is static retail Ghidra evidence only. Exact effect-handle/link-node/render-node/owner layouts, exact source-body identity, runtime particle shutdown behavior, runtime particle/effect behavior, runtime render behavior, BEA patching, and rebuild parity remain deferred.

## Wave478 Read-Back

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave478-engine-queue-head-004cdbe0/`
- Apply script: `tools/ApplyParticleManagerListWave478.java`
- Probe: `tools/ghidra_particle_manager_list_wave478_probe.py`
- Test alias: `npm run test:ghidra-particle-manager-list-wave478`
- Initial dry summary: `updated=0 skipped=2 created=0 would_create=0 renamed=0 would_rename=1 missing=0 bad=0`
- Initial apply issue: `updated=0 skipped=0 created=0 would_create=0 renamed=1 would_rename=0 missing=0 bad=2`
- Corrected apply summary: `updated=2 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=2 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Read-back verified `0x004cdba0` and `0x004cdbe0` metadata/tag/decompile rows, the sibling link/unlink disassembly range `0x004cdba0..0x004cdc22`, callsites `0x004c0520` and `0x004c05b4`, and focused probe status `PASS`.
- The initial apply issue was a Ghidra `__thiscall` parameter-modeling mismatch; the corrected script models ECX as `this` and final read-back is clean.
- Verified backup: `G:\GhidraBackups\BEA_20260517-013642_post_wave478_particle_manager_list_verified` (`19` files, `157256583` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`).

## Wave748 Unwind Continuation Read-Back

Wave748 unwind continuation saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for particle-manager cleanup callbacks at `0x005d20f0 Unwind@005d20f0` and `0x005d2130 Unwind@005d2130`. The rows have scope-table DATA xrefs `0x0061afbc` and `0x0061b014`; decompile/instruction evidence calls `CParticleManager__RemoveFromGlobalList_Thunk` on stack-local manager/list nodes at `EBP-0x90` and `EBP-0x74`.

The same `unwind-continuation-wave748` tranche spans `0x005d1fc8 Unwind@005d1fc8` through `0x005d222b Unwind@005d222b`, with verified backup `G:\GhidraBackups\BEA_20260522-183258_post_wave748_unwind_continuation_verified`. Next high-signal queue head is `0x005d2250 Unwind@005d2250`; earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.

This is saved static retail Ghidra evidence only. Exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Wave761 Unwind Continuation Read-Back

Wave761 static read-back (`unwind-continuation-wave761`, `wave761-readback-verified`) saved ParticleManager.cpp-adjacent cleanup callbacks including `0x005d4070 Unwind@005d4070` through `0x005d40d0 Unwind@005d40d0` as `void __cdecl Unwind@...(void)` compiler-generated SEH unwind allocation-cleanup rows. DATA scope-table xrefs `0x0061cc0c`, `0x0061cc34`, and `0x0061cc5c` point at `OID__FreeObject_Callback` bodies using the ParticleManager.cpp debug path at `0x00630e60`, line token `0x10`, and allocation/type values `0x1a6`, `0x2c0`, and `0x2e2`. The same wave also saved `0x005d3fe8 Unwind@005d3fe8`, which jumps to `CParticleManager__RemoveFromGlobalList_Thunk` on object field `(*(EBP-0x10))+0x7c`. Verified backup: `G:\GhidraBackups\BEA_20260523-140318_post_wave761_unwind_continuation_verified`. This is saved static retail Ghidra evidence only; exact parent source-body identity, runtime particle/list cleanup behavior, runtime exception behavior, BEA patching, and rebuild parity remain deferred.

## Wave760 Unwind Continuation Read-Back

Wave760 static read-back (`unwind-continuation-wave760`, `wave760-readback-verified`) saved `0x005d3eeb Unwind@005d3eeb` as a `void __cdecl Unwind@005d3eeb(void)` compiler-generated SEH unwind particle-list cleanup callback. DATA scope-table xref `0x0061ca84` points at the body; instruction/decompile evidence jumps to `CParticleManager__RemoveFromGlobalList_Thunk` on object field `(*(EBP+0x4))+0x7c`. Verified backup: `G:\GhidraBackups\BEA_20260523-133538_post_wave760_unwind_continuation_verified`. This is saved static retail Ghidra evidence only; exact parent source-body identity, runtime particle/list cleanup behavior, runtime exception behavior, BEA patching, and rebuild parity remain deferred.

## Wave477 Read-Back

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave477-unit-finalize-linked-state-004cb0b0/`
- Apply script: `tools/ApplyParticleEffectLinkWave477.java`
- Comment refresh script: `tools/ApplyParticleEffectLinkCommentRefreshWave477.java`
- Probe: `tools/ghidra_particle_effect_link_wave477_probe.py`
- Test alias: `npm run test:ghidra-particle-effect-link-wave477`
- Dry summary: `updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=1 missing=0 bad=0`
- Apply summary: `updated=1 skipped=0 created=0 would_create=0 renamed=1 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Comment-refresh apply summary: `updated=3 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Read-back verified target metadata/tag/decompile rows, refreshed comments/tags on `0x0047cea0`, `0x004ba490`, and `0x004f84e0`, key xrefs from Mine/CUnit/BattleEngine/raw/projectile contexts, `RET 0x4` epilogues, the raw caller range at `0x004c570f..0x004c5725`, and focused probe status `PASS`.
- Verified backup: `G:\GhidraBackups\BEA_20260517-010555_post_wave477_particle_effect_link_verified` (`19` files, `157223815` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`).

## Wave468 Read-Back

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave468-cunitai-particle-current/`
- Apply script: `tools/ApplyParticleDescriptorWave468.java`
- Probe: `tools/ghidra_particle_descriptor_wave468_probe.py`
- Test alias: `npm run test:ghidra-particle-descriptor-wave468`
- Dry summary: `updated=0 skipped=5 created=0 would_create=0 renamed=0 would_rename=3 missing=0 bad=0`
- Apply summary: `updated=5 skipped=0 created=0 would_create=0 renamed=3 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=5 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Read-back verified `5` metadata rows, `5` tag rows, `22` xref rows, `5` target decompile exports plus `index.tsv`, `1105` focused instruction rows, `13` RTTI type rows, `416` vtable-slot rows, and focused probe status `PASS`.
- Corrected `CParticleManager__LinkNodeFront` to `CParticleManager__AppendNodeToActiveList`.
- Corrected `CEngine__RemoveNodeFromActiveList` to `CParticleManager__UnlinkNodeFromActiveList`.
- Verified backup: `G:\GhidraBackups\BEA_20260516-210736_post_wave468_particle_descriptor_verified` (`19` files, `157125511` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`).

## Wave463 Read-Back

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave463-particle-manager-current/`
- Apply script: `tools/ApplyParticleManagerWave463.java`
- Probe: `tools/ghidra_particle_manager_wave463_probe.py`
- Test alias: `npm run test:ghidra-particle-manager-wave463`
- Dry summary: `updated=0 skipped=17 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Apply summary: `updated=17 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=17 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Read-back verified `17` metadata rows, `17` tag rows, `95` xref rows, `17` target decompile exports plus `index.tsv`, `1037` focused instruction rows, and focused probe status `PASS`.
- Verified backup: `G:\GhidraBackups\BEA_20260516-185524_post_wave463_particle_manager_verified` (`19` files, `157059975` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`).

## Key Observations

- The manager pool contains `0x200` particles, each `0xd8` bytes, inside a `0x1b004` backing allocation.
- Effect handles are `0xb8` bytes and are linked through `DAT_0082b3e4`.
- Manager count and manager-chain state are tracked through `DAT_0082b3ec` and `DAT_0082b3e8`.
- Active-list append/unlink helpers maintain manager-local node head/tail/current state around offsets `+0x50`, `+0x54`, and `+0x58`, and use the global nonempty-manager chain when the first node is appended or the last node is removed.
- LOD allocation gates are behavior-backed only: observed skip thresholds include `700`, `900`, and `800`, with probabilistic ranges below those hard skips.
- Terrain projection uses static-shadow terrain height sampling, not proof of runtime particle collision behavior.

## Layout Notes

These offsets are observed static-binary fields, not complete structure declarations.

### Particle Node

| Offset | Observed role |
| ---: | --- |
| `0x00` | Previous/list pointer area |
| `0x04` | Next/list pointer area |
| `0x38..0x44` | Spawn/current vector fields |
| `0x58` | Attached effect handle/backlink |
| `0x5c` | Type/class field used by update logic |
| `0x60` | Lifetime/position-update field |
| `0x64` | Death flag/state field |
| `0x88` | Resource block pointer |

### Effect Handle

| Offset | Observed role |
| ---: | --- |
| `0x00..0x0f` | Position/vector fields |
| `0x10..0x4f` | Transform/state fields |
| `0x48` | `10000.0` sentinel/default scale in interpolation paths |
| `0xa4` | Activity flag |
| `0xa8` | Particle/backlink pointer |
| `0xac` | Looping/flag field |
| `0xb0` | Next handle pointer |
| `0xb4` | Handle state, observed values `1`, `2`, and `3` |

### Owner/Effect Link Cell

| Offset | Observed role |
| ---: | --- |
| `0x04` | Linked effect handle pointer cleared by `ParticleEffectLink__SetHandleStateAndClear` |

## Boundary

Wave463, Wave468, Wave477, and Wave478 are saved static Ghidra refinements only. Runtime particle/effect/list behavior, exact particle/handle/set/manager/owner-link layouts, exact source identities, BEA launch behavior, game patching, and rebuild parity remain unproven.
