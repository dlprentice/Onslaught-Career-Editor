# thing.cpp

Wave1217 (`wave1217-lifecycle-cleanup-tail-current-risk-review`) re-read and comment/tag-normalized the object lifecycle tail row `CCSPersistentThing__dtor_base` with adjacent CThing/CComplexThing destructor context. Fresh static evidence keeps it tied to the persistent collision helper cleanup path and the base `CThing__dtor_base` neighborhood, with no rename, signature, function-boundary, or executable-byte change. Verified backup: `G:\GhidraBackups\BEA_20260607-110625_post_wave1217_lifecycle_cleanup_tail_current_risk_review_verified`. Runtime collision-helper cleanup behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Wave1216 (`wave1216-render-resource-texture-hud-tail-current-risk-review`) re-read `CThing__InitRenderThingFromInitMeshName` as part of the render/resource/texture/HUD tail current-risk review. Verified backup: `G:\GhidraBackups\BEA_20260607-101007_post_wave1216_render_resource_texture_hud_tail_current_risk_review_verified`. Runtime render behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

> Base game object class (CThing) from BEA.exe

**Debug Path**: `C:\dev\ONSLAUGHT2\thing.cpp` at `0x006331c0`

## Overview
> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

CThing is the base class for all game objects in Battle Engine Aquila. CComplexThing extends it with orientation, animation, mission-script, motion-controller, and name ownership. This file provides fundamental functionality for:
- Collision detection and handling
- Object naming/identification through CComplexThing
- Mission-script event hooks
- Animation mode and render-frame helpers

This is a foundational class - most game entities (units, projectiles, buildings) inherit through CThing / CComplexThing.

## 2026-06-07 Wave1211 Score-17 Residual Current-Risk Review

Wave1211 (`wave1211-score17-residual-current-risk-review`) re-read and tag-normalized `0x004f45e0 CComplexThing__SetVar` as one of `8 score-17 residual current-risk rows` in the current-risk denominator. Fresh evidence keeps the row tied to the base script-variable fallback warning path (`Warning: Uknown var`) and the `RET 0x8` two-argument signature already recorded by Wave958. No rename, signature, comment, function-boundary, or executable-byte change was made. Active current-risk accounting after the wave is `1110/1179 = 94.15%`; verified backup: `G:\GhidraBackups\BEA_20260607-061324_post_wave1211_score17_residual_current_risk_review_verified`. Runtime MissionScript variable behavior, exact datatype/layout identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

## 2026-06-05 Wave1127 Opening Animation State Callback

Wave1127 (`wave1127-mixed-score23-current-risk-review`) re-read and tag-normalized `0x00418090 OpeningAnimationStateCallback__StartOpeningIfPending` as a score-23 current-risk row. Fresh evidence keeps the callback tied to an opening-animation state record: it checks the state field around `+0x254`, resolves the `opening` animation string through `CMesh__FindAnimationIndexByName`, and writes adjacent state around `+0x25c`. Wave1127 added tags only; no rename, signature, comment, function-boundary, or executable-byte change was made. Verified backup: `G:\GhidraBackups\BEA_20260605-071212_post_wave1127_mixed_score23_current_risk_review_verified`. Runtime opening-animation behavior, exact state-record layout, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

## 2026-06-02 Wave1081 CThing/Waypoint Residual Vtable Boundary Recovery

Wave1081 (`cthing-waypoint-residual-vtable-boundary-wave1081`) recovered additional CThing/CWaypoint residual true-vtable boundary rows that had previously appeared as raw table pointers. CThing vtable `0x005df550` and CWaypoint vtable `0x005dd278` now resolve `0x004bfa00 SharedVFunc__CopyGlobal829dd0Block30ToOut_004bfa00`, `0x004bfa20 SharedVFunc__CopyGlobal829dd0Block30ToOut_004bfa20`, `0x004bfa40 SharedVFunc__CopyGlobal829dd0Block30ToOut_004bfa40`, `0x004f3760 CThing__AddShutdownEvent_004f3760`, `0x004f37a0 CThing__StartDieProcess_004f37a0`, `0x004f3d20 SharedVFunc__ForwardField28Slot10OrNull_004f3d20`, and `0x0043e9c0 SharedVFunc__CopyGlobal0066ea10Block10ToOut_0043e9c0`. CInfantryAI vtable `0x005dbf14` also references `0x004f3d20 SharedVFunc__ForwardField28Slot10OrNull_004f3d20`.

