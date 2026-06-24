# SquadNormal.cpp Functions

> Source File: SquadNormal.cpp | Binary: BEA.exe
> Debug Path: 0x0063283c ("C:\dev\ONSLAUGHT2\SquadNormal.cpp")

## Overview
> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

Wave1218 (wave1218-generic-shared-vfunc-thunk-tail-current-risk-review) re-read 0x004e66d0 SharedVFunc__ForwardProcessNoOp as part of the generic/shared vfunc-thunk tail current-risk review. The row remains an owner-neutral process/no-op forwarder and preserves the stale-owner correction away from CWaypoint, with no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change. Verified backup: G:\GhidraBackups\BEA_20260607-222830_post_wave1218_generic_shared_vfunc_thunk_tail_current_risk_review_verified. Runtime squad/frontend process behavior, exact owner coverage, exact layouts, and rebuild parity remain separate proof.

Wave1215 (`wave1215-unit-targeting-combat-residual-current-risk-review`) re-read `CSquadNormal__SelectBestEngagementTarget` in the unit-targeting combat residual cluster. CALL xref `0x004e815a` from `CSquadNormal__ScheduleTargetReaderRefresh` and no-function callsite `0x004ea584` preserve the one-stack-argument scoring helper shape; state `+0x7c` selects `DAT_00855090`, `DAT_008550b0`, or `DAT_008550c0`, and candidate scoring uses config weights at `squad+0xa0`. Verified backup: `G:\GhidraBackups\BEA_20260607-090802_post_wave1215_unit_targeting_combat_residual_current_risk_review_verified`. Runtime squad AI behavior, concrete candidate/global-list layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Wave1211 (`wave1211-score17-residual-current-risk-review`) re-read and tag-normalized `0x004e97e0 CGenericActiveReader__SwapWithCandidateIfFormationCloser` and `0x004e9f00 CSquadNormal__VFunc_52_004e9f00` as part of `8 score-17 residual current-risk rows` in the current-risk denominator. Fresh evidence keeps `CGenericActiveReader__SwapWithCandidateIfFormationCloser` tied to `CSquadNormal__ResolveFormationSlotConflicts` and `CGenericActiveReader__SetReader`, while `CSquadNormal__VFunc_52_004e9f00` remains a static-shadow/debug-render-style virtual with static shadow anchor `0x006fadc8`. No rename, signature, comment, function-boundary, or executable-byte change was made. Active current-risk accounting after the wave is `1110/1179 = 94.15%`; verified backup: `G:\GhidraBackups\BEA_20260607-061324_post_wave1211_score17_residual_current_risk_review_verified`. Runtime squad/formation behavior, exact active-reader/squad layouts, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Wave1168 current-risk update: Wave1168 (`wave1168-unit-target-reader-tail-current-risk-review`) accounts for `12 CUnit / CSquadNormal / SharedUnitAI target-reader tail current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, no runtime-file mutation, and Codex read-only consult used. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `648/1179 = 54.96%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 531; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `191 xref rows` and `618 instruction rows`. Static anchors include `CSquadNormal__IsValidLinkedSupportForTarget`, `CUnit__ForwardAimTransformAndAttachTargetReader`, `CUnit__SetSpawnCooldownState3`, `CUnit__ForwardAttachedNodeVFunc14IfPresent`, `CUnit__VFunc22_ActivateLinkedTargetsAndChildren`, and `SharedUnitAI__UpdateField28TargetReaderGate_004ffbb0`; xref/callee context includes `CSpawnerThng__ProcessSpawnWave` and `OID__UpdateAimTransformAndAttachTargetReader`. Boundary: `CUnit__SetSpawnCooldownState3` is adjacent CUnit tail/spawn-cooldown accounting, not target-reader behavior. Verified backup: `G:\GhidraBackups\BEA_20260606-052300_post_wave1168_unit_target_reader_tail_current_risk_review_verified`. Runtime targeting behavior, runtime squad AI behavior, runtime attached-node behavior, exact CUnit/CSquadNormal/CUnitAI/SharedUnitAI concrete layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1168; wave1168-unit-target-reader-tail-current-risk-review; 648/1179 = 54.96%; 12 CUnit / CSquadNormal / SharedUnitAI target-reader tail current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 531; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult used; 0 / 0 / 0; 6411/6411 = 100.00%; 191 xref rows; 618 instruction rows; CSquadNormal__IsValidLinkedSupportForTarget; CUnit__ForwardAimTransformAndAttachTargetReader; CUnit__SetSpawnCooldownState3; CUnit__ForwardAttachedNodeVFunc14IfPresent; CUnit__VFunc22_ActivateLinkedTargetsAndChildren; SharedUnitAI__UpdateField28TargetReaderGate_004ffbb0; CSpawnerThng__ProcessSpawnWave; OID__UpdateAimTransformAndAttachTargetReader; G:\GhidraBackups\BEA_20260606-052300_post_wave1168_unit_target_reader_tail_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

