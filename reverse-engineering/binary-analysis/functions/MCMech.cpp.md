# MCMech.cpp Functions

> Source File: MCMech.cpp | Binary: BEA.exe
> Debug Path: `C:\dev\ONSLAUGHT2\MCMech.cpp` at 0x0062df60

## Overview

Motion Controller for Mech/Walker units. Handles leg animation, foot placement, and inverse kinematics for multi-legged walking machines. The class manages procedural leg animation with terrain adaptation, including cylinder-based hydraulic leg components and toe/foot positioning.

## Functions

| Address | Name | Size | Purpose |
|---------|------|------|---------|
| 0x004983b0 | CMCMech__Constructor | ~352 bytes | Initialize CMCMech object, set default parameters |
| 0x00498510 | CMCMech__ScalarDeletingDestructor | ~32 bytes | MSVC scalar deleting destructor wrapper |
| 0x00498530 | CMCMech__Destructor | ~560 bytes | Clean up allocated arrays and unlink from global list |
| 0x00498080 | CMCMech__HasAllCylinders | ~496 bytes | Check if model has all 24 hydraulic cylinder bones (N/E/W/S x top/mid/bot x in/out) |
| 0x00498270 | CMCMech__HasCylinderBones | ~320 bytes | Check if any leg has Nmidoutcyl bone |
| 0x004988b0 | CMCMech__Reset | ~736 bytes | Reset mech state with identity matrices |
| 0x00498bf0 | CMCMech__SetParams | ~80 bytes | Set motion parameters (offsets 0x98-0xc4) |
| 0x00498c40 | CMCMech__Init | ~3008 bytes | Main initialization - allocate arrays, find leg bones, compute motion data |
| 0x00499bc0 | CMCMech__GetFootHeight | ~320 bytes | Calculate foot height for terrain following |
| 0x00499d60 | CMCMech__TranslatePositions | ~208 bytes | Apply translation offset to all foot positions |
| 0x00499e30 | CMCMech__UpdateBone | ~7200 bytes | Main update - compute bone transforms for leg animation |

**Total: 11 functions (~12,312 bytes)**

## Class Structure (CMCMech)

Based on decompiled code analysis:

| Offset | Type | Name | Purpose |
|--------|------|------|---------|
| 0x00 | vtable* | vtable | Virtual function table (PTR_LAB_005dc3b4) |
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

### Hydraulic Cylinders
- 24 cylinder bones per mech model (N/E/W/S orientations)
- Three vertical positions: top, mid, bot
- Inner and outer cylinders for telescoping effect
- HasAllCylinders validates complete leg hydraulics

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
- `FUN_004aa820` - Find bone by name with index
- `FUN_004aa630` - Get animation channel by name
- `FUN_004aa680` - Get animation data
- `FUN_004b0fb0` - Sample animation at frame
- `FUN_0047eb80` - Get terrain height
- `FUN_0047ec60` - Get terrain normal

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
