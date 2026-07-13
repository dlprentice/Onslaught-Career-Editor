# CollisionSeekingRound.cpp Functions

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x00425a10` → `CCollisionSeekingInfantryBloke__CheckCollisionFlagsWithDeadSideBranch` (was `CCollisionSeekingInfantryBloke__CheckSideCompatibleOrCollisionFlags`); `0x00437fe0` comment correction; `0x004d8410` comment correction. Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Wave1162 current-risk update: Wave1162 (`wave1162-collision-terrain-detector-current-risk-review`) re-read the adjacent collision/terrain detector handoff context with fresh Ghidra evidence. It includes `0x00425a10 CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags` plus the HLCollisionDetector sweep path reached through `CCollisionSeekingRound__ProcessMapWhoCollisionSweep`. Accounting advances to `547/1179 = 46.40%` with `14 collision/terrain detector current-risk rows`, current focused candidates: 1178, live regenerated current focused candidates: 1178, remaining active focused work: 632, current risk candidates: 6166, fresh Ghidra export, read-only review, no mutation, `0 / 0 / 0`, `6411/6411 = 100.00%`, `41 xref rows`, and `2104 instruction rows`. Anchors include `CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags`, `CMeshCollisionVolume__IsDirectionInsideTrianglePrism`, `CHeightField__GetHeightSamplePacked16`, `CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions`, `CHLCollisionDetector__ProcessMapWhoCollisionSweep`, and `CHLCollisionDetector__HandleScheduledCollisionEvent`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-021413_post_wave1162_collision_terrain_detector_current_risk_review_verified`; tag `wave1162-collision-terrain-detector-current-risk-review`; source denominator `wave1108-current-risk-rank`; current-risk denominator; focused threshold `15`; not Wave911 reconstruction. Runtime collision behavior, runtime projectile behavior, exact layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

