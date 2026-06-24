# HiveBoss.cpp Functions

> Source File: HiveBoss.cpp | Binary: BEA.exe
> Debug Path: 0x0062cc98

> **Current authority (2026-06-21):** Active static accounting is centralized in `reverse-engineering/binary-analysis/static-reaudit-measurement-register.md` and validated by Wave1220. Current closure is `6411/6411 = 100.00%`, static debt is `0 / 0 / 0`, and active current-risk focused accounting is `1179/1179 = 100.00%`. Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Hive Boss enemy implementation. CHiveBoss is a boss-type unit that inherits from CUnit and uses the "core2" model. Wave432 added the adjacent `CMCHiveBoss` motion-controller correction for the subobject allocated at owner `+0x178`. Wave753 added saved static read-back comments/tags/signatures for the adjacent HiveBoss.cpp unwind cleanup callbacks. Wave921 re-reviewed the HiveBoss config/init/motion-controller cluster read-only and found no mutation warranted. Wave942 normalized the adjacent destructable-segments motion-controller comments/tags against the recovered CMCHiveBoss boundaries. Wave958 re-reviewed the `0x004804c0 CHiveBoss__SetVar` fallback into `0x004f45e0 CComplexThing__SetVar` and found no mutation needed. Wave1087 recovered ten CHiveBoss/unit-family vtable-tail boundaries from vtable `0x005e1668`. Wave1127 re-read and tag-normalized `0x004804c0 CHiveBoss__SetVar`. Wave1177 re-read `0x0047fe30 CHiveBoss__Init`, `0x00480050 CHiveBossVFunc__ForwardApplyDamageUnlessFlag01000000_00480050`, and `0x00480080 CHiveBossVFunc__ComputeScaledOffsetVectorToOut_00480080` as current-risk HiveBoss rows.

Wave1177 (`wave1177-hiveboss-init-vfunc-current-risk-review`) accounts for `3 CHiveBoss init/vfunc current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It is a read-only review with no mutation, and Codex read-only consult used while Codex root final judgment retained this already-exported HiveBoss mini-cluster for Wave1177. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; Wave1108 current focused accounting is now `695/1179 = 58.95%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 484; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `3 xref rows` and `249 instruction rows`; prior Wave397/Wave921/Wave1087/Wave1127/Wave1140 read-back evidence remains the provenance base. Verified backup: `G:\GhidraBackups\BEA_20260606-091847_post_wave1177_hiveboss_init_vfunc_current_risk_review_verified`. Static clean-room target: the retail-static contract should support a future rebuild implementation aiming at no noticeable difference, while runtime HiveBoss behavior, runtime boss damage gating, runtime guide/target/vector behavior, exact CHiveBoss layout, exact source virtual names, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

| Wave1177 address | Static contract |
| --- | --- |
| `0x0047fe30 CHiveBoss__Init` | DATA xref `0x005e1704`; allocates and wires the destructable-segment controller, `CMCHiveBoss`, `CUnit__Init`, `core2` lookup, guide object, and seeded HiveBoss floats. |
| `0x00480050 CHiveBossVFunc__ForwardApplyDamageUnlessFlag01000000_00480050` | DATA xref `0x005e1780`; slot-70 path checks source flags for `0x01000000`, forwards to `CUnit__ApplyDamage` only when clear, and returns with the observed stack cleanup. |
| `0x00480080 CHiveBossVFunc__ComputeScaledOffsetVectorToOut_00480080` | DATA xref `0x005e1898`; slot-140 path computes a scaled vector output using `DAT_008a9d3c`, field `+0x2a0`, and `CStaticShadows__SampleShadowHeightBilinear`. |