Static body evidence ties `CThing__AddShutdownEvent_004f3760` to `this+0x2c` bit `0x1` plus event id `0x7d0`, matching the Stuart-source `CThing::AddShutdownEvent` shape; `CThing__StartDieProcess_004f37a0` tests/sets `this+0x2c` bit `0x4`, dispatches same-object vtable slot `+0x38`, and returns first-transition boolean, matching the `CThing::StartDieProcess` shape. Queue closure is `6283/6283 = 100.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface advances to `1394/1560 = 89.36%`; top-500 remains `500/500 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260602-103048_post_wave1081_cthing_waypoint_residual_vtable_boundary_verified`.

Exact source virtual names, concrete CThing/CWaypoint/CInfantryAI layout semantics, global block identity, runtime event-delivery/death-process/field-forward/output-copy behavior, BEA patching, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1081; cthing-waypoint-residual-vtable-boundary-wave1081; 0x004bfa00 SharedVFunc__CopyGlobal829dd0Block30ToOut_004bfa00; 0x004f3760 CThing__AddShutdownEvent_004f3760; 0x004f37a0 CThing__StartDieProcess_004f37a0; 0x004f3d20 SharedVFunc__ForwardField28Slot10OrNull_004f3d20; 0x0043e9c0 SharedVFunc__CopyGlobal0066ea10Block10ToOut_0043e9c0; 0x005df550; 0x005dd278; 0x005dbf14; 812/1408 = 57.67%; 1394/1560 = 89.36%; 500/500 = 100.00%; 6283/6283 = 100.00%; G:\GhidraBackups\BEA_20260602-103048_post_wave1081_cthing_waypoint_residual_vtable_boundary_verified; boundary recovery.

## 2026-06-02 Wave1080 Thing/Waypoint Vtable Boundary Recovery

Wave1080 (`thing-waypoint-vtable-boundary-wave1080`) recovered CThing-family true-vtable boundary rows that had previously appeared as raw table pointers. CThing vtable `0x005df550` now resolves `0x004040a0 SharedVFunc__CopyVector14ToOut_004040a0`, `0x004013f0 SharedVFunc__ReturnColorFF000080_004013f0`, `0x00405910 SharedVFunc__ReturnMinusOne_00405910`, `0x00401400 SharedVFunc__ForwardField28Slot18OrFallbackFloat_00401400`, `0x00405920 SharedVFunc__ReturnOneRet4_00405920`, `0x004f3460 CThing__GetClassNameString_004f3460`, and `0x004f3470 CThing__SetThingTypeMaskOr1_004f3470`; CInfantryAI vtable `0x005dbf14` also references shared helpers including `0x004040d0 SharedVFunc__CopyBlock34ToOut_004040d0`, `0x004014d0 SharedVFunc__ReturnField64Offset10OrMinusOne_004014d0`, `0x00401500 SharedVFunc__ReturnField64Offset14OrZero_00401500`, and `0x004014f0 SharedVFunc__ReturnField68_004014f0`. Queue closure is `6276/6276 = 100.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface advances to `1387/1560 = 88.91%`; top-500 remains `500/500 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260602-095224_post_wave1080_thing_waypoint_vtable_boundary_verified`.

Exact source virtual names, concrete CThing/CWaypoint/CInfantryAI layout semantics, type-mask bit labels, runtime object/class-name/type-mask/vector-copy behavior, BEA patching, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1080; thing-waypoint-vtable-boundary-wave1080; 0x004013f0 SharedVFunc__ReturnColorFF000080_004013f0; 0x00401400 SharedVFunc__ForwardField28Slot18OrFallbackFloat_00401400; 0x004040a0 SharedVFunc__CopyVector14ToOut_004040a0; 0x004bfb50 CWaypoint__GetClassNameString_004bfb50; 0x004f3460 CThing__GetClassNameString_004f3460; 0x0052db60 CWaypoint__GetTypeId12_0052db60; 0x005df550; 0x005dd278; 0x005dbf14; 812/1408 = 57.67%; 1387/1560 = 88.91%; 500/500 = 100.00%; 6276/6276 = 100.00%; G:\GhidraBackups\BEA_20260602-095224_post_wave1080_thing_waypoint_vtable_boundary_verified; boundary recovery.

## 2026-05-31 Wave1022 Object-Lifecycle Destructor Review

Wave1022 (`object-lifecycle-dtor-review-wave1022`) re-read the adjacent destructor strip that includes `0x004bff30 CComplexThing__dtor_base_Thunk_004bff30`. The thunk remains a jump to canonical `CComplexThing__dtor_base` at `0x004f3f00` and is reached by unwind cleanup and the shared complex-thing scalar-deleting wrapper path. Context exports also re-read `0x004f33e0 CThing__ctor_base`, `0x004f3480 CThing__scalar_deleting_dtor`, `0x004f3640 CThing__dtor_base`, `0x004f3e10 CComplexThing__ctor_base`, `0x004f3ee0 CComplexThing__scalar_deleting_dtor`, and `0x004f3f00 CComplexThing__dtor_base`. Verified backup: `G:\GhidraBackups\BEA_20260531-230345_post_wave1022_object_lifecycle_dtor_review_verified`.

Probe token anchor: Wave1022; object-lifecycle-dtor-review-wave1022; 0x004bff30 CComplexThing__dtor_base_Thunk_004bff30; CComplexThing__dtor_base; 6238/6238 = 100.00%; G:\GhidraBackups\BEA_20260531-230345_post_wave1022_object_lifecycle_dtor_review_verified.

Runtime complex-thing cleanup behavior, exact source-body identity, concrete object layouts, BEA patching, and rebuild parity remain separate proof.

## 2026-05-28 Wave958 CComplexThing SetVar Review