CSquadNormal class implementation - handles normal squad behavior for groups of AI units. This class manages squad member spawning, iteration, positioning, and lifetime. The class uses a linked list to track squad members.

Wave1072 (`oid-target-profile-ballistic-review-wave1072`) re-read the support-mask bridge with no mutation. `0x0050a0b0 CSquadNormal__HasActiveMaskMatchWithTarget` and adjacent `0x0050a0d0 CUnit__HasMaskBitsA8` remain coherent with the target-profile gate cluster, while runtime squad support/escort selection behavior, exact mask layout, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof. Queue closure remains `6246/6246 = 100.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface progress advances to `1334/1560 = 85.51%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260602-035902_post_wave1072_oid_target_profile_ballistic_review_verified`.

Wave766 static read-back (`unwind-continuation-wave766`, `wave766-readback-verified`) saved comments/tags/signatures for SquadNormal.cpp-adjacent compiler-generated unwind cleanup callbacks from `0x005d4d30 Unwind@005d4d30` through `0x005d4de9 Unwind@005d4de9`. Evidence includes SquadNormal.cpp debug path `0x0063283c`, DATA scope-table xrefs `0x0061d5e4` through `0x0061d67c`, complex-thing destructor-base thunks, member `CSPtrSet__Clear` callbacks, active-reader destructor callbacks, `CDXLandscape__FreeObjectCallback` rows, and the `0x005d4dd0 Unwind@005d4dd0` allocation-free row. Verified backup: `G:\GhidraBackups\BEA_20260523-161835_post_wave766_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