Wave1161 current-risk update: Wave1161 (`wave1161-collision-seeking-round-current-risk-review`) accounts for `17 collision-seeking/mesh-collision current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, no runtime-file mutation, and Codex read-only consults used while Codex root made the final judgment. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `533/1179 = 45.21%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 646; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `74 xref rows` and `1567 instruction rows`. Static anchors include `CCollisionSeekingRound__InitCollisionLineAndSound`, `CCollisionSeekingRound__ResolveRoundCollisionResponse`, `CCollisionSeekingRound__ProcessMapWhoCollisionSweep`, `CMeshCollisionVolume__TestSweptSphereAgainstMeshPart`, `CMeshCollisionVolume__ResolveContactNormalAndPlane`, and `CCollisionSeekingRound__ShutdownMonitorAndDestruct`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-014548_post_wave1161_collision_seeking_round_current_risk_review_verified`. Runtime collision behavior, runtime projectile behavior, exact CCollisionSeekingRound/CMeshCollisionVolume/CLine layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1161; wave1161-collision-seeking-round-current-risk-review; 533/1179 = 45.21%; 17 collision-seeking/mesh-collision current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 646; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; 74 xref rows; 1567 instruction rows; CCollisionSeekingRound__InitCollisionLineAndSound; CCollisionSeekingRound__ResolveRoundCollisionResponse; CCollisionSeekingRound__ProcessMapWhoCollisionSweep; CMeshCollisionVolume__TestSweptSphereAgainstMeshPart; CMeshCollisionVolume__ResolveContactNormalAndPlane; CCollisionSeekingRound__ShutdownMonitorAndDestruct; [maintainer-local-ghidra-backup-root]\BEA_20260606-014548_post_wave1161_collision_seeking_round_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

> Source File: CollisionSeekingRound.cpp | Binary: BEA.exe
> Debug Paths:
> - 0x00624630: `[maintainer-local-source-export-root]\CollisionSeekingRound.cpp`
> - 0x006246d8: `[maintainer-local-source-export-root]\collisionseekingthing.cpp`

## Current Status

Wave 322 (2026-05-11) recovered the missing `CCollisionSeekingRound` vtable target boundaries and saved conservative names, signatures, and proof-boundary comments in the live Ghidra project. The earlier note that the main vtable targets were still `UNDEFINED` is superseded.

Wave398 (2026-05-14) corrected two older adjacent owner labels out of this file: `0x00480a30` is now `CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions`, and `0x00480e10` is now `CHLCollisionDetector__TraverseQuadNodeAndDispatchCollisions`. `CCollisionSeekingRound__ProcessMapWhoCollisionSweep` remains documented here because its vtable slot forwards map/who sweep context to the detector object rooted at the round's `+0x24` field.

Wave919 re-reviewed six collision-seeking round / infantry-bloke helpers (`0x00425a10`, `0x00425c60`, `0x00426900`, `0x00426920`, `0x00426a00`, and `0x00426a20`) with fresh metadata, tag, instruction, and decompile exports. The saved names/signatures/comments remain appropriate for the current evidence; no Ghidra mutation was performed.

Wave991 (`round-config-bridge-review-wave991`, `wave991-readback-verified`) normalized `0x00426150 CCollisionSeekingRound__Init` after fresh round/projectile config bridge read-back. The pass replaced the older "tags unproven" caveat with current caller and DATA-ref evidence, added static read-back tags, and made no rename, no signature change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation. Context rows included `0x00437fe0 CPhysicsRoundValue__SetOwnedAuxStringAt0C`, `0x00438050 CPhysicsRoundValue__SetOwnedValueStringAt08`, `0x00438b40 CRoundGridOfFear__ApplyToRoundByName`, `0x00430210 CRoundStatement__LoadFromMemBuffer`, `0x00437490 CPhysicsScriptStatements__CreateStatementType5`, and `0x004d8410 CRound__Init`. Queue closure remains `6222/6222 = 100.00%`; Wave911 focused re-audit progress is `445/1408 = 31.61%`; expanded static surface progress is `525/1478 = 35.52%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-045300_post_wave991_round_config_bridge_review_verified`. Runtime projectile behavior, runtime physics-script behavior, exact layouts, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

Wave1059 (`collision-seeking-round-tail-review-wave1059`, `wave1059-readback-verified`) re-read the collision-seeking round tail and adjacent context rows, then saved function-tag normalization for fourteen already named/commented rows. Primary anchors include `0x00425b50 CCollisionSeekingRound__InitCollisionLineAndSound`, `0x00425e30 CCollisionSeekingRound__UpdatePrimarySeekerLeadVector`, `0x00426300 CMeshCollisionVolume__ScalarDeletingDestructor_00426300`, `0x00426370 CCollisionSeekingRound__ReplacePrimarySeekerAndRefreshOffset`, `0x004263f0 CCollisionSeekingRound__Destructor`, `0x00426480 CCollisionSeekingRound__SetCollisionMask`, and `0x004264a0 CCollisionSeekingRound__ResolveRoundCollisionResponse`; context anchors include `0x00425a10 CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags`, `0x00425c60 CCollisionSeekingRound__FilterCollisionCandidateByTrajectory`, `0x00426900 CCollisionSeekingRound__CheckCollisionFlags`, `0x00426920 CCollisionSeekingRound__ComputeScaledMapCellChebyshevDistance`, `0x00426a00 CCollisionSeekingRound__ProcessMapWhoCollisionSweep`, and `0x00426a20 CCollisionSeekingRound__MarkDelayedCollisionReady`. Fresh primary pre/post exports verified `8` metadata rows, `8` tag rows, `26` xref rows, `665` function-body instruction rows, and `8` decompile rows; context pre/post exports verified `6` metadata rows, `6` tag rows, `18` xref rows, `257` instruction rows, and `6` decompile rows. Dry/apply/final-dry reported `updated=0 skipped=0 tags_added=131 missing=0 bad=0`, then `updated=14 skipped=0 tags_added=131 missing=0 bad=0`, then `updated=0 skipped=14 tags_added=0 missing=0 bad=0`. Queue closure remains `6246/6246 = 100.00%`; Wave911 focused progress advances to `812/1408 = 57.67%`; expanded static surface progress advances to `1140/1509 = 75.55%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-195206_post_wave1059_collision_seeking_round_tail_review_verified`, `19` files, `174689159` bytes, `DiffCount=0`, `HashDiffCount=0`. Runtime projectile/collision/event/response behavior, exact helper layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1059; collision-seeking-round-tail-review-wave1059; 0x00425b50 CCollisionSeekingRound__InitCollisionLineAndSound; 0x00425e30 CCollisionSeekingRound__UpdatePrimarySeekerLeadVector; 0x00426300 CMeshCollisionVolume__ScalarDeletingDestructor_00426300; 0x00426370 CCollisionSeekingRound__ReplacePrimarySeekerAndRefreshOffset; 0x004263f0 CCollisionSeekingRound__Destructor; 0x00426480 CCollisionSeekingRound__SetCollisionMask; 0x004264a0 CCollisionSeekingRound__ResolveRoundCollisionResponse; 0x00426a20 CCollisionSeekingRound__MarkDelayedCollisionReady; 812/1408 = 57.67%; 1140/1509 = 75.55%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-195206_post_wave1059_collision_seeking_round_tail_review_verified; tag normalization.

Wave1126 (`wave1126-projectile-collision-targeting-current-risk-review`, `wave1126-readback-verified`) re-read the current-risk projectile/collision targeting cluster and normalized the saved comments/tags for `0x00425c60 CCollisionSeekingRound__FilterCollisionCandidateByTrajectory` and `0x00426920 CCollisionSeekingRound__ComputeScaledMapCellChebyshevDistance`. `0x00425c60` is bounded as the candidate filter that calls `CCollisionSeekingRound__CheckCollisionFlags`, rejects same-owner/context target candidates, checks target state flags, samples the candidate center, and applies movement/trajectory range evidence. `0x00426920` is bounded as the packed map-cell distance helper that scales cell depths and returns a Chebyshev-style max absolute delta. Wave1126 also re-read `0x004daba0 CRound__FindNearbyHostileWithinProjectileRadius` in the adjacent CRound targeting context. Fresh pre/post exports verified `3` metadata rows, `3` tag rows, `7` xref rows, `291` instruction rows, and `3` decompile rows. Dry/apply/final-dry reported `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=2 tags_added=19 missing=0 bad=0`, then `updated=3 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=2 tags_added=19 missing=0 bad=0`, then `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`. Current focused accounting is `138/1179 = 11.70%` of current focused candidates: 1179; live regenerated focused candidates: 1178; remaining active focused work: 1041; static closure remains `6410/6410 = 100.00%` with `0 / 0 / 0` debt. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-061135_post_wave1126_projectile_collision_targeting_current_risk_review_verified`; previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-053504_post_wave1125_carver_targeting_current_risk_review_verified`. Probe anchor: `3 rows`; score-23 projectile collision targeting current-risk cluster; fresh Ghidra export; comment/tag normalization; `19 tags`; Wave919; Wave920; Wave1059; Wave495. Runtime collision behavior, runtime targeting behavior, runtime projectile behavior, concrete layouts, exact source-body identity, BEA patching, visual QA, and rebuild parity remain separate proof.

Wave494 (2026-05-17) hardened the collision-seeking / CCSRay destructor-tail entries at `0x004d8a50`, `0x004d8a70`, `0x004d9da0`, and `0x004d9dc0`. It also recorded that `0x004d8dc0`, `0x004d9d60`, and `0x004d9ef0` are adjacent CRound/engine launch-tail evidence rather than proof of full CollisionSeekingRound source-body recovery.

Wave1011 (`round-vtable-boundary-wave1011`) clarified the next adjacent post-`CCollisionSeekingRound__ShutdownMonitorAndDestruct` region as shared CRound / CMissile-style vtable evidence rather than CollisionSeekingRound-specific source proof. It recovered `0x004d8ac0 VFuncSlot_16_004d8ac0` and `0x004d8ae0 VFuncSlot_39_004d8ae0`, followed the raw caller from `0x004d8d07` into `0x0040ac50 CBattleEngine__Rearm`, preserved the already-saved `0x004d8dc0 VFuncSlot_02_004d8dc0` context, and deferred the larger separate `0x004d8e40` DATA-backed vtable target. Queue closure is `6236/6236 = 100.00%`; Wave911 focused progress remains `505/1408 = 35.87%`; expanded static surface progress is `705/1491 = 47.28%`; top-500 coverage remains `409/500 = 81.80%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-172337_post_wave1011_round_vtable_boundary_verified`. Runtime projectile/hit/collision/rearm/impact-sound/event behavior, exact source virtual names, concrete layouts, BEA patching, and rebuild parity remain separate proof.

Wave742 unwind continuation (2026-05-22) does not add new CollisionSeekingRound source-body identity, but it records five compiler unwind callbacks that call the shared `CLine__SetBaseVtable_00426360` helper documented below. `0x005d1220 Unwind@005d1220`, `0x005d1240`, `0x005d1260`, `0x005d1280`, and `0x005d128b` reset stack-local CLine helpers at `EBP-0x180`, `EBP-0xb0`, `EBP-0x70`, `EBP-0x134`, and `EBP-0x40`; the tranche uses `unwind-continuation-wave742` and `wave742-readback-verified`, spans `0x005d1170 Unwind@005d1170` through `0x005d13b3 Unwind@005d13b3`, leaves next high-signal queue head `0x005d13d0 Unwind@005d13d0`, and verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260522-153147_post_wave742_unwind_continuation_verified`. Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.

