# MCMech.cpp Functions

> Source File: MCMech.cpp | Binary: BEA.exe
> Debug Path: `[maintainer-local-source-export-root]\MCMech.cpp` at 0x0062df60

## Overview

Motion Controller for Mech/Walker units. Handles leg animation, foot placement, and inverse kinematics for multi-legged walking machines. The class manages procedural leg animation with terrain adaptation, including cylinder-based hydraulic leg components and toe/foot positioning.

Wave433 is saved static Ghidra evidence, not runtime proof. It corrected two stale `CMCMech` labels to `CMeshPart` predicates, recovered three `CMCMech` vtable-slot boundaries, and hardened nearby lifecycle/init/reset/set/get/translate and matrix-helper signatures. Wave437 hardened the large `CMCMech__UpdateBone` signature/comment at `0x00499e30`; `CMCMech__UpdateBoneHierarchyRecursive` at `0x0049bd50` remains deferred.

## Wave755 MCMech Unwind Continuation (2026-05-23)

Wave755 static read-back (`unwind-continuation-wave755`, `wave755-readback-verified`) saved comments/tags/signatures for six MCMech.cpp-adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d32a0 Unwind@005d32a0` through `0x005d3340 Unwind@005d3340`. Evidence includes MCMech.cpp debug path `0x0062df60`, DATA scope-table xrefs `0x0061bfec` through `0x0061c074`, three `OID__FreeObject_Callback` allocation-cleanup rows, one `CLine__SetBaseVtable_00426360` local line-helper cleanup, one `CMCBuggy__ProfileEnd` profiler epilogue, and one `CMotionController__dtor_base` row. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-105815_post_wave755_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

| Address | Scope-table xref | Static read-back evidence |
| --- | --- | --- |
| `0x005d32a0` | `0x0061bfec` | `OID__FreeObject_Callback(*(EBP-0x160))`, MCMech.cpp line token `0x1b`, allocation/type value `0x131`. |
| `0x005d32bc` | `0x0061bff4` | `OID__FreeObject_Callback(*(EBP-0x160))`, allocation/type value `0x135`. |
| `0x005d32d8` | `0x0061bffc` | `OID__FreeObject_Callback(*(EBP-0x160))`, allocation/type value `0x17d`. |
| `0x005d3300` | `0x0061c024` | `CLine__SetBaseVtable_00426360(EBP-0x40)`. |
| `0x005d3320` | `0x0061c04c` | `CMCBuggy__ProfileEnd(EBP-0x1b4)`. |
| `0x005d3340` | `0x0061c074` | `CMotionController__dtor_base(*(EBP-0x10))`. |

## Functions

| Address | Name | Size | Purpose |
|---------|------|------|---------|
| 0x00498080 | CMeshPart__NameIsNotAnyMechCylinderBone | ~496 bytes | Mesh-part token predicate for the 24 observed hydraulic cylinder bone names |
| 0x00498270 | CMeshPart__AnyChildNameIsNmidoutcyl | ~320 bytes | Mesh-part child scan for `Nmidoutcyl` |
| 0x004983b0 | CMCMech__Constructor | ~352 bytes | Initialize CMCMech object, set default parameters |
| 0x00498510 | CMCMech__ScalarDeletingDestructor | ~32 bytes | MSVC scalar deleting destructor wrapper |
| 0x00498530 | CMCMech__Destructor | ~560 bytes | Clean up allocated arrays and unlink from global list |
| 0x00498870 | CMCMech__VFunc_00_OnTimedResetEvent_00498870 | created slot | Vtable slot-0 timed reset/event requeue boundary |
| 0x004988b0 | CMCMech__Reset | ~736 bytes | Reset mech state with identity matrices |
| 0x00498bf0 | CMCMech__SetParams | ~80 bytes | Set motion parameters (offsets 0x98-0xc4) |
| 0x00498c40 | CMCMech__Init | ~3008 bytes | Main initialization - allocate arrays, find leg bones, compute motion data |
| 0x00499bc0 | CMCMech__GetFootHeight | ~320 bytes | Calculate foot height for terrain following |
| 0x00499d60 | CMCMech__TranslatePositions | ~208 bytes | Apply translation offset to all foot positions |
| 0x00499e30 | CMCMech__UpdateBone | ~7200 bytes | Large bone-update body; Wave437 signature/comment hardening only, with exact parameter roles and runtime animation behavior still unproven |
| 0x0049bbb0 | MathMatrix3x3__DivideByScalarInPlace | helper | Matrix helper signature corrected by Wave433 |
| 0x0049bc10 | MathMatrix3x3__TransposeInPlace | helper | Matrix helper signature corrected by Wave433 |
| 0x0049bc40 | MathMatrix3x3__Determinant | helper | Matrix helper signature corrected by Wave433 |
| 0x0049bc80 | MathMatrix3x3__BuildCofactorMatrix | helper | Matrix helper signature corrected by Wave433 |
| 0x0049bd50 | CMCMech__UpdateBoneHierarchyRecursive | large body | Recursive hierarchy update body; deferred by Wave433 |
| 0x0049be00 | CMCMech__VFunc_04_UpdateInterpolatedBoneTransform_0049be00 | created slot | Vtable slot-4 interpolated/cached bone-transform update boundary |
| 0x0049c1d0 | CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0 | slot helper | Writes interpolated/cached float for mesh part output |
| 0x0049c240 | CMCMech__VFunc_08_GetUpdateStateFlag_0049c240 | created slot | Compact getter returning field `+0xc8` |
| 0x0049c250 | CMeshPart__NameAvoidsMechOptimizationTokens | helper | Mesh-part token filter corrected by Wave433 |

**Current tracked surface: 21 addresses, with 20 saved/hardened targets and 1 large recursive `CMCMech` body deferred.**

## Class Structure (CMCMech)

Based on decompiled code analysis:

| Offset | Type | Name | Purpose |
|--------|------|------|---------|
| 0x00 | vtable* | vtable | Virtual function table at `0x005dc3b4`; Ghidra may label the pointer as `PTR_CMCMech__VFunc_00_OnTimedResetEvent_00498870_005dc3b4` after Wave433 |
| 0x08 | ptr | pModel | Pointer to model/mesh data |
| 0x0C | float | param4 | Motion parameter (set by SetParams) |
| 0x10 | float | param5 | Motion parameter (set by SetParams) |
| 0x14 | ptr | pFootbasePos | Array of foot base positions (vec4 x numLegs) |
| 0x18 | ptr | pArray18 | Per-leg float array |
| 0x1C | ptr | pArray1C | Per-leg float array |
| 0x20 | ptr | pArray20 | Per-leg float array |
| 0x24 | ptr | pFootTargetPos | Array of foot target positions (vec4 x numLegs) |
| 0x2C | float | mBlendWeight | Animation blend weight (0x2C, default 0.0) |
| 0x30 | ptr | pBoneMatrices | Bone transformation matrices (mat4x3 array) |
| 0x34 | ptr | pArray34 | Position array (vec4 x numBones) |
| 0x38 | ptr | pArray38 | Per-bone float array (initialized to -1.0) |
| 0x3C | ptr | pBoneMatrices2 | Secondary bone matrices |
| 0x40 | ptr | pArray40 | Position array (initialized to 0,0,0) |
| 0x44 | ptr | pArray44 | Per-bone float array (initialized to -1.0) |
| 0x4C | float | mLastTime | Last update time |
| 0x50 | int | mFlag50 | State flag |
| 0x54 | int | mFlag54 | Copy of mFlag50 |
| 0x88-0xA4 | floats | mBaseTransform | Base position/orientation |
| 0x98-0xA4 | floats | mParamBlock | Parameters set by SetParams |
| 0xA8 | int | mNumLegs | Number of legs (counted from "Footbase" bones) |
| 0xAC | int | mNumLegFrames | Number of animation frames for legs |
| 0xB0 | int | mLegMotionStart | Start frame of LegMotion animation |
| 0xB4 | int | mToeMotionStart | Start frame of ToeMotion animation |
| 0xB8 | int | mToeMotionEnd | End frame of ToeMotion animation |
| 0xBC | ptr | pToeStopData | Toe stop animation data |
| 0xC0 | int | mNumToeStops | Number of toe stops per leg |
| 0xC4 | float | param7 | Motion parameter (set by SetParams) |
| 0xC8 | int | mUpdateFlag | Update state flag |
| 0xCC | int | mCounter | Update counter |
| 0xE4 | ptr | pSharedData | Shared data between instances with same model |
| 0xE8 | ptr | pParent | Parent model/entity pointer |
| 0xEC | ptr | pNext | Next CMCMech in global linked list |

## Key String References

Animation/bone markers found in the code:
- `"Footbase"` - Foot base bone prefix (counted to determine leg count)
- `"toestop"` / `"Toestop"` - Toe constraint bones
- `"ToeMotion"` - Toe animation channel
- `"LegMotion"` - Leg animation channel

Hydraulic cylinder bones (24 total, checked by HasAllCylinders):
- `"Nmidoutcyl"`, `"Emidoutcyl"`, `"Wmidoutcyl"`, `"Smidoutcyl"` - Mid outer cylinders
- `"Nmidincyl"`, `"Emidincyl"`, `"Wmidincyl"`, `"Smidincyl"` - Mid inner cylinders
- `"Ntopoutcyl"`, `"Etopoutcyl"`, `"Wtopoutcyl"`, `"Stopoutcyl"` - Top outer cylinders
- `"Ntopincyl"`, `"Etopincyl"`, `"Wtopincyl"`, `"Stopincyl"` - Top inner cylinders
- `"Nbotoutcyl"`, `"Ebotoutcyl"`, `"Wbotoutcyl"`, `"Sbotoutcyl"` - Bottom outer cylinders
- `"Nbotincyl"`, `"Ebotincyl"`, `"Wbotincyl"`, `"Sbotincyl"` - Bottom inner cylinders

## Key Observations

### Leg Animation System
- Legs are procedurally animated based on "Footbase" bones in the model
- Toe stops provide IK constraints for foot placement
- LegMotion and ToeMotion animations define the walking cycle
- System supports arbitrary number of legs (counted at runtime)

### Hydraulic Cylinder Mesh Tokens
- 24 cylinder bones per mech model (N/E/W/S orientations)
- Three vertical positions: top, mid, bot
- Inner and outer cylinders for telescoping effect
- Wave433 corrects the nearby helpers to `CMeshPart__NameIsNotAnyMechCylinderBone` and `CMeshPart__AnyChildNameIsNmidoutcyl`; they are mesh-part token predicates, not CMCMech-owned model validators

### Shared Data Optimization
- Multiple CMCMech instances sharing the same parent model share data via pSharedData
- Init() searches global list (DAT_00704650) for existing instances with same parent
- Reduces memory allocation for duplicate mechs

### Global Linked List
- All CMCMech instances linked via pNext pointer (offset 0xEC)
- Head stored in DAT_00704650
- Used for cleanup and data sharing

### Physics Constants
- Foot height calculation uses ray casting with +10.0/-2.0 vertical offsets
- Sine wave modulation (3.14 * 0.0055555557 = ~1/180 for degree conversion)
- Foot position clamping to +/-5.0 range

### Memory Allocation
- Uses OID__AllocObject for allocation (category 0x1b = motion controller)
- Multiple arrays allocated per leg and per bone
- Matrices stored as 12 floats (3x4 row-major)

## Related Functions

Called helper functions:
- `CMCMech__FindSlotValueByNameAndOwner` - named slot/value lookup used by mech setup paths
- `CMeshPart__NameIsNotAnyMechCylinderBone` - hydraulic-cylinder token predicate
- `CMeshPart__AnyChildNameIsNmidoutcyl` - child token scan
- `MathMatrix3x3__DivideByScalarInPlace`, `MathMatrix3x3__TransposeInPlace`, `MathMatrix3x3__Determinant`, and `MathMatrix3x3__BuildCofactorMatrix` - nearby matrix helpers corrected in Wave433
- Terrain/shadow sampling helpers remain static evidence only until runtime foot-placement proof is added

---
*Updated by Wave433 static Ghidra read-back (2026-05-15) and Wave437 `CMCMech__UpdateBone` hardening (2026-05-16).*