Wave958 (`ccomplexthing-setvar-review-wave958`) re-reviewed `0x004f45e0 CComplexThing__SetVar` read-only against fresh metadata/tags/xref/instruction/decompile/string exports and the source fallback at `references/Onslaught/thing.cpp:827-829`. no mutation was needed; the Wave517 correction away from older `CExplosionInitThing` / `CUnit` ownership still holds.

The saved base fallback remains `void __stdcall CComplexThing__SetVar(void * var_name, void * data)`. Instruction evidence loads `var_name` from `[ESP+4]`, calls the name object vtable slot `+0x38`, pushes `Warning: Uknown var`, calls `0x00441740 CConsole__Printf`, and returns at `0x004f45fc` with `RET 0x8`. Context includes `0x004804c0 CHiveBoss__SetVar`, which still falls back to this base warning path, plus `0x004f4230 CComplexThing__SetScript`, `0x004f44a0 CComplexThing__SetAnimMode`, `0x004f45a0 CComplexThing__FinishedPlayingCurrentAnimation`, and `0x0042a7b0 CConsole__SetVariableByName`.

Wave911 focused re-audit progress after Wave958 is `293/1408 = 20.81%`; static export-contract closure remains `6151/6151 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260528-114016_post_wave958_ccomplexthing_setvar_review_verified`. Runtime mission-script variable behavior, exact `CStringDataType` / `CDataType` layouts, exact virtual dispatch target identity, runtime console output behavior, BEA patching, and rebuild parity remain separate proof.

## 2026-05-25 Wave852 PC Platform/Resource Tail Read-Back

Wave852 PC platform/resource tail (`pc-platform-resource-tail-wave852`, `wave852-readback-verified`) adds saved static evidence for the render-resource instantiation connector called by `CThing__InitRenderThing`: `0x005164b0 CResourceDescriptorTable__InstantiateChain`. Probe token anchor: `Wave852 PC platform/resource tail`; `0x005164b0 CResourceDescriptorTable__InstantiateChain`; `CThing__InitRenderThing`; `PCRTID__CreateObject`; `5736/6098 = 94.06%`; `0x005168d0 CPCSoundManager__dtor`; `G:\GhidraBackups\BEA_20260525-093157_post_wave852_pc_platform_resource_tail_verified`.

The saved row scans the global 0x428-byte-stride descriptor table up to `DAT_00896488`, matches a descriptor pointer, skips disabled descriptors, walks descriptor chain entries backward, creates objects through `PCRTID__CreateObject`, stores `owner_tag` into the descriptor payload, calls the created object's init vfunc slot `+4`, and links created objects into a local chain. Exact descriptor payload schema, returned chain/list-head semantics, runtime render-object behavior, BEA patching, and rebuild parity remain deferred.

## 2026-05-28 Wave946 CAnimal / CThing Vtable Boundary Recovery

Wave946 (`animal-lifecycle-boundary-wave946`, `wave946-readback-verified`) recovered CAnimal vtable-boundary functions that are inherited from or source-parallel to CThing/CComplexThing. Representative anchors include `0x0044c140 CAnimal__HandleEvent3000Dispatch`, `0x00401440 CThing__GetRenderRadiusFromRenderThing`, `0x00401460 CThing__MakeVisible`, `0x00401470 CThing__MakeInvisible`, `0x00401490 CThing__Damage_NoOp`, `0x004014e0 CComplexThing__IsObjectiveFlagSet`, `0x004041d0 CAnimal__CopyMatrix9CToOut`, and `0x004f3d30 CThing__DrawDebugStuff3d`.

The real CAnimal table span through slot 68 now reads back without `NO_FUNCTION_AT_POINTER` rows. Queue closure after refresh is `6139/6139 = 100.00%`; Wave911 progress is `232/1408 = 16.48%`; verified backup `G:\GhidraBackups\BEA_20260528-062816_post_wave946_animal_lifecycle_boundary_review_verified`. Static evidence only: exact source virtual names, exact field/layout names, runtime animal/render/objective/physics/debug-render behavior, BEA patching, and rebuild parity remain deferred.

Wave1016 (`animal-init-dtor-review-wave1016`) re-read the CAnimal init/destructor head rows against this base lifecycle context with no mutation. The fresh context exports covered `0x004f3fd0 CComplexThing__Init`, `0x004f3f00 CComplexThing__dtor_base`, `0x004f41b0 CComplexThing__Shutdown`, `0x004f33e0 CThing__ctor_base`, `0x004f34a0 CThing__Init`, `0x004f3600 CThing__Shutdown`, `0x004f3640 CThing__dtor_base`, and the CAnimal vtable `0x005d8698`. Probe token anchor: Wave1016; animal-init-dtor-review-wave1016; 0x00403d30 CAnimal__Init; 0x00404010 CAnimal__dtor_base; 0x004041f0 CAnimal__scalar_deleting_dtor; 0x005d8698; 0x00622d48 bird.msh; 0x00622d1c Warning! Unknown animal type; 0x00622d70 CAnimal; 513/1408 = 36.43%; 739/1493 = 49.50%; 439/500 = 87.80%; 6238/6238 = 100.00%; G:\GhidraBackups\BEA_20260531-195306_post_wave1016_animal_init_dtor_review_verified; no mutation.