This is static saved-Ghidra refinement only. Wave1059 proves tag normalization for the reviewed rows, but it does not prove concrete layouts, source virtual method names, local variable names, runtime collision behavior, BEA launch behavior, game patching, or rebuild parity.

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

`CCollisionSeekingRound` is the retail collision-seeking projectile/effect family around seeker lines, mesh collision-volume helpers, collision masks, delayed collision readiness, and map/who collision sweeps. The current source snapshot does not provide exact method bodies for every recovered retail slot, so names are behavior-bounded rather than source-final.

## Vtable

Behavioral slots are located at **0x005de95c**. Wave494 also read back the adjacent lifecycle vtable evidence: `0x005de950` slot 1 points to `CCollisionSeekingRound__ScalarDeletingDestructor_004d8a50`, and `0x005de980` slot 1 points to `CCSRay__ScalarDeletingDestructor_004d9da0`.

| Offset | Address | Saved Ghidra function | Current status |
|--------|---------|-----------------------|----------------|
| +0x00 | 0x00425b50 | `CCollisionSeekingRound__InitCollisionLineAndSound` | Recovered boundary; initializes/replaces a CLine-style helper and wraps `InitWithSound`. |
| +0x04 | 0x00402d20 | inherited/base slot | Outside this wave. |
| +0x08 | 0x00426a00 | `CCollisionSeekingRound__ProcessMapWhoCollisionSweep` | Recovered boundary; forwards to `CHLCollisionDetector__ProcessMapWhoCollisionSweep`. |
| +0x0C | 0x004264a0 | `CCollisionSeekingRound__ResolveRoundCollisionResponse` | Recovered boundary; peer collision-response helper. |
| +0x10 | 0x00425e30 | `CCollisionSeekingRound__UpdatePrimarySeekerLeadVector` | Recovered boundary; updates primary seeker lead vector. |
| +0x14 | 0x00425c60 | `CCollisionSeekingRound__FilterCollisionCandidateByTrajectory` | Recovered boundary; filters collision candidates by flags, owner context, and trajectory. |
| +0x18 | 0x00426370 | `CCollisionSeekingRound__ReplacePrimarySeekerAndRefreshOffset` | Recovered boundary; replaces primary seeker and refreshes owner-relative offset. |
| +0x1C | 0x00426920 | `CCollisionSeekingRound__ComputeScaledMapCellChebyshevDistance` | Recovered boundary; computes scaled map/who cell distance. |