Probe token anchor: Wave1177; wave1177-hiveboss-init-vfunc-current-risk-review; 695/1179 = 58.95%; 3 CHiveBoss init/vfunc current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 484; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult used; Codex root final judgment; prior Wave397/Wave921/Wave1087/Wave1127/Wave1140 read-back evidence; 0 / 0 / 0; 6411/6411 = 100.00%; 3 xref rows; 249 instruction rows; 0x0047fe30 CHiveBoss__Init; 0x00480050 CHiveBossVFunc__ForwardApplyDamageUnlessFlag01000000_00480050; 0x00480080 CHiveBossVFunc__ComputeScaledOffsetVectorToOut_00480080; G:\GhidraBackups\BEA_20260606-091847_post_wave1177_hiveboss_init_vfunc_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Wave1140 (`wave1140-motion-controller-current-risk-review`) re-read the motion-controller residual current-risk cluster including HiveBoss anchors `0x00497090 CMCHiveBoss__Constructor`, `0x00497140 CDestructableSegmentsMotionController__CacheNamedCollisionCylinders`, `0x00494fa0 SharedMotionController__VFunc_UpdateUnitAIIndexedEntryFlag`, `0x00494ff0 SharedMotionController__VFunc_CallUnitAIIndexedEntryVFunc10`, `0x0049c1d0 CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0`, `0x0049c3e0 CMCMine__Constructor`, `0x0049c440 CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440`, `0x0049c5d0 CMCSentinel__Constructor`, and `0x0049f820 SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820`. It covers `9 current-risk rows`; current focused accounting is `238/1179 = 20.19%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 941; static debt `0 / 0 / 0`; static closure `6411/6411 = 100.00%`. This was a fresh Ghidra export, read-only review, no mutation. Verified backup: `G:\GhidraBackups\BEA_20260605-142515_post_wave1140_motion_controller_current_risk_review_verified`; previous completed backup: `G:\GhidraBackups\BEA_20260605-134608_post_wave1139_battleengine_jetpart_current_risk_review_verified`. Runtime motion-controller behavior, exact layouts, and rebuild parity remain separate proof.

Wave958 (`ccomplexthing-setvar-review-wave958`) verified that `CHiveBoss__SetVar` still handles `hb_*` config names before falling back to the base unknown-variable warning path. The base fallback pushes `Warning: Uknown var`, calls `CConsole__Printf`, and returns at `0x004f45fc` with `RET 0x8`; the saved base signature remains `void __stdcall CComplexThing__SetVar(void * var_name, void * data)`. Wave911 focused re-audit progress after Wave958 is `293/1408 = 20.81%`; static closure remains `6151/6151 = 100.00%`; verified backup `G:\GhidraBackups\BEA_20260528-114016_post_wave958_ccomplexthing_setvar_review_verified`. Runtime mission-script variable behavior, exact `CStringDataType` / `CDataType` layouts, exact virtual dispatch target identity, runtime console output behavior, BEA patching, and rebuild parity remain separate proof.

Wave1087 (`hiveboss-unit-vtable-tail-review-wave1087`) recovered and saved ten previously missing CHiveBoss/unit-family vtable-tail function boundaries from vtable `0x005e1668`. The CHiveBoss vtable-tail sample now reports `158` OK / `2` `NO_FUNCTION_AT_POINTER`; the two remaining unresolved rows are deliberate `.rdata`/non-function entries at slots `29` and `147`. Queue closure is `6365/6365 = 100.00%`; expanded static surface progress is `1482/1560 = 95.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; top-500 remains `500/500 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260602-141730_post_wave1087_hiveboss_unit_vtable_tail_verified`. Exact source virtual names, concrete CHiveBoss/unit-family layout semantics, runtime behavior, gameplay outcomes, BEA patching, and rebuild parity remain separate proof. Probe token anchor: Wave1087; hiveboss-unit-vtable-tail-review-wave1087; 0x00480000 CHiveBossVFunc__CheckField170AndMaybeReturn64_00480000; 0x0050eb10 CHiveBossVFunc__GetClassNameString_0050eb10; 0x00480050 CHiveBossVFunc__ForwardApplyDamageUnlessFlag01000000_00480050; 0x00480220 CHiveBossVFunc__AccumulateMotionOffsetsThenTailJmp4fa8d0_00480220; 0x00480340 CHiveBossVFunc__BuildField164ContextAndDispatch_00480340; 0x00480080 CHiveBossVFunc__ComputeScaledOffsetVectorToOut_00480080; 158 OK / 2 NO_FUNCTION_AT_POINTER; 1482/1560 = 95.00%; 812/1408 = 57.67%; 500/500 = 100.00%; 6365/6365 = 100.00%; G:\GhidraBackups\BEA_20260602-141730_post_wave1087_hiveboss_unit_vtable_tail_verified; boundary recovery.

Wave1127 (`wave1127-mixed-score23-current-risk-review`) re-read and tag-normalized `0x004804c0 CHiveBoss__SetVar` as a score-23 current-risk row. Fresh evidence keeps the handler tied to the `hb_*` config-name chain including `s_hb_maxvelx` and `s_hb_safe_dist`, followed by the base `CComplexThing__SetVar` unknown-var fallback when no HiveBoss-specific name matches. Wave1127 added tags only; no rename, signature, comment, function-boundary, or executable-byte change was made. Verified backup: `G:\GhidraBackups\BEA_20260605-071212_post_wave1127_mixed_score23_current_risk_review_verified`. Runtime mission-script variable behavior, exact `CHiveBoss`/config layout, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x0047fe30 | CHiveBoss__Init | Initialize boss with sub-objects, `core2` segment lookup, guide object, and seeded HiveBoss fields | ~400 bytes |
| 0x004804c0 | CHiveBoss__SetVar | Handles `hb_*` config float fields and falls back to the base unknown-var path | ~300 bytes |

## Wave1087 CHiveBoss Unit Vtable Tail Review

