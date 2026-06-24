# Infantry.cpp Functions

> Source File: Infantry.cpp | Binary: BEA.exe
> Debug Path: 0x0062d4a8

## Overview

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

Infantry unit implementation. Handles foot soldier spawning, movement, and initialization. Infantry units have smaller scale factors and use angle-based heading calculation. Wave753 added saved static read-back comments/tags/signatures for the adjacent Infantry.cpp unwind cleanup callbacks. Wave805 hardened the CInfantryUnit primary vfunc02 cleanup extension. Wave1082 recovered the CInfantryAI vtable-boundary code-pointer subset tied to table `0x005dbf14`. Wave1180 re-read the CInfantryUnit lifecycle/vfunc contract from the live Ghidra database for rebuild-grade static use.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x00488bb0 | [CInfantry__Init](./CInfantry__Init.md) | Infantry initialization; allocates helper objects and seeds ground-unit state | ~1000 bytes |
| 0x00488dc0 | CInfantryAI__scalar_deleting_dtor | Scalar-deleting destructor wrapper for InfantryAI | ~32 bytes |
| 0x00488de0 | CInfantryAI__dtor_body_00488de0 | Destructor body that restores CUnitAI base vtable, removes pointer-set links, and shuts down monitor state | ~160 bytes |
| 0x00488e80 | CCollisionSeekingInfantryBloke__scalar_deleting_dtor | Scalar-deleting destructor wrapper for the collision-seeking infantry helper | ~32 bytes |
| 0x00488ea0 | CCollisionSeekingInfantryBloke__dtor_body_00488ea0 | Destructor body that shuts down monitor state and chains to collision-seeking round cleanup | ~80 bytes |
| 0x00488ef0 | CCollisionSeekingThing__ctor_base | Collision-seeking helper constructor-base vtable setup | ~16 bytes |
| 0x00488f00 | CHLCollisionDetector__ctor_base | High-level collision detector constructor-base vtable setup | ~16 bytes |
| 0x00488f10 | CInfantryUnit__VFunc38_HandleHitOrDispatchHit | Wave1076 CInfantryUnit primary vtable slot-38 hit/collision dispatch boundary | ~96 bytes |
| 0x00488f60 | CInfantryUnit__VFunc02_ClearParticleLinkAndForward | CInfantryUnit vfunc02 cleanup extension; clears the `this+0x270` particle/effect owner-link cell and forwards to CUnit slot-2 cleanup | ~32 bytes |
| 0x00488f80 | CInfantryUnit__VFunc34_CreateCollisionSphereWithAttachmentRadius | Wave1076 slot-34 collision-sphere helper with Infantry.cpp allocation-token evidence | ~176 bytes |
| 0x00489090 | CInfantryUnit__VFunc59_SelectAnimationMode | Wave1076 slot-59 animation-mode selector with mesh-animation lookup evidence | ~544 bytes |
| 0x004892c0 | CInfantryUnit__VFunc65_UpdateMotionAnimationState | Wave1076 slot-65 motion/effects/shadow animation-state update boundary | ~880 bytes |
| 0x00489650 | CInfantryUnit__VFunc39_HandleCollisionDamageReaction | Wave1076 slot-39 collision-damage/reaction boundary | ~1264 bytes |
| 0x00489b40 | CInfantryUnit__VFunc49_HandleDeathPickupAndEffects | Wave1076 slot-49 death/pickup/effect completion boundary | ~672 bytes |
| 0x0048a030 | CInfantryAI__UpdateSupportSelection_0048a030 | Wave1082 CInfantryAI vtable slot-9 support-selection boundary tied to table `0x005dbf14` | ~704 bytes |
| 0x0048a3c0 | CInfantryGuide__ctor | Infantry guide constructor with owner-unit argument and guide/monitor setup | ~240 bytes |
| 0x0048a4b0 | SharedGuide__GetField24Block_0048a4b0 | Shared compact vtable-slot helper returning `this+0x24` block | ~16 bytes |
| 0x0048a4c0 | CInfantryGuide__scalar_deleting_dtor | Scalar-deleting destructor wrapper for the infantry guide helper | ~32 bytes |
| 0x0048a4e0 | CInfantryGuide__dtor | Infantry guide helper destructor body (reader/unregister + monitor shutdown) | ~160 bytes |
| 0x0048a570 | CInfantryGuide__UpdateGuidanceState_0048a570 | Infantry guide vtable slot-3 update/guidance-state body | ~1792 bytes |
| 0x0048ac70 | CInfantryGuide__HandleTargetRecheckEvent | Infantry guide event-id 2000 handler that selects a target and reschedules recheck | ~112 bytes |
| 0x0048ace0 | CInfantryGuide__SelectNearestTargetReader | Infantry guide target-selection helper over nearby map-who entries | ~544 bytes |
| 0x0050ee30 | CInfantryUnit__scalar_deleting_dtor | Wave557 CInfantryUnit primary vtable slot-1 wrapper; calls `CInfantryUnit__Destructor_VFunc01` and optionally frees `this` on `delete_flags & 1` | ~32 bytes |
| 0x0050f1a0 | CInfantryUnit__Destructor_VFunc01 | Wave557 CInfantryUnit destructor body; removes the `this+0x270` global-list node, then calls `CUnit__dtor_base` | ~80 bytes |