## Saved Functions

| Address | Saved Ghidra name | Signature / purpose |
|---------|-------------------|---------------------|
| 0x00425a10 | `CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags` | `bool __thiscall ... (void * this, void * candidateRound)`; infantry-bloke filter helper with mount-state compatibility fallback. |
| 0x00425b50 | `CCollisionSeekingRound__InitCollisionLineAndSound` | `void __thiscall ... (void * this, void * roundConfig)`; recovered boundary for line-helper setup plus sound-aware init. |
| 0x00425c60 | `CCollisionSeekingRound__FilterCollisionCandidateByTrajectory` | `bool __thiscall ... (void * this, void * candidateRound)`; applies collision flags, owner rejection, target/weapon flags, and trajectory range test. |
| 0x00425e30 | `CCollisionSeekingRound__UpdatePrimarySeekerLeadVector` | `void * __fastcall ... (void * this)`; updates primary seeker target delta or lead-vector fields. |
| 0x00426150 | `CCollisionSeekingRound__Init` | `void __thiscall ... (void * this, void * roundConfig)`; Wave991-normalized bridge row that initializes owner/config flags and primary/secondary seeker helpers; callers include `0x004269b0 CCollisionSeekingRound__InitWithSound` and `0x00426a40 CCollisionSeekingRound__CreateEffect`, with DATA/vtable ref `0x005d9614`. |
| 0x00426300 | `CMeshCollisionVolume__ScalarDeletingDestructor_00426300` | `void * __thiscall ... (void * this, int deleteFlags)`; scalar-deleting wrapper for a mesh collision-volume helper. |
| 0x00426340 | `CLine__ScalarDeletingDestructor_00426340` | `void * __thiscall ... (void * this, int deleteFlags)`; scalar-deleting wrapper for the shared CLine-style helper. |
| 0x00426360 | `CLine__SetBaseVtable_00426360` | `void __fastcall ... (void * this)`; owner-neutral CLine vtable reset, broader than CollisionSeekingRound. |
| 0x00426370 | `CCollisionSeekingRound__ReplacePrimarySeekerAndRefreshOffset` | `void __thiscall ... (void * this, void * newSeeker)`; deletes/replaces the primary seeker and samples owner target position. |
| 0x004263f0 | `CCollisionSeekingRound__Destructor` | `void __fastcall ... (void * this)`; resets vtable, deletes helper pointers, then shuts down monitor state. |
| 0x00426460 | `CCollisionSeekingRound__ScalarDeletingDestructor` | `void * __thiscall ... (void * this, int deleteFlags)`; scalar-deleting destructor wrapper. |
| 0x00426480 | `CCollisionSeekingRound__SetCollisionMask` | `void __thiscall ... (void * this, int collisionMask)`; writes `+0x10` and marks `+0x0c` bit `0x100`. |
| 0x004264a0 | `CCollisionSeekingRound__ResolveRoundCollisionResponse` | `void __thiscall ... (void * this, void * otherRound)`; gates on delayed-ready flag `0x400`, owner/self filters, helper selection, and response callbacks. |
| 0x00426900 | `CCollisionSeekingRound__CheckCollisionFlags` | `bool __thiscall ... (void * this, void * candidateRound)`; compares candidate owner flags against this round collision mask. |
| 0x00426920 | `CCollisionSeekingRound__ComputeScaledMapCellChebyshevDistance` | `int __thiscall ... (void * this, void * packedCell)`; scaled Chebyshev-style map/who cell distance. |
| 0x004269b0 | `CCollisionSeekingRound__InitWithSound` | `void __thiscall ... (void * this, void * roundConfig)`; wraps init, schedules a 3000ms event, and scans neighboring sectors. |
| 0x00426a00 | `CCollisionSeekingRound__ProcessMapWhoCollisionSweep` | `void __thiscall ... (void * this, void * startOrContext, void * endOrContext)`; forwards sweep context to `CHLCollisionDetector`. |
| 0x00426a20 | `CCollisionSeekingRound__MarkDelayedCollisionReady` | `void __thiscall ... (void * this, void * event)`; sets flag `0x400` when the event code/timestamp equals 3000ms. |
| 0x00426a40 | `CCollisionSeekingRound__CreateEffect` | `void __thiscall ... (void * this, void * roundConfig)`; builds a trace helper from secondary seeker state and dispatches impact effect context. |
| 0x004d8a50 | `CCollisionSeekingRound__ScalarDeletingDestructor_004d8a50` | `void * __thiscall ... (void * this, int flags)`; Wave494 scalar-deleting wrapper from vtable `0x005de950` slot 1. |
| 0x004d8a70 | `CCollisionSeekingRound__ShutdownMonitorAndDestruct` | `void __fastcall ... (void * this)`; Wave494 destructor body / monitor shutdown helper. |
| 0x004d9da0 | `CCSRay__ScalarDeletingDestructor_004d9da0` | `void * __thiscall ... (void * this, int flags)`; Wave494 scalar-deleting wrapper from adjacent vtable `0x005de980` slot 1. |
| 0x004d9dc0 | `CCSRay__DestructorBody_004d9dc0` | `void __fastcall ... (void * this)`; Wave494 CCSRay-style destructor body with exact source identity still open. |