## Functions

| Address | Name | Status | Line | Notes |
|---------|------|--------|------|-------|
| 0x004f33e0 | CThing__ctor_base | RENAMED | 28 | Constructor body: vtables, map-who invalidation, flags, render/collision pointer init, thing counter |
| 0x004f3480 | CThing__scalar_deleting_dtor | RENAMED | n/a | Scalar deleting destructor wrapper for `CThing__dtor_base` |
| 0x004f34a0 | CThing__Init | RENAMED | 40 | Source-order init path: render init, position, ground/water, map-who/collision setup, world add |
| 0x004f35d0 | CThing__InitRenderThing | RENAMED | 92 | Creates render-thing from class id and stores pointer at this+0x30 |
| 0x005164b0 | CResourceDescriptorTable__InstantiateChain | DOCUMENTED | n/a | Wave852 render-resource descriptor instantiation connector called by `CThing__InitRenderThing` |
| 0x004f3600 | CThing__Shutdown | RENAMED | 102 | Removes from world/big-thing sets, shuts down monitor state, then scalar-deletes |
| 0x004f3640 | CThing__dtor_base | RENAMED | 116 | Deletes collision-seeking/render pointers, removes map-who entry, shuts down monitor state |
| 0x004f36d0 | CThing__Render | RENAMED | 133 | Invisibility/objective gating, render dispatch, optional debug cuboid draw |
| 0x004f3710 | CThing__RenderImposter | RENAMED | 150 | Calls render-thing imposter render path when renderable |
| 0x004f3730 | CThing__HandleEvent | RENAMED | 159 | Handles shutdown/start-die event codes |
| 0x004f37c0 | CThing__DrawDebugCuboid | RENAMED | 207 | Debug draw helper for bounding cuboids/sphere overlays |
| 0x0053d760 | CThing__RenderDebugVolumeOverlay | DOCUMENTED | n/a | Wave593 saved 16-stack-argument debug-volume overlay helper signature; exact source identity unproven |
| 0x0043e9f0 | CThing__GetRenderPos | DOCUMENTED | n/a | Wave946 recovered inherited vtable-boundary getter; copies four dwords from `this+0x1c` to caller output |
| 0x0043ea20 | CComplexThing__GetRenderOrientation | DOCUMENTED | n/a | Wave946 recovered inherited vtable-boundary getter; copies `0x30` bytes from `this+0x3c` to caller output |
| 0x00401420 | CThing__GetCueFactorFromRenderThing | DOCUMENTED | n/a | Wave946 recovered shared cue-factor getter through `this+0x30` render object with fallback constant |
| 0x00401440 | CThing__GetRenderRadiusFromRenderThing | DOCUMENTED | n/a | Wave946 recovered shared render-radius getter through `this+0x30` render object with fallback constant |
| 0x00401460 | CThing__MakeVisible | DOCUMENTED | n/a | Wave946 recovered shared visibility helper; clears flag bit `0x10` at `this+0x2c` |
| 0x00401470 | CThing__MakeInvisible | DOCUMENTED | n/a | Wave946 recovered shared visibility helper; sets flag bit `0x10` at `this+0x2c` |
| 0x00401490 | CThing__Damage_NoOp | DOCUMENTED | n/a | Wave946 recovered empty four-argument damage virtual (`RET 0x10`) |
| 0x004014b0 | CThing__GravityDefault | DOCUMENTED | n/a | Wave946 recovered shared constant-float gravity/default getter |
| 0x004014e0 | CComplexThing__IsObjectiveFlagSet | DOCUMENTED | n/a | Wave946 recovered objective flag predicate over `this+0x2c` bit `0x20` |
| 0x004f3d30 | CThing__DrawDebugStuff3d | DOCUMENTED | n/a | Wave946 recovered shared debug-render helper that calls `CThing__RenderDebugVolumeOverlay` |
| 0x004f3940 | CThing__GetBoundingRadius | RENAMED | 254 | Returns render bounding-box radius or falls back to virtual GetRadius |
| 0x004f3970 | CThing__SetObjective | RENAMED | 269 | Adds/removes this from objective noticeboard and toggles objective flag |
| 0x004f39b0 | CThing__UpdatePosition | RENAMED | 290 | Owner-corrected render-position update helper |
| 0x004f39c0 | CThing__InitCollisionSeekingThing | RENAMED | 300 | Owner/name-corrected collision-seeking init helper; allocates at this+0x38 when needed |
| 0x004f3a50 | CCSPersistentThing__scalar_deleting_dtor | RENAMED | n/a | Adjacent persistent collision helper scalar deleting destructor |
| 0x004f3a70 | CCSPersistentThing__dtor_base | RENAMED | n/a | Adjacent persistent collision helper destructor base |
| 0x004f3ac0 | CThing__GetCentrePos | RENAMED | 342 | Owner-corrected center/targeting position helper |
| 0x004f3c50 | CThing__StickToGround | RENAMED | 400 | Samples terrain/ground height into position Z and updates render position |
| 0x004f3cb0 | CThing__MoveTo | RENAMED | 423 | Copies position vector and updates render position |
| 0x004f3ce0 | CThing__Teleport | RENAMED | 430 | Copies position vector and dispatches MoveTo-style slot |
| 0x004f3d10 | CThing__GetPersistentCollisionSeekingThing | RENAMED | 441 | Owner-corrected GetCSPT-style helper |
| 0x004f3de0 | CThing__IsOverWater | RENAMED | 543 | Returns true when water level is above terrain collision height at current position |
| 0x004046d0 | CAnimation__ctor | RENAMED | n/a | Owner-corrected from CAtmospheric constructor; stores owner at +0x20 and schedules event 3000 |
| 0x00404790 | CAnimation__Process | RENAMED | n/a | Owner-corrected animation update helper; advances frame state and handles finished-animation callback/fallback mode |
| 0x00404860 | CAnimation__SetAnimMode | RENAMED | n/a | Owner-corrected animation mode setter; samples render-thing frame increment |
| 0x004048c0 | CAnimation__GetRenderFrame | RENAMED | n/a | Owner-corrected render-frame interpolation helper |
| 0x004f3c80 | CThing__GetRenderThingFrameIncrement | RENAMED | 414 | Owner-corrected render-thing frame increment helper |
| 0x004f3e10 | CComplexThing__ctor_base | RENAMED | 563 | Constructor body: base CThing construction, orientation identity matrix, and CComplexThing pointer clears |
| 0x004f3ee0 | CComplexThing__scalar_deleting_dtor | RENAMED | n/a | Scalar deleting destructor wrapper for `CComplexThing__dtor_base` |
| 0x004f3f00 | CComplexThing__dtor_base | RENAMED | 586 | Deletes mission script, animation, motion controller, then chains to CThing destructor-base |
| 0x004f3fd0 | CComplexThing__Init | RENAMED | 592 | Sets name/script, builds orientation, then delegates to CThing init |
| 0x004f4120 | CComplexThing__SetName | RENAMED | 625 | Owner-corrected name helper at this+0x78 |
| 0x004f41b0 | CComplexThing__Shutdown | RENAMED | 651 | Shutdown virtual: removes/frees name state and list participation |
| 0x004f4230 | CComplexThing__SetScript | RENAMED | 665 | Owner-corrected mission-script helper at this+0x74 |
| 0x004f43d0 | CComplexThing__AddShutdownEvent | RENAMED | 709 | Mission-script shutdown notification before base shutdown event |
| 0x004f4430 | CComplexThing__StartDieProcess | RENAMED | 728 | Base start-die path plus mission-script StartedDying callback |
| 0x004f4480 | CComplexThing__Hit | RENAMED | 748 | Mission-script hit callback when colliding with complex-thing target |
| 0x004f44a0 | CComplexThing__SetAnimMode | RENAMED | 767 | Owner-corrected animation mode helper; supersedes old CThing trail attribution |
| 0x004f45a0 | CComplexThing__FinishedPlayingCurrentAnimation | RENAMED | 780 | Mission-script finished-animation callback |
| 0x004f45e0 | CComplexThing__SetVar | RENAMED | 811 | Unknown script-variable warning fallback |
| 0x00403ba0 | CThing__Hit_TriggerDieOnUnitOrTypeMask02100000 | RENAMED | n/a | Hit helper variant: death gate keyed to other-thing type bits `0x10` or `0x02100000` |
| 0x00403bf0 | CThing__Hit_TriggerDieOnTypeMask00100000 | RENAMED | n/a | Hit helper variant: death gate keyed to other-thing type bit `0x00100000` |
| 0x00417540 | CThing__RenderAndUpdateStaticShadow | RENAMED | n/a | Wave 313 saved one-stack-argument render wrapper signature; calls `CThing__Render`, updates static-shadow visibility, and runs frame-gated callback |
| 0x004176c0 | CThing__InitRenderThingFromInitMeshName | RENAMED | n/a | Wave 313 saved one-stack-argument init signature; init-data-driven render object creation path using `%s.msh` naming and `this+0x30` bind |