## Exception Handlers

Wave753 static read-back (`unwind-continuation-wave753`, `wave753-readback-verified`) hardened these rows as `void __cdecl Unwind@...(void)` and tied them to DATA scope-table xrefs, the Infantry.cpp debug path at `0x0062d4a8`, and helper calls. Exact anchors include `0x005d2e10 Unwind@005d2e10` and `0x005d2e78 Unwind@005d2e78`. Verified backup: `G:\GhidraBackups\BEA_20260522-221626_post_wave753_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

| Address | Name | Scope-table xref | Static read-back evidence |
|---------|------|------------------|---------------------------|
| 0x005d2e10 | Unwind@005d2e10 | 0x0061bbec | `OID__FreeObject_Callback` on `*(EBP+0x4)` with line token `0x0b` and allocation/type value `0x1c` |
| 0x005d2e26 | Unwind@005d2e26 | 0x0061bbf4 | `CCollisionSeekingRound__Destructor(*(EBP+0x4))` |
| 0x005d2e2e | Unwind@005d2e2e | 0x0061bbfc | `OID__FreeObject_Callback` on `*(EBP+0x4)` with line token `0x17` and allocation/type value `0x46` |
| 0x005d2e44 | Unwind@005d2e44 | 0x0061bc04 | `OID__FreeObject_Callback` on `*(EBP+0x4)` with line token `0x16` and allocation/type value `0x47` |
| 0x005d2e70 | Unwind@005d2e70 | 0x0061bc2c | `CMonitor__Shutdown(*(EBP-0x10))` |
| 0x005d2e78 | Unwind@005d2e78 | 0x0061bc34 | `CGenericActiveReader__dtor((*(EBP-0x10))+0x0c)` |

## Key Observations

- **Wave1180 CInfantryUnit lifecycle/vfunc current-risk review** (`wave1180-cinfantryunit-lifecycle-vfunc-current-risk-review`) - Fresh Ghidra export evidence re-read `8 CInfantryUnit lifecycle/vfunc current-risk rows` with no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change. Codex read-only consults used; one adversarial consult recommended already-counted CUnitAI door-wing rows, while Codex root final judgment rejected duplicate Wave1116 accounting and kept the CInfantryUnit slice; root rejected duplicate Wave1116 accounting; the infantry consult recommended exact eight-row CInfantryUnit slice. no Cursor/Composer was used. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt; Wave1108 current focused accounting is `729/1179 = 61.83%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 450; current risk candidates: 6166; fresh Ghidra export; read-only review; `8 xref rows`; `1150 instruction rows`; anchors `CInfantryUnit__VFunc38_HandleHitOrDispatchHit`, `CInfantryUnit__VFunc02_ClearParticleLinkAndForward`, `CInfantryUnit__VFunc34_CreateCollisionSphereWithAttachmentRadius`, `CInfantryUnit__VFunc59_SelectAnimationMode`, `CInfantryUnit__VFunc65_UpdateMotionAnimationState`, `CInfantryUnit__VFunc39_HandleCollisionDamageReaction`, `CInfantryUnit__VFunc49_HandleDeathPickupAndEffects`, and `CInfantryUnit__Destructor_VFunc01`; backup `G:\GhidraBackups\BEA_20260606-104634_post_wave1180_cinfantryunit_lifecycle_vfunc_current_risk_review_verified`; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction. Runtime infantry behavior, runtime hit/collision/damage/death/pickup/effect behavior, exact concrete CInfantryUnit/CUnit/CUnitAI/layout semantics, exact source virtual names, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof. Static clean-room target: rebuild-grade static contracts for a future clean-room implementation aiming at no noticeable difference.
- **Wave416 lifecycle correction** - Saved Ghidra now distinguishes InfantryAI destructor wrappers/bodies, collision-seeking infantry helper destructor paths, and adjacent constructor-base helpers.
- **Wave417 InfantryGuide correction** - Saved Ghidra now has the CInfantryGuide constructor, scalar-deleting destructor wrapper, slot-3 update body, true `0x0048ac70` event-handler boundary, nearest-target reader, and shared guide field-block helper. The old `0x0048ac80` entry was a stale mid-body boundary and is no longer a saved function entry.
- **Wave1077 InfantryGuide lifecycle review** (`infantryguide-lifecycle-review-wave1077`) - Saved Ghidra now also resolves CInfantryGuide vtable `0x005dbfa8` slots `4` through `8` to shared guide-family functions: `0x0047e2d0 SharedGuide__VFunc04_SetVectorMode1_0047e2d0`, `0x0047e310 SharedGuide__VFunc05_SetVectorMode2_0047e310`, `0x0047e340 SharedGuide__VFunc06_SetVectorMode3_0047e340`, `0x0047e370 SharedGuide__VFunc07_SetVectorModeFromOwnerState_0047e370`, and `0x0047e3d0 SharedGuide__VFunc08_ResetVectorsFromOwner_0047e3d0`. The same pass recovered `0x0047d750 CGroundVehicleGuide__VFunc03_UpdateGuidanceState_0047d750` for CGroundVehicleGuide vtable `0x005dbd90` slot `3`. Queue closure is `6260/6260 = 100.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface is `1371/1560 = 87.88%`; top-500 remains `500/500 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260602-073929_post_wave1077_infantryguide_lifecycle_review_verified`. Exact source virtual names, concrete guide/vector/class layouts, runtime InfantryGuide or GroundVehicleGuide behavior, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.
- **Wave1082 CInfantryAI vtable-boundary recovery** (`infantryai-vtable-boundary-review-wave1082`) - Saved Ghidra now resolves eleven previously unresolved CInfantryAI/shared UnitAI vtable code-pointer boundaries from table `0x005dbf14`, including `0x004ff330 SharedUnitAI__HandleEventAndMaybeFire_004ff330`, `0x0048a030 CInfantryAI__UpdateSupportSelection_0048a030`, and `0x004f45c0 SharedVFunc__ForwardField64FloatOrZero_004f45c0`. Post CInfantryAI vtable-slot export improves from `71` OK / `25` unresolved candidates to `82` OK / `14` unresolved `.rdata` or no-memory literal/float-like entries. Queue closure is `6294/6294 = 100.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface is `1405/1560 = 90.06%`; top-500 remains `500/500 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260602-110925_post_wave1082_infantryai_vtable_boundary_verified`. Exact source virtual names, concrete `CUnitAI`/`CInfantryAI`/reader/vector field layout semantics, runtime AI targeting/firing/support-selection/event-scheduling/animation behavior, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.
- **Wave557 primary CInfantryUnit lifecycle** - Saved Ghidra now distinguishes `CInfantryUnit__scalar_deleting_dtor` and `CInfantryUnit__Destructor_VFunc01` in the adjacent factory/lifecycle range. This is static retail-binary evidence only; exact layout, runtime teardown behavior, and rebuild parity remain unproven.
- **Wave805 InfantryUnit vfunc02 cleanup** (`infantryunit-vfunc02-wave805`) - Saved Ghidra now renames the old `0x00488f60 CInfantryUnit__VFunc_02_00488f60` placeholder to `0x00488f60 CInfantryUnit__VFunc02_ClearParticleLinkAndForward` with `void __fastcall ... (void * this)`. CInfantryUnit primary vtable `0x005e2730` slot `0x005e2734` points here; the body clears `ParticleEffectLink__SetHandleStateAndClear(this+0x270, 0)` and forwards to `CUnit__VFunc02_CleanupWorldLinksAndForward(this)`. Queue after Wave805: `5577/6098 = 91.46%`; next raw commentless row is `0x0048ddf0 thunk_DXMemBuffer__Close`. Verified backup: `G:\GhidraBackups\BEA_20260524-094441_post_wave805_infantryunit_vfunc02_verified`. Exact source virtual name, concrete infantry-unit particle/effect link layout, runtime cleanup order, BEA patching, and rebuild parity remain deferred.
- **Wave1076 InfantryUnit lifecycle boundary recovery** (`infantryunit-lifecycle-boundary-wave1076`) - Saved Ghidra recovered six previously missing CInfantryUnit primary-vtable function boundaries: `0x00488f10 CInfantryUnit__VFunc38_HandleHitOrDispatchHit`, `0x00488f80 CInfantryUnit__VFunc34_CreateCollisionSphereWithAttachmentRadius`, `0x00489090 CInfantryUnit__VFunc59_SelectAnimationMode`, `0x004892c0 CInfantryUnit__VFunc65_UpdateMotionAnimationState`, `0x00489650 CInfantryUnit__VFunc39_HandleCollisionDamageReaction`, and `0x00489b40 CInfantryUnit__VFunc49_HandleDeathPickupAndEffects`. CInfantryUnit primary vtable `0x005e2730` ties them to slot addresses `0x005e27b8`, `0x005e27c8`, `0x005e27cc`, `0x005e27f4`, `0x005e281c`, and `0x005e2834`; post-Wave1076 queue closure is `6254/6254 = 100.00%`, Wave911 focused progress is `812/1408 = 57.67%`, expanded static surface progress is `1365/1560 = 87.50%`, and top-500 remains `500/500 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260602-065500_post_wave1076_infantryunit_lifecycle_boundary_verified`. Exact source virtual names, concrete CInfantryUnit/CUnitAI/layout semantics, runtime infantry behavior, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.
- **Three-stage initialization** - Allocates 0x38, 0x48, and 0x60 byte objects
- **Scale factor** - Sets scale to 4.0f at offset 0x260 (or 1.0f with special flag)
- **Heading calculation** - Uses fpatan() to compute initial facing from X/Y
- **State flags** - Sets flags at 0x80 to 1, 0x70 to 0x2000010
- **Position from parent** - Reads spawn position from offset 0x3bc
- **VTable references** - Uses vtables at 0x5dbf48 and 0x5dbf14

## Related Files

- Unit.cpp - CInfantry likely inherits from CUnit
- Player.cpp - Kill tracking counts infantry kills (TK_INFANTY index 3; typo preserved)

---
*Discovered via Phase 1 xref analysis (Dec 2025); lifecycle metadata corrected by Wave416 static read-back (2026-05-14), and InfantryGuide metadata/boundaries corrected by Wave417 static read-back (2026-05-14).*