Wave1087 hardened the recovered vtable-tail rows as bounded static names/signatures/comments/tags without an executable-byte change, BEA launch, runtime/game-file mutation, or installed-game mutation. Representative read-back rows:

| Address | Name | Slot / xref | Static read-back evidence |
| --- | --- | --- | --- |
| 0x00480000 | CHiveBossVFunc__CheckField170AndMaybeReturn64_00480000 | slot 26 / `0x005e16d0` | Checks field `+0x170`, uses the `!!all flash!!` string at `0x0062ccb8`, and returns the bounded `0x64` value only under the observed branch pattern. |
| 0x0050eb10 | CHiveBossVFunc__GetClassNameString_0050eb10 | slot 37 / `0x005e16fc` | Returns the `CHiveBoss` string at `0x0063d844`. |
| 0x0050eb20 | CHiveBossVFunc__ForwardArgWithFlags40100400_0050eb20 | slot 68 / `0x005e1778` | Forwards the argument through the shared unit-family helper path with flag value `0x40100400`. |
| 0x00480050 | CHiveBossVFunc__ForwardApplyDamageUnlessFlag01000000_00480050 | slot 70 / `0x005e1780` | Gates a damage-style forwarding path on flag `0x01000000`. |
| 0x0050eb40 | CHiveBossVFunc__ReturnFloat005d8580_0050eb40 | slot 75 / `0x005e1794` | Returns the global float at `0x005d8580`. |
| 0x004802f0 | CHiveBossVFunc__MaybeScheduleEvent1388ForField74_004802f0 | slot 80 / `0x005e17a8` | Checks field `+0x74` and follows an event-style `0x1388` scheduling path. |
| 0x00480220 | CHiveBossVFunc__AccumulateMotionOffsetsThenTailJmp4fa8d0_00480220 | slot 96 / `0x005e17e8` | Accumulates observed motion-offset fields before tail-jumping into the `0x004fa8d0` shared helper. |
| 0x00480690 | CHiveBossVFunc__ForwardArgToThingHelper4f3ac0_00480690 | slot 120 / `0x005e1848` | Forwards the argument into the bounded `0x004f3ac0` CThing-family helper path. |
| 0x00480340 | CHiveBossVFunc__BuildField164ContextAndDispatch_00480340 | slot 125 / `0x005e185c` | Builds a context around field `+0x164` and dispatches through the recovered helper path. |
| 0x00480080 | CHiveBossVFunc__ComputeScaledOffsetVectorToOut_00480080 | slot 140 / `0x005e1898` | Computes a scaled offset-vector output from observed fields and constants. |

## Motion Controller Functions

| Address | Name | Purpose | Status |
|---------|------|---------|--------|
| 0x00497090 | CMCHiveBoss__Constructor | Constructs the destructable-segments motion-controller subobject, passes owner `+0x178` to the base constructor, clears cached cylinder slots, and installs vtable `0x005dc388`. | SAVED IN GHIDRA |
| 0x00497110 | CMCHiveBoss__ScalarDeletingDestructor | Vtable slot-1 scalar-deleting destructor wrapper that calls the destructable-segments destructor thunk. | SAVED IN GHIDRA |
| 0x004976d0 | CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0 | Recovered vtable slot-4 boundary; lazily caches named collision cylinders, applies rumble transforms, and updates cached cylinder transform groups. | SAVED IN GHIDRA |

## Wave942 Destructable-Segments Motion Review

Wave942 (`destructable-segments-motion-review-wave942`) re-reviewed the CMCHiveBoss bridge into the destructable-segments motion controller and saved six comment/tag normalizations. This was a comment-only mutation: no rename, no signature change, no function-boundary change, and no executable-byte change.

Read-back ties `0x00497090 CMCHiveBoss__Constructor` to `0x00494c60 CDestructableSegmentsMotionController__Ctor` with `owner_hiveboss+0x178`, `0x00497110 CMCHiveBoss__ScalarDeletingDestructor` to `0x00497130 CDestructableSegmentsMotionController__DestructorThunk_00497130`, and `0x004976d0 CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0` to both `0x00497140 CDestructableSegmentsMotionController__CacheNamedCollisionCylinders` at `0x004976f1` and `0x00494ce0 CDestructableSegmentsMotionController__ApplyRumbleTransform` at `0x00497711`. Vtable anchors `0x005dc27c` and `0x005dc388` preserve the destructable-segments and HiveBoss motion-controller tables.

Wave911 focused re-audit progress after Wave942 is `180/1408 = 12.78%`; static export-contract closure remains `6113/6113 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260528-040608_post_wave942_destructable_segments_motion_review_verified`.