## CThing Member Offsets

Based on function analysis:

| Offset | Type | Name | Notes |
|--------|------|------|-------|
| 0x30 | ptr | mRenderThing | Render object pointer; used by render, imposter, position-update, bounds, and collision downgrade checks |
| 0x38 | ptr | mCollisionSeekingThing | Collision-seeking helper pointer; `GetPersistentCollisionSeekingThing` dispatches its `+0x10` slot |
| 0x6c | ptr | CComplexThing::mAnimation | Animation object pointer |
| 0x70 | ptr | CComplexThing::mMotionController | Motion-controller pointer |
| 0x74 | ptr | CComplexThing::mMissionScript | Mission-script object pointer |
| 0x78 | char* | CComplexThing::mName | Object name string |

## Details

### Wave768 thing.cpp Unwind Continuation

Wave768 static read-back (`unwind-continuation-wave768`, `wave768-readback-verified`) saved `0x005d5220 Unwind@005d5220` and `0x005d5250 Unwind@005d5250` as `void __cdecl Unwind@...(void)` compiler-generated SEH allocation-cleanup rows tied to thing.cpp debug path `0x006331c0`. DATA scope-table xrefs `0x0061dafc` and `0x0061db24` point at the bodies; instruction/decompile evidence calls `OID__FreeObject_Callback` with line tokens `0x299` and `0x2ff` and allocation/type values `0x18` and `0x05`. Verified backup: `G:\GhidraBackups\BEA_20260523-171555_post_wave768_unwind_continuation_verified`. Static retail Ghidra evidence only; exact parent source-body identity, runtime object cleanup behavior, runtime exception behavior, BEA patching, and rebuild parity remain deferred.