Wave767 static read-back (`unwind-continuation-wave767`, `wave767-readback-verified`) continued the SquadNormal.cpp unwind coverage for exact anchors `0x005d4e00 Unwind@005d4e00` and `0x005d4e30 Unwind@005d4e30`. Both rows are saved as `void __cdecl Unwind@...(void)` and tie to SquadNormal.cpp debug path `0x0063283c`, DATA scope-table xrefs `0x0061d6a4` and `0x0061d6cc`, and `OID__FreeObject_Callback` allocation-cleanup evidence. Verified backup: `G:\GhidraBackups\BEA_20260523-164622_post_wave767_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

Wave927 (`cunit-active-reader-targeting-review-wave927`) re-reviewed `0x004e97e0 CGenericActiveReader__SwapWithCandidateIfFormationCloser` as the SquadNormal-side formation conflict context for the CUnit/CUnitAI active-reader targeting lane. Fresh xrefs tie it to `0x004e8640 CSquadNormal__ResolveFormationSlotConflicts`; the decompile compares current and cross-assigned formation offsets, then swaps reader cells through `CGenericActiveReader__SetReader` only when the candidate pairing is closer. The same Wave927 note also anchors `0x00428b50 CUnit__SetReaderAndComputeRelativeYaw`, `0x00428bc0 CUnitAI__GetTargetHeadingWithOffset`, `0x00429270 CUnitAI__UpdateHeadingTowardTargetClamped`, `0x004fd3d0 CUnit__IsCandidateSideCompatibleForTargeting`, and context helper `0x004fb650 CUnit__ForwardAimTransformAndAttachTargetReader`. Wave911 focused re-audit progress after Wave927 is `103/1408 = 7.32%`; export-contract closure remains `6113/6113 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260527-223748_post_wave927_cunit_active_reader_targeting_review_verified`. Runtime formation/targeting behavior, exact active-reader layout, exact source-body identity, and rebuild parity remain separate proof.

Wave1009 (`geometry-guide-heightfield-spine-review-wave1009`) recovered three DATA-backed CSquadNormal static-shadow caller boundaries: `0x004e9600 CSquadNormal__VFunc_20_004e9600`, `0x004e96f0 CSquadNormal__VFunc_21_004e96f0`, and `0x004e9f00 CSquadNormal__VFunc_52_004e9f00`. Queue closure is `6233/6233 = 100.00%`; verified backup: `G:\GhidraBackups\BEA_20260531-155648_post_wave1009_geometry_guide_heightfield_spine_review_verified`. Runtime squad formation/debug/render behavior, exact source virtual names, concrete layouts, BEA patching, and rebuild parity remain separate proof.

## Functions

| Address | Name | Purpose | Status |
|---------|------|---------|--------|
| 0x004e5da0 | CSquad__Constructor | Initialize CSquad base object and install CSquad vtables | Wave508 read-back |
| 0x004e5e70 | CSquad__Init | CSquad base init vfunc that copies init fields and spawns initial members | Wave509 read-back |
| 0x004e65b0 | CSquad__VFunc02_RemoveFromGlobalLists | Remove CSquad from observed global squad lists, then chain to base slot-2 cleanup | Wave508 read-back |
| 0x004e65e0 | CSquad__HandleEvent | CSquad event handler with special `0xfa2` dispatch and ComplexThing fallback | Wave508 read-back |
| 0x004e6680 | CSquadNormal__IsFactionCompatible | Candidate faction/state compatibility predicate used by target selection | Wave508 read-back |
| 0x004e6870 | CSquadNormal__Constructor | Initialize CSquadNormal instance, sets vtables and member arrays | Renamed |
| 0x004e6ac0 | CSquadNormal__ScalarDeletingDestructor | Scalar deleting destructor wrapper | Wave508 read-back |
| 0x004e6ae0 | CSquadNormal__Destructor | Clean up squad resources, destroy member lists | Renamed |
| 0x004e6bb0 | CSquadNormal__Init | Initialize squad with spawn point position and state | Renamed |
| 0x004e6ce0 | (Orphan code) | Virtual method, references line 129 (0x81) | NOT A FUNCTION |
| 0x004e6f70 | CSquadNormal__RemoveMember | Remove a unit from the squad member list | Renamed |
| 0x004e6ff0 | CSquadNormal__SyncFromLeaderUnit | Sync formation/grid/flag context from leader unit | Wave508 read-back |
| 0x004e7cf0 | CSquadNormal__UpdateFormationAdvanceScale | Formation/member-set advance-scale predicate/update helper | Wave508 read-back |
| 0x004e7f40 | CSquadNormal__IsLeaderNearFormationCentroid | Leader-vs-centroid proximity predicate | Wave508 read-back |
| 0x004e8100 | CSquadNormal__ScheduleTargetReaderRefresh | Select target, set active reader, and schedule event `4000` refresh | Wave508 read-back |
| 0x004e7110 | CSquadNormal__Process | Main squad update/process path over leader sync, formation, spawn/split, merge, and member-centroid refresh | Wave509 read-back |
| 0x004e81d0 | CSquadNormal__EvaluateLeaderTargetPursuitMode | Leader-target pursuit/support mode evaluator | Wave509 read-back |
| 0x004e83b0 | CSquadNormal__PruneDeadMembersAndReschedule | Remove null/dead member-reader nodes and optionally schedule event `0xfa1` | Wave509 read-back |
| 0x004e84e0 | CSquadNormal__ResolveFormationSlotConflicts | Formation-slot conflict resolver over member reader nodes | Wave509 read-back |
| 0x004e8730 | CSquadNormal__BuildColumnFormation | Column-formation builder and member command dispatcher | Wave509 read-back |
| 0x004e8930 | CSquadNormal__BuildAttackFormation | Attack-formation builder and target/support reader refresher | Wave509 read-back |
| 0x004e8dd0 | CSquadNormal__ShouldSwitchToAttackFormation | Attack-formation predicate based on leader/target distance and state | Wave509 read-back |
| 0x004e8ed0 | CSquadNormal__CreateIterator | Allocate a 0x10-byte CSPtrSet snapshot over current squad members | Wave509 read-back |
| 0x004e8f80 | CSquadNormal__TryMergeWithNearbySquad | Try to merge members into a nearby compatible squad | Wave509 read-back |
| 0x004e91f0 | CSquadNormal__SpawnMembers | Split grounded members into new squads or realign singleton squad position | Wave509 read-back |
| 0x004e9570 | CSquadNormal__SetFactionAndRefreshGlobalLists | Set squad/member faction state and refresh observed global faction lists | Wave509 read-back |
| 0x004e97e0 | CGenericActiveReader__SwapWithCandidateIfFormationCloser | Active-reader helper used by formation conflict resolution | Wave509 read-back |
| 0x0050a0b0 | CSquadNormal__HasActiveMaskMatchWithTarget | Wave554 support-mask helper; `RET 0x4` proves one `target_unit` argument | Wave554 read-back |
| 0x0050a0d0 | CUnit__HasMaskBitsA8 | Wave554 adjacent Unit mask helper used by `CSquadNormal__SelectBestSupportOrEscort` | Wave554 read-back |

## Wave408 Select-Target Hardening

Wave408 preserved the saved `CSquadNormal__SelectBestEngagementTarget` name at `0x00477cb0` and hardened its saved Ghidra signature/comment/tags to:

```cpp
void * __stdcall CSquadNormal__SelectBestEngagementTarget(void * squad);
```

Fresh retail read-back supports the body as a squad target-selection/scoring helper: one stack argument with `RET 0x4`, no ECX-thiscall setup, squad state at `+0x7c` selecting `DAT_00855090`, `DAT_008550b0`, or `DAT_008550c0`, virtual context reads at vtable `+0x120/+0x124`, flag/range/faction/support filtering, config scoring offsets under `squad+0xa0`, and fallback through `candidate+0x148`. Direct xrefs are `CSquadNormal__ScheduleTargetReaderRefresh` at `0x004e815a` and a no-function callsite at `0x004ea584`.

This is saved static Ghidra metadata and instruction/decompile/xref evidence only. Exact source identity, candidate struct layout, global list semantics, runtime AI behavior, BEA launch behavior, game patching, and rebuild parity remain open.

## Wave508 Unit / Squad Support Cleanup

Wave508 saved static names, signatures, comments, and tags for 20 adjacent unit/squad support helpers, including CSquad base helpers, CSquadNormal constructor/destructor/init/member/formation/target-refresh helpers, and CUnit support predicates consumed by squad code.

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x004e5da0 | CSquad__Constructor | Calls `CThing__ctor_like_004f3e10`, installs CSquad vtables `0x005def1c` and `0x005deea4`, and is reached by `CSquadNormal__Constructor`. |
| 0x004e65b0 | CSquad__VFunc02_RemoveFromGlobalLists | CSquad vtable `0x005def1c` slot 2; removes the squad from observed global list/set heads before chaining to the base slot-2 cleanup path. |
| 0x004e65e0 | CSquad__HandleEvent | CSquad vtable `0x005def1c` slot 0; delegates non-`0xfa2` events to `CComplexThing__HandleEvent` and dispatches a special vtable path for the observed event. |
| 0x004e6680 | CSquadNormal__IsFactionCompatible | One explicit stack argument after `ECX`; compares candidate faction/state against the squad state at `this+0x7c`. |
| 0x004e6870 | CSquadNormal__Constructor | Calls `CSquad__Constructor`, initializes pointer-set fields, allocates local state, and installs vtables `0x005df0f4` and `0x005df07c`. |
| 0x004e6ac0 | CSquadNormal__ScalarDeletingDestructor | CSquadNormal vtable `0x005df0f4` slot 1; wrapper calls `CSquadNormal__Destructor` and conditionally frees on delete flags. |
| 0x004e6ae0 | CSquadNormal__Destructor | Frees observed resource/list fields, clears pointer-set style lists, and chains to `CComplexThing__dtor_base`. |
| 0x004e6bb0 | CSquadNormal__Init | CSquadNormal vtable `0x005df0f4` slot 9; samples shadow/height, calls the CSquad slot-9 helper, registers global sets, dispatches a vtable slot, and schedules target refresh. |
| 0x004e6f70 | CSquadNormal__RemoveMember | Removes a member from `this+0xa4`, clears reader/unregister state, updates `member+0x148`, and decrements observed member count `this+0xb4`. |
| 0x004e6ff0 | CSquadNormal__SyncFromLeaderUnit | CSquadNormal vtable `0x005df0f4` slot 68; reads leader vtable slots `+0x44` and `+0x1bc`, calls `CUnit__GetGridMapByType`, and refreshes formation fields. |
| 0x004e7cf0 | CSquadNormal__UpdateFormationAdvanceScale | ECX-only formation helper over member-set and occupancy context; xref from `CSquadNormal__Process`. |
| 0x004e7f40 | CSquadNormal__IsLeaderNearFormationCentroid | ECX-only predicate comparing leader/squad centroid distance against the observed static threshold. |
| 0x004e8100 | CSquadNormal__ScheduleTargetReaderRefresh | Calls `CSquadNormal__SelectBestEngagementTarget`, sets the active reader, and schedules event `4000`; xref from `CSquadNormal__Init`. |

This pass also corrected `0x004e5e50` to owner-neutral `SharedComplexThing__ScalarDeletingDestructor` and corrected `0x004e4d70` to `CSphere__VFunc02_ResolveCollisionAsCylinder`; those are shared/static collision context, not CSquadNormal methods. Larger adjacent bodies `0x004e5e70`, `0x004e6610`, `0x004e66d0`, and `0x004e7110` were intentionally deferred for focused review.

This is static saved-Ghidra evidence only. Runtime squad AI, faction/formation behavior, target refresh scheduling, concrete member-list/global-list layouts, exact source virtual names, and rebuild parity remain unproven.

## Wave509 CSquadNormal Tail Cleanup

Wave509 saved static names, signatures, comments, and tags for 15 adjacent CSquad/CSquadNormal tail helpers. It promoted the CSquad slot-9 helper to `CSquad__Init`, corrected two stale owner labels to owner-neutral shared helpers, fixed two undefined signatures, and corrected the slot-swap helper to active-reader ownership.

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x004e5e70 | CSquad__Init | CSquad vtable `0x005def1c` slot 9; copies init fields, resolves a type/name through `DAT_008553fc`, spawns initial members, calls `CComplexThing__Init`, and adds the squad to `DAT_008550a0`. |
| 0x004e6610 | SharedState__IsTimer88PendingAndState7CZero | Corrects stale `CExplosionInitThing` ownership; ECX-only predicate over `DAT_00672fd0`, `this+0x88`, and `this+0x7c`. Exact owner/timer meaning remains open. |
| 0x004e66d0 | SharedVFunc__ForwardProcessNoOp | Corrects stale `CWaypoint` ownership; `RET 0x4` and ECX passthrough show a one-argument thiscall wrapper around the shared process/no-op path. |
| 0x004e7110 | CSquadNormal__Process | Main process/update path for leader sync, pursuit mode, path/reader state, column/attack formation, static-shadow height, spawn/split, merge, and member-position averaging. |
| 0x004e81d0 | CSquadNormal__EvaluateLeaderTargetPursuitMode | ECX-only helper that reads target/support candidates and ballistic-arc fire readiness before returning a small mode value. |
| 0x004e83b0 | CSquadNormal__PruneDeadMembersAndReschedule | `RET 0x4`; removes null/dead readers from `this+0xa4`, decrements `this+0xb4`, clears formation state when needed, resolves conflicts, and can schedule event `0xfa1`. |
| 0x004e84e0 | CSquadNormal__ResolveFormationSlotConflicts | Walks member-reader nodes, compares transformed formation-slot error, invokes the active-reader swap helper, and returns true when stable. |
| 0x004e8730 | CSquadNormal__BuildColumnFormation | Computes column offsets, marks `this+0xbc` as column mode, resolves conflicts, transforms offsets, and dispatches members through vfunc `+0xf4`. |
| 0x004e8930 | CSquadNormal__BuildAttackFormation | Computes attack offsets, refreshes target/support readers, resolves conflicts, and dispatches members through vfunc `+0xf4`. |
| 0x004e8dd0 | CSquadNormal__ShouldSwitchToAttackFormation | Vtable-backed target-distance predicate gated by observed state `this+0x9c`. |
| 0x004e8ed0 | CSquadNormal__CreateIterator | Corrects undefined signature to return `void *`; allocates and fills a 0x10-byte `CSPtrSet` snapshot from `this+0xa4`. |
| 0x004e8f80 | CSquadNormal__TryMergeWithNearbySquad | `RET 0x4`; scans `DAT_008550a0` for compatible nearby squads and transfers members unless capacity gates block the merge. |
| 0x004e91f0 | CSquadNormal__SpawnMembers | Corrects undefined signature; splits grounded members into new `CSquadNormal` instances or realigns singleton squads to leader/static-shadow height. |
| 0x004e9570 | CSquadNormal__SetFactionAndRefreshGlobalLists | Stores `faction_state` at `this+0x7c`, propagates to member units, and refreshes `DAT_008550c0` / `DAT_008550b0` membership for observed state values `0`, `1`, and `6`. |
| 0x004e97e0 | CGenericActiveReader__SwapWithCandidateIfFormationCloser | Corrects owner from CSquadNormal to active-reader helper; swaps reader assignments when cross-pairing reduces total formation error. |

This is static saved-Ghidra evidence only. Runtime squad AI, exact formation/merge/spawn behavior, concrete member/reader/global-list/faction/event layouts, exact source-body identity, BEA launch behavior, game patching, and rebuild parity remain unproven.

## Wave523 Support Target Range Check

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x004fb3d0 | CSquadNormal__IsValidLinkedSupportForTarget | `RET 0x4` proves one explicit `target_unit` argument after ECX. The body requires a non-null target with vfunc `+0x1b0` success, scans support candidates at `this+0x18c` through `CUnit__IsSupportTargetMaskCompatible`, scans active mask candidates at `this+0x17c`, samples terrain height, and checks profile height-window offsets `+0x6c/+0x70`. |

This is static saved-Ghidra evidence only. Runtime squad support selection, concrete support-list/target/profile layouts, exact source-body identity, BEA launch behavior, game patching, and rebuild parity remain unproven.

## Wave524 Support Range / Selection Helpers

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x004fb780 | CSquadNormal__GetSupportMinEngageDistance | `RET 0x10` proves four explicit stack arguments after ECX. When `this+0x140` is active, the helper forwards the context/vector triple to `CUnit__ComputeMinBallisticTravelDistance`; otherwise it returns the active reader profile field `+0x2c` or a global fallback float. |
| 0x004fb7e0 | CSquadNormal__GetSupportMaxEngageDistance | `RET 0x10` proves four explicit stack arguments after ECX. When `this+0x140` is active, the helper forwards to `CUnit__ComputeMaxBallisticTravelDistance`; otherwise it returns the active reader profile field `+0x30` or a global fallback float. |
| 0x004fb840 | CSquadNormal__SelectBestSupportOrEscort | Corrected during Wave524 read-back to `RET 0x4` / one explicit `target_unit` argument. The body clears prior support state, scores linked support units at `this+0x18c` and active-mask units at `this+0x17c` against target range, mask, height-window, ballistic-distance, and blocked-support predicates, then stores either `this+0x140` or active reader `this+0x144`. |

Wave553 tightened the callee side for the two CUnit ballistic-distance helpers: `CUnit__ComputeMinBallisticTravelDistance` and `CUnit__ComputeMaxBallisticTravelDistance` now have four-dword target-vector signatures, and their non-ballistic fallbacks return profile fields `+0x74/+0x78`. This narrows the support-distance calls but does not prove runtime squad selection behavior.

## Wave766 SquadNormal.cpp Unwind Continuation

Wave766 hardened ten SquadNormal.cpp-adjacent unwind callbacks as `void __cdecl Unwind@...(void)` without renames, function-boundary changes, or executable-byte changes. Representative rows:

| Address | Evidence |
| --- | --- |
| 0x005d4d30 | DATA xref `0x0061d5e4`; `CComplexThing__dtor_base_Thunk_004bff30(*(EBP-0x14))`. |
| 0x005d4d38 | DATA xref `0x0061d5ec`; `CSPtrSet__Clear((*(EBP-0x14))+0xa4)`. |
| 0x005d4d46 | DATA xref `0x0061d5f4`; `CGenericActiveReader__dtor((*(EBP-0x14))+0xc4)`. |
| 0x005d4d54 | DATA xref `0x0061d5fc`; `CGenericActiveReader__dtor((*(EBP-0x14))+0xc8)`. |
| 0x005d4d62 | DATA xref `0x0061d604`; `CDXLandscape__FreeObjectCallback((*(EBP-0x10))+0x10)`. |
| 0x005d4d80 | DATA xref `0x0061d62c`; second `CComplexThing__dtor_base_Thunk_004bff30(*(EBP-0x14))` cleanup row. |
| 0x005d4d88 | DATA xref `0x0061d634`; second `CSPtrSet__Clear((*(EBP-0x14))+0xa4)` cleanup row. |
| 0x005d4db2 | DATA xref `0x0061d64c`; second `CDXLandscape__FreeObjectCallback((*(EBP-0x10))+0x10)` cleanup row. |
| 0x005d4dd0 | DATA xref `0x0061d674`; `OID__FreeObject_Callback(*(EBP+0xc))` with line token `0x81` and allocation/type value `0x0a`. |
| 0x005d4de9 | DATA xref `0x0061d67c`; `CGenericActiveReader__dtor(*(EBP+0xc))`. |

Wave554 support-mask and target/profile gates tightened the adjacent callee side: `CSquadNormal__HasActiveMaskMatchWithTarget` now has one `target_unit` argument and returns `this+0xa8 & target_unit+0x34` only when `this+0x9c` is non-null; `CUnit__HasMaskBitsA8` now has one `mask_bits` argument and returns `this+0xa8 & mask_bits`; `TargetProfileContext__IsEligibleByDistanceBucketOrRange` is owner-neutral shared target/profile context logic rather than a CUnit-only method; and `CUnit__IsTargetTimeoutBeforeProfileLimit` is now documented as an ECX-only timeout/profile predicate. This narrows support-selection callsites but does not prove runtime squad selection behavior.

This is static saved-Ghidra evidence only. Runtime squad support selection, exact support-list/profile layouts, exact selection scoring semantics, source identity, BEA launch behavior, game patching, and rebuild parity remain unproven.

## Wave767 SquadNormal.cpp Unwind Continuation

Wave767 hardened the next two SquadNormal.cpp-adjacent unwind callbacks as `void __cdecl Unwind@...(void)` without renames, function-boundary changes, or executable-byte changes.

| Address | Evidence |
| --- | --- |
| 0x005d4e00 | DATA xref `0x0061d6a4`; `OID__FreeObject_Callback(*(EBP-0x10))` with SquadNormal.cpp line token `0x437` and allocation/type value `0x08`. |
| 0x005d4e30 | DATA xref `0x0061d6cc`; `OID__FreeObject_Callback(*(EBP-0x4e4))` with SquadNormal.cpp line token `0x48b` and allocation/type value `0x08`. |

This is static saved-Ghidra metadata/decompile/xref evidence only. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Exception Handlers (Unwind Functions)

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d4dd0 | Unwind@005d4dd0 | 129 (0x81) | Exception cleanup |
| 0x005d4e00 | Unwind@005d4e00 | 1079 (0x437) | Exception cleanup for CreateIterator |
| 0x005d4e30 | Unwind@005d4e30 | 1163 (0x48b) | Exception cleanup for SpawnMembers |

## Class Structure (Partial)

Based on decompiled code analysis:

```cpp
class CSquadNormal {
    /* 0x00 */ void* vtable1;           // PTR_LAB_005df0f4
    /* 0x04 */ unknown field_4;
    /* 0x08 */ void* vtable2;           // PTR_LAB_005df07c
    /* ... */
    /* 0x1c */ float position[4];       // X, Y, Z, W position vector
    /* ... */
    /* 0x7c */ int field_7c;            // State flag (values 0, 1, 6 observed)
    /* ... */
    /* 0xa4 */ void* memberListHead;    // Linked list of squad members
    /* 0xa8 */ unknown field_a8;
    /* 0xac */ void* currentMember;     // Current iteration pointer
    /* ... */
    /* 0xb4 */ int memberCount;         // Number of members in squad
    /* ... */
    /* 0xc4 */ void* field_c4;          // Resource pointer (cleaned in destructor)
    /* 0xc8 */ void* field_c8;          // Resource pointer (cleaned in destructor)
    /* ... */
    /* 0xe4 */ void* field_e4;          // Resource pointer
    /* 0xec */ void* field_ec;          // Resource pointer
    /* ... */
    /* 0xf4 */ float savedPosition[4];  // Saved position vector
    /* ... */
    /* 0x124 */ float position2[4];     // Secondary position vector
    /* 0x134 */ float position3[4];     // Tertiary position vector
    /* 0x148 */ CSquadNormal* ownerSquad; // Pointer to owning squad
};
```

## VTables

- **Primary vtable**: 0x005df0f4
- **Secondary vtable**: 0x005df07c (at offset 0x08)

## Key Observations

1. **Linked list member management** - Squad members stored in linked list starting at offset 0xa4
2. **Multiple position vectors** - Stores several position vectors for movement/spawning logic
3. **Dual vtables** - Uses two vtable pointers (multiple inheritance or COM-style interfaces)
4. **Timeout-based spawning** - SpawnMembers checks `currentTime - spawnTime < -5.0` for spawn timing
5. **Iterator pattern** - CreateIterator allocates 0x10-byte iterator objects for member traversal
6. **Memory allocation** - Uses OID__AllocObject (tracked allocation with source file/line debug info)

## Wave 366 Correction Note

Earlier static notes and saved Ghidra names treated `0x0044c720` and `0x0044c810` as `CSquadNormal` grid helpers based on caller context. Fresh Wave 366 metadata, decompile, xref, instruction, tag, and callsite review corrected those labels to `CFearGrid__GetOccupancyAtWorldVector` and `CFearGrid__FindNearestFreeCellSpiral`. The checked bodies are called through global FearGrid pointers and operate on FearGrid occupancy/clearance state, not on a `CSquadNormal` instance directly.

This does not invalidate the fact that squad/caller code may consume the grid helpers; it only narrows ownership for the checked callee bodies. Runtime squad behavior and adjacent callers still need their own evidence-grade review.

## Orphan Code at 0x004e6ce0

The xref at 0x004e6e52 points into code that Ghidra hasn't recognized as a function. This code:
- Is referenced from vtable at 0x005df0fc
- Pushes SquadNormal.cpp debug path with line 129 (0x81)
- Contains arithmetic operations suggesting positioning/movement calculations
- Likely a virtual method that wasn't auto-detected

## Source Line References

| Line | Hex | Location | Context |
|------|-----|----------|---------|
| 129 | 0x81 | Orphan (0x004e6e52) via unwind | Unknown method |
| 1079 | 0x437 | CSquadNormal__CreateIterator | Iterator allocation |
| 1163 | 0x48b | CSquadNormal__SpawnMembers | Member spawning |

## Related Functions (Called)

- OID__AllocObject - Memory allocation with debug tracking
- FUN_0047eb80 - Get current game time
- CSPtrSet__Init (`0x004e5840`) - Simple 3-dword zero-init helper (called during construction)
- CSPtrSet__AddToTail (`0x004e5b20`) - Set/list insertion helper (called during Init based on state)
- CSPtrSet__Remove - Remove member from set/list (returns node to pool)
- CSquad__Constructor (`0x004e5da0`) - Base constructor called during CSquadNormal construction
- CSquad__Init (`0x004e5e70`) - Base init called during CSquadNormal init
- CSquadNormal__ScheduleTargetReaderRefresh (`0x004e8100`) - Target-reader/event scheduler called during init
- CSquadNormal__PruneDeadMembersAndReschedule (`0x004e83b0`) - Member prune/reschedule helper called during init and formation rebuild
- FUN_0048dcf0 - Unknown (called during SpawnMembers)
- FUN_00409760 / FUN_00409780 - List iteration helpers
- OID__FreeObject - Memory deallocation

## Investigation Needed

1. Analyze vtable at 0x005df0f4 for complete method list
2. Create function at 0x004e6ce0 (orphan virtual method)
3. Identify remaining Squad methods (likely 0x004e5xxx - 0x004e6xxx range)
4. Cross-reference with Stuart's source code if SquadNormal.cpp is available
5. Document interaction with Unit classes (squad members are Units)

---
*Discovered via debug path xref analysis (Dec 2025)*
*Functions renamed in Ghidra via GhydraMCP*