## Partial Layout Signals

Observed fields are still layout clues, not a final structure:

| Offset | Observed role |
|--------|---------------|
| `+0x0c` | state/collision flags, including `0x100` explicit-mask and `0x400` delayed-ready context |
| `+0x10` | collision mask |
| `+0x14` | primary CLine-style seeker/helper pointer |
| `+0x18` | secondary CMeshCollisionVolume-style helper pointer |
| `+0x24` | collision detector sweep context used by the map/who sweep slot |
| `+0x38` | positive distance/radius context used by the primary seeker update |

## collisionseekingthing.cpp References

`collisionseekingthing.cpp` remains most clearly observed as debug-path allocation/provenance context used by CollisionSeekingRound helper allocation sites:

| From address | Current owner | Alloc size / line | Observed role |
|--------------|---------------|-------------------|---------------|
| 0x004261be | `CCollisionSeekingRound__Init` | `0x1c`, line `0x28` | Primary seeker/helper allocation context. |
| 0x0042627a | `CCollisionSeekingRound__Init` | `0x28`, line `0x39` | Secondary mesh collision-volume helper allocation context. |
| 0x00426ad3 | `CCollisionSeekingRound__CreateEffect` | `0x34`, line `0x13a` | Effect/trace helper allocation context. |

## Wave 322 Evidence