### Wave761 Thing/ComplexThing Unwind Continuation

Wave761 static read-back (`unwind-continuation-wave761`, `wave761-readback-verified`) saved thing-hierarchy cleanup callbacks including `0x005d3f4b Unwind@005d3f4b` and `0x005d4000 Unwind@005d4000` as `void __cdecl Unwind@...(void)` compiler-generated SEH unwind rows. DATA scope-table xrefs include `0x0061cab4`, `0x0061cb14`, `0x0061cb3c`, `0x0061cb64`, and `0x0061cb94`; instruction/decompile evidence jumps to `CComplexThing__dtor_base` or `CThing__dtor_base` through `ECX` loaded from `*(EBP+0x4)` or `*(EBP-0x10)`. Verified backup: `G:\GhidraBackups\BEA_20260523-140318_post_wave761_unwind_continuation_verified`. This is saved static retail Ghidra evidence only; exact parent source-body identity, runtime object cleanup behavior, runtime exception behavior, BEA patching, and rebuild parity remain deferred.

### CThing Hit Signature Tranche (2026-05-09)

- `0x00403ba0` now has the saved signature `void __thiscall CThing__Hit_TriggerDieOnUnitOrTypeMask02100000(void * this, void * otherThing, void * collisionReport)`.
- `0x00403bf0` now has the saved signature `void __thiscall CThing__Hit_TriggerDieOnTypeMask00100000(void * this, void * otherThing, void * collisionReport)`.
- `0x004fcc30` now has the saved signature `void __thiscall CThing__CreateHitRefEvaluateImpulseAndDispatchHit(void * this, void * otherThing, void * collisionReport)`.
- `0x004e6640` now has the saved signature `void __thiscall CThing__CreateThingRefWithSquad(void * this, void * ownerThing, void * otherThing)`.
- The old `DamageMaskA/B` labels were corrected because current read-back evidence points at other-thing type-bit context, not a proven incoming damage-mask field.
- This is saved name/signature/comment refinement only; concrete `CThing`, referred-object, and `CCollisionReport` layouts, exact type-bit labels, tags, local names, structure types, runtime hit/death/script behavior, exact source identity, and rebuild parity remain open.

### Wave516 CThing Core Static Read-Back (2026-05-17)

Wave516 saved 22 source-order CThing/core-adjacent functions in the live Ghidra project. It corrected stale owner/name labels including `CUnit__DebugTraceIfFlag30Set` -> `CThing__UpdatePosition`, `CThing__AddCollision` -> `CThing__InitCollisionSeekingThing`, `CUnitAI__GetWorldPositionForTargeting` -> `CThing__GetCentrePos`, and `CCollisionSeekingRound__GetCollisionComponentOrNull` -> `CThing__GetPersistentCollisionSeekingThing`.

Read-back evidence:

- Apply script: `tools/ApplyCThingCoreWave516.java`
- Probe: `tools/ghidra_cthing_core_wave516_probe.py`
- Readiness note: `release/readiness/ghidra_cthing_core_wave516_2026-05-17.md`
- Post exports: `22` metadata rows, `22` tag rows, `416` xref rows, `4862` instruction rows, and `22` decompile exports.
- Queue after refresh: `6078` functions, `2433` commented, `3645` commentless, `1610` exact-undefined signatures, and `1403` `param_N` signatures.
- Backup: `G:\GhidraBackups\BEA_20260517-204846_post_wave516_cthing_core_verified`, `19` files, `158501767` bytes, no missing/extra/hash-diff files.

Claim boundary: static saved-Ghidra/source-order evidence only. Runtime object lifecycle behavior, render behavior, collision behavior, exact structure layouts, and rebuild parity remain open.

### Wave517 CComplexThing / CAnimation Static Read-Back (2026-05-17)

Wave517 saved 18 CComplexThing, CAnimation, and adjacent CThing animation helpers in the live Ghidra project. It supersedes the older Atmospherics/trail attribution for `0x004046d0`, `0x00404790`, `0x00404860`, `0x004048c0`, `0x004f3c80`, and `0x004f44a0`: the current evidence maps those functions to CAnimation / CComplexThing animation flow, not CAtmospheric trail setup.

Read-back evidence:

- Apply script: `tools/ApplyCComplexThingAnimationWave517.java`
- Probe: `tools/ghidra_ccomplexthing_animation_wave517_probe.py`
- Readiness note: `release/readiness/ghidra_ccomplexthing_animation_wave517_2026-05-17.md`
- Post exports: `18` metadata rows, `18` tag rows, `415` xref rows, `5202` instruction rows, and `18` decompile exports.
- Queue after refresh: `6078` functions, `2443` commented, `3635` commentless, `1608` exact-undefined signatures, and `1396` `param_N` signatures.
- Backup: `G:\GhidraBackups\BEA_20260517-212455_post_wave517_ccomplexthing_animation_verified`, `19` files, `158567303` bytes, no missing/extra/hash-diff files.

Claim boundary: static saved-Ghidra/source-parity evidence only. Runtime animation behavior, runtime mission-script behavior, exact CComplexThing/CAnimation layouts, exact source-body identity for optimized retail bodies, and rebuild parity remain open.

### Wave760 CComplexThing Unwind Continuation (2026-05-23)

Wave760 static read-back (`unwind-continuation-wave760`, `wave760-readback-verified`) saved four compiler-generated SEH unwind cleanup callbacks that jump to `CComplexThing__dtor_base`: `0x005d3e20 Unwind@005d3e20` (DATA xref `0x0061ca24`), `0x005d3e75 Unwind@005d3e75` (DATA xref `0x0061ca4c`), `0x005d3ee3 Unwind@005d3ee3` (DATA xref `0x0061ca7c`), and `0x005d3f22 Unwind@005d3f22` (DATA xref `0x0061ca9c`). Each row is saved as `void __cdecl Unwind@...(void)` and the instruction/decompile evidence loads `ECX` from `*(EBP+0x4)` before chaining into the destructor-base helper.

The same tranche also includes `0x005d3f2a Unwind@005d3f2a` active-reader cleanup and adjacent oids.cpp allocation cleanup. Verified backup: `G:\GhidraBackups\BEA_20260523-133538_post_wave760_unwind_continuation_verified`. This is saved static retail Ghidra evidence only; exact parent source-body identity, runtime complex-thing cleanup behavior, runtime exception behavior, BEA patching, and rebuild parity remain deferred.

### Wave593 Debug Volume Overlay Static Read-Back (2026-05-19)

Wave593 saved `0x0053d760` as:

```c
void __stdcall CThing__RenderDebugVolumeOverlay(
    uint color_argb,
    void * half_extents_vec3,
    void * center_vec3,
    float m00,
    float m01,
    float m02,
    float m03_unused,
    float m10,
    float m11,
    float m12,
    float m13_unused,
    float m20,
    float m21,
    float m22,
    float m23_unused,
    void * texture_or_material);
```

Read-back evidence:

- Apply script: `tools/ApplyDebugVolumeOverlayWave593.java`
- Probe: `tools/ghidra_debug_volume_overlay_wave593_probe.py`
- Readiness note: `release/readiness/ghidra_debug_volume_overlay_wave593_2026-05-19.md`
- Named xrefs: `CDebugMarkers__Render`, `CMapWho__DebugDrawSector`, `CMeshRenderer__RenderMesh`, and two `CThing__DrawDebugCuboid` calls.
- ABI evidence: `RET 0x40` plus caller setup for `color_argb`, `half_extents_vec3`, `center_vec3`, twelve copied transform dwords, and `texture_or_material`.
- Body evidence: render-state setup/restoration around transient `CVBufTexture` creation, six face-emission paths, `CVBufTexture__Render`, and resource release.
- Post exports: `1` metadata row, `1` tag row, `10` xref rows, `1701` instruction rows, `1` target decompile row, `4` caller decompile rows, `490` callsite instruction rows, and `446` proof instruction rows.
- Queue after refresh: `6093` functions, `3033` commented, `3060` commentless, `1347` exact-undefined signatures, `1100` `param_N` signatures, comment-backed proxy `3033/6093 = 49.78%`, strict clean-signature proxy `2987/6093 = 49.02%`, next head `0x0053f040 CVBufTexture__SetStateCacheModeByFlag`.
- Backup: `G:\GhidraBackups\BEA_20260519-140648_post_wave593_debug_volume_overlay_verified`, `19` files, `160992135` bytes, `DiffCount=0`.

Claim boundary: static saved-Ghidra evidence only. Runtime debug-render behavior, exact vector/matrix/vertex/CVBufTexture/texture/material layouts, exact source identity, BEA patching, and rebuild parity remain open.

### CThing__InitCollisionSeekingThing (0x004f39c0)

- **Purpose**: Initializes the CThing collision-seeking helper from an init collision descriptor
- **Source Line**: 310 (0x136)
- **Xref**: Found via debug path at 0x006331c0
- **Thiscall**: ECX = CThing pointer

**Behavior**:
1. Checks if `init_collision[2] != -1` (collision enabled/type check)
2. If `this+0x38` is null, allocates a 0x38-byte collision-seeking helper from pool `0x0b`
3. Initializes collision helper vtable and members
4. If `this+0x30` (render thing) is null and `init_collision[6] == 2` (mesh collision type):
   - Logs warning: "Warning: Trying to do mesh collision on a object that has no mesh"
   - Downgrades collision type from 2 to 1