Probe token anchor: Wave942; `destructable-segments-motion-review-wave942`; comment-only mutation; `0x00494c60 CDestructableSegmentsMotionController__Ctor`; `0x00494ca0 CDestructableSegmentsMotionController__ScalarDeletingDestructor`; `0x00494cc0 CDestructableSegmentsMotionController__Destructor`; `0x00494ce0 CDestructableSegmentsMotionController__ApplyRumbleTransform`; `0x00497130 CDestructableSegmentsMotionController__DestructorThunk_00497130`; `0x00497140 CDestructableSegmentsMotionController__CacheNamedCollisionCylinders`; `0x00497090 CMCHiveBoss__Constructor`; `0x00497110 CMCHiveBoss__ScalarDeletingDestructor`; `0x004976d0 CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0`; `0x004976f1`; `0x005dc27c`; `0x005dc388`; `180/1408 = 12.78%`; `6113/6113 = 100.00%`; `G:\GhidraBackups\BEA_20260528-040608_post_wave942_destructable_segments_motion_review_verified`.

Runtime HiveBoss rumble/cylinder behavior, exact destructable-segments motion-controller and CMCHiveBoss layouts, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

## Exception Handlers

Wave753 static read-back (`unwind-continuation-wave753`, `wave753-readback-verified`) hardened these rows as `void __cdecl Unwind@...(void)` and tied them to DATA scope-table xrefs, the HiveBoss.cpp debug path at `0x0062cc98`, and `OID__FreeObject_Callback`. Exact anchor: `0x005d2cb0 Unwind@005d2cb0`. Verified backup: `G:\GhidraBackups\BEA_20260522-221626_post_wave753_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

| Address | Name | Scope-table xref | Static read-back evidence |
|---------|------|------------------|---------------------------|
| 0x005d2cb0 | Unwind@005d2cb0 | 0x0061ba9c | `OID__FreeObject_Callback` on `*(EBP+0x4)` with line token `0x55` and allocation/type value `0x21` |
| 0x005d2cc6 | Unwind@005d2cc6 | 0x0061baa4 | `OID__FreeObject_Callback` on `*(EBP+0x4)` with line token `0x1b` and allocation/type value `0x22` |
| 0x005d2cdc | Unwind@005d2cdc | 0x0061baac | `OID__FreeObject_Callback` on `*(EBP+0x4)` with line token `0x17` and allocation/type value `0x28` |

## Key Observations

- **Inherits CUnit** - Calls CUnit__Init during initialization
- **"core2" model** - Loads model via FUN_00444520("core2")
- **Factory pattern** - Function pointer at 0x005e1704
- **Three sub-objects** - Dynamically allocated components
- **Config field handler** - Wave397 corrects the older `CExplosionInitThing` owner label at `0x004804c0` to `CHiveBoss__SetVar`; static read-back shows `hb_*` name checks for guide velocities, rotation speeds, safe distance, and minimum ground clearance style fields.
- **Motion controller** - Wave432 corrects `CMCHiveBoss` vtable `0x005dc388` slot `4` to the recovered cylinder-transform boundary at `0x004976d0`; this remains static boundary/name evidence, not runtime motion proof.
- **Wave921 read-only review** - Fresh metadata, tags, xrefs, instructions, and decompile exports verified `CHiveBoss__Init`, `CHiveBoss__SetVar`, `CMCHiveBoss__Constructor`, `CMCHiveBoss__ScalarDeletingDestructor`, and `CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0`; no Ghidra mutation was needed.

## Memory Allocations

| Line | Size | Type ID | Offset | Purpose |
|------|------|---------|--------|---------|
| 33 | 48 bytes | 0x55 | +0x178 | Sub-object #1 |
| 34 | 120 bytes | 0x1B | +0x70 | Sub-object #2 |
| 40 | 44 bytes | 0x17 | +0x208 | Sub-object #3 (vtable 0x5DBE08) |

## Float Constants

| Value | Float | Offset | Purpose |
|-------|-------|--------|---------|
| 0x41200000 | 10.0f | +0x12C | Initial value |
| 0x41F00000 | 30.0f | +0x2A0 | Range/distance |
| 0xBF800000 | -1.0f | +0x268 | Unset/invalid state |
| 0x3CA3D70A | 0.02f | sub-object | Rate/speed |

## Class Hierarchy

```
CUnit
  └── CHiveBoss (uses "core2" model)
```

## Related Files

- Unit.cpp - CUnit base class
- BattleEngine.cpp - Combat system
- `release/readiness/ghidra_help_hive_wave397_2026-05-14.md` - Saved Ghidra read-back evidence for `CHiveBoss__Init` and `CHiveBoss__SetVar`.
- `release/readiness/ghidra_cmcgroundattack_hiveboss_wave432_2026-05-15.md` - Saved Ghidra read-back evidence for the `CMCGroundAttack` / `CMCHiveBoss` motion-controller correction.

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