Fresh headless read-back after mutation verified:

- `19/19` final metadata rows.
- `19/19` final decompile exports.
- `94` xref rows.
- `1691` instruction rows.
- `8/8` newly created boundary targets read back.
- Refreshed static queue: `5884` total functions, `743` commented functions, `5141` commentless functions, `2004` undefined signatures, and `2307` `param_N` signatures.

Public-safe evidence lives in `release/readiness/ghidra_collision_seeking_round_boundary_signature_correction_2026-05-11.md`. Raw decompile, instruction, xref, and probe JSON outputs remain ignored under `subagents/`.

## Wave 494 Evidence

- Apply script: `tools/ApplyCollisionRoundTailWave494.java`
- Probe: `tools/ghidra_collision_round_tail_wave494_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave494-collision-round-tail-004d8a50/`
- Dry/apply/verify summaries:
  - Dry: `updated=0 skipped=7 created=0 would_create=0 renamed=0 would_rename=3 missing=0 bad=0`
  - Apply: `updated=7 skipped=0 created=0 would_create=0 renamed=3 would_rename=0 missing=0 bad=0`
  - Verify dry: `updated=0 skipped=7 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post-readback verified vtable `0x005de950` slot 1 -> `0x004d8a50`, adjacent vtable `0x005de980` slot 1 -> `0x004d9da0`, focused probe PASS, npm probe PASS, queue refresh PASS, and Ghidra backup `[maintainer-local-ghidra-backup-root]\BEA_20260517-093427_post_wave494_collision_round_tail_verified`.