5. Writes `this` into `init_collision+0x00`
6. Calls virtual method at collision helper vtable `+0x0c` to initialize/register collision context

**Warning String** at 0x0063317c:
```
Warning: Trying to do mesh collision on a object that has no mesh
```

**Allocation**: Uses OID__AllocObject (memory allocator) with type=0xB

---

### CComplexThing__SetName (0x004f4120)

- **Purpose**: Sets the name/identifier string for the object
- **Source Line**: 625 (0x271)
- **Xref**: Found via debug path at 0x006331c0
- **Thiscall**: ECX = CComplexThing pointer
- **Saved signature**: `void __thiscall CComplexThing__SetName(void * this, char * name)` as of Wave517

**Behavior**:
1. If this+0x78 (name ptr) is not null:
   - Calls CSPtrSet__Remove (unregister old name from global name set)
   - Frees old name via OID__FreeObject
   - Sets this+0x78 to null
2. If param_1 is non-empty string:
   - Calculates string length
   - Allocates memory for string (type=5)
   - Copies string via strncpy
   - Null-terminates
   - Calls CSPtrSet__AddToHead (register name in global name set)

**Allocation**: Uses OID__AllocObject with type=0x5

---

### CComplexThing__SetScript (0x004f4230)

- **Purpose**: Sets/replaces the CComplexThing mission script
- **Source Line**: 665 (0x299)
- **Xref**: Found via debug path at 0x006331c0
- **Thiscall**: ECX = CComplexThing pointer
- **Saved signature**: `void __thiscall CComplexThing__SetScript(void * this, char * script_name)` as of Wave517

**Behavior**:
1. If this+0x74 (mission script ptr) is not null:
   - Calls virtual destructor on existing mission-script object
   - Sets this+0x74 to null
2. If `script_name` is non-null and non-empty:
   - Looks up script object code via `CWorld__CloneScriptObjectCodeByName`
   - If found, allocates 0x3C bytes (60 bytes) for the script object (type=0x18)
   - Initializes the script object through the current `0x005333b0` helper name
   - Stores at this+0x74
   - Triggers INIT_SCRIPT event `0x7D1` (2001) with float -1.0f via `CEventManager__AddEvent_AtTime`

**Note**: 0xbf800000 = -1.0f in IEEE 754 floating point

**Allocation**: Uses OID__AllocObject with type=0x18

---

### CComplexThing__SetAnimMode (0x004f44a0)

- **Purpose**: Lazily creates CAnimation state and sets the current animation mode
- **Source Line**: 767 (0x2FF)
- **Xref**: Found via debug path at 0x006331c0
- **Thiscall**: ECX = CComplexThing pointer
- **Saved signature**: `bool __thiscall CComplexThing__SetAnimMode(void * this, int anim_mode, int reset_frame, int force_looped)` as of Wave517

**Behavior**:
1. If this+0x6c (animation ptr) is null:
   - Allocates 0x24 bytes (36 bytes) for a CAnimation object (type=5)
   - Creates animation state via `CAnimation__ctor`, passing the owning CComplexThing pointer
   - Stores at this+0x6c
2. Calls `CAnimation__SetAnimMode` with `anim_mode`, `reset_frame`, and `force_looped`

**Parameters**: The retail signature is named from `ret 0xc`, source parity, and `CAnimation__SetAnimMode` call-shape evidence. Exact animation enum values remain provisional.

**Allocation**: Uses OID__AllocObject with type=0x5

---

## Related Functions

These functions were found but not renamed (exception handlers):

| Address | Name | Notes |
|---------|------|-------|
| 0x005d5220 | Unwind@005d5220 | Exception handler for thing.cpp |
| 0x005d5250 | Unwind@005d5250 | Exception handler for thing.cpp |

## Memory Allocation Types

The allocator OID__AllocObject uses type codes:

| Type | Size | Used By |
|------|------|---------|
| 0x05 | varies | Name strings, CAnimation objects |
| 0x0B | 0x38 | Collision objects |
| 0x18 | 0x3C | Mission-script objects |

## Cross-References

- OID__AllocObject - Memory allocator (appears in all functions)
- OID__FreeObject - Memory deallocator (in SetName)
- CConsole__Printf (`FUN_00441740`) - Debug/warning logger (in InitCollisionSeekingThing)
- `CWorld__CloneScriptObjectCodeByName` (`0x0050abc0`) - Script-object-code lookup by name + clone (used by SetScript)
- `0x005333b0` current helper name - Mission-script object constructor path used by SetScript
- `CEventManager__AddEvent_AtTime` - Event trigger system (in SetScript and CAnimation constructor)
- `CAnimation__ctor` - Animation object constructor (in SetAnimMode)
- `CAnimation__SetAnimMode` - Animation mode setter (in CComplexThing__SetAnimMode)
- CSPtrSet__AddToHead - Name registration (in SetName)
- CSPtrSet__Remove - Name unregistration (in SetName)
