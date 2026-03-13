# MCBuggy.cpp Functions

> Source File: MCBuggy.cpp | Binary: BEA.exe
> Debug Path Address: 0x0062dc80 (`C:\dev\ONSLAUGHT2\MCBuggy.cpp`)
> RTTI: `.?AVCMCBuggy@@` at 0x0062dc70

## Overview

Motion Controller for buggy/wheeled vehicles. CMCBuggy inherits from a base motion controller class and implements wheel physics, animation, and ground contact handling for buggy-type vehicles in Battle Engine Aquila.

The class manages:
- Wheel base positioning and transforms
- Wheel motion/rotation animation
- Ground contact detection
- Wheel rumble/shake effects on impact
- Per-wheel state tracking (position, rotation, contact)

## Functions

| Address | Name | Size | Purpose |
|---------|------|------|---------|
| 0x00493020 | CMCBuggy__CMCBuggy | ~96 bytes | Constructor - initializes vtable and member variables |
| 0x00493080 | CMCBuggy__scalar_deleting_destructor | ~32 bytes | Scalar deleting destructor wrapper |
| 0x004930a0 | CMCBuggy__destructor | ~224 bytes | Destructor - frees allocated wheel buffers |
| 0x00493180 | CMCBuggy__SetC0 | ~16 bytes | Setter for member at offset 0xC0 |
| 0x00493190 | CMCBuggy__Init | ~864 bytes | Initialize wheel arrays, allocate memory for wheel data |
| 0x004934f0 | CMCBuggy__UpdateWheel | ~3616 bytes | Main update - wheel transforms, animation, physics |
| 0x00494310 | CMCBuggy__ProfileEnd | ~64 bytes | Performance profiling end (rdtsc timing) |
| 0x00494350 | CMCBuggy__InvertMatrix | ~352 bytes | 3x3 matrix inversion for wheel transforms |
| 0x004944b0 | CMCBuggy__DivideVector | ~32 bytes | Divide 3D vector by scalar |
| 0x00494ca0 | CMCBuggy__WheelScalarDelDtor | ~32 bytes | Wheel struct scalar deleting destructor |
| 0x00494cc0 | CMCBuggy__WheelDestructor | ~32 bytes | Wheel struct destructor |
| 0x00494ce0 | CMCBuggy__ApplyWheelRumble | ~352 bytes | Apply shake/rumble effect to wheel matrix |

**Total: 12 functions identified**

## Vtable Layout (0x005dc250)

| Offset | Address | Function |
|--------|---------|----------|
| +0x00 | 0x004014C0 | (inherited) |
| +0x04 | 0x00493080 | CMCBuggy__scalar_deleting_destructor |
| +0x08 | 0x004BACB0 | (inherited - base class) |
| +0x0C | 0x004BAE60 | (inherited - base class) |
| +0x10 | 0x004944D0 | (virtual - not analyzed) |
| +0x14 | 0x00494940 | (virtual - not analyzed) |
| +0x18 | 0x00452DA0 | (inherited) |
| +0x1C | 0x004D6B20 | (inherited) |
| +0x20 | 0x00494AE0 | (virtual - not analyzed) |
| +0x24 | 0x005019C0 | (inherited) |

## Key Technical Findings

### Wheel System Architecture
- Wheels tracked via "WheelBase" string lookups (0x0062dca0)
- Wheel animation via "WheelMotion" string (0x0062cb54)
- Each wheel has: position (16 bytes), transform matrix (48 bytes), rotation state (4 bytes)
- Wheels allocated dynamically based on vehicle type

### Member Variable Offsets (CMCBuggy this pointer)
| Offset | Type | Purpose |
|--------|------|---------|
| +0x00 | vtable* | Virtual function table pointer |
| +0x08 | void* | Associated object pointer |
| +0x0C | void* | Wheel base positions array |
| +0x10 | float* | Wheel rotation angles array |
| +0x18 | int | Number of wheels |
| +0x1C | int | Wheel motion frame count |
| +0x20 | int | First wheel motion frame index |
| +0x24 | void* | Wheel transform matrices (current) |
| +0x28 | void* | Wheel positions array |
| +0x2C | float* | Wheel contact times array |
| +0x30 | void* | Wheel transform matrices (previous) |
| +0x34 | void* | Previous wheel positions |
| +0x38 | float* | Previous wheel contact times |
| +0x40-0x6C | float[12] | Current frame transform matrix |
| +0x70-0x7C | float[4] | Position vector |
| +0x80-0xAC | float[12] | Orientation matrix |
| +0xB0-0xBC | float[4] | Smoothed direction vector |
| +0xC0 | int | Unknown flag (set by SetC0) |
| +0xC4 | void* | Wheel motion cache data |

### Physics Constants
- `0xbf800000` = -1.0f (used for uninitialized contact times)
- `0.01` / `0.99` - smoothing factors for direction vector
- `0.071428575` (1/14) - wheel rumble rotation rate X
- `0.04` (1/25) - wheel rumble rotation rate Y
- Max rumble value clamped to 2.0

### Performance Profiling
- Uses `rdtsc` instruction for cycle counting
- Profiling data stored at globals:
  - DAT_0083c7e4: Accumulated cycle count
  - DAT_0083c9b4: Call count

### Related Strings
- `"WheelBase"` at 0x0062dca0 - wheel attachment point marker
- `"WheelMotion"` at 0x0062cb54 - wheel animation data reference

## Call Graph

```
CMCBuggy__CMCBuggy
    -> FUN_004bae30 (base class constructor)

CMCBuggy__destructor
    -> OID__FreeObject (memory free - called for each buffer)
    -> FUN_004bae50 (base class destructor)

CMCBuggy__Init
    -> FUN_004aa820 (find "WheelBase" markers)
    -> OID__AllocObject (memory allocation)
    -> FUN_004aa630 (find "WheelMotion" animation)
    -> FUN_004aa680 (get animation info)
    -> FUN_004b0fb0 (sample animation frame)
    -> FUN_004011b0 (initialize data)

CMCBuggy__UpdateWheel
    -> CMCBuggy__Init (lazy initialization)
    -> FUN_0047ec60 (physics calculation)
    -> FUN_004404f0 (matrix operation)
    -> FUN_00411a60 (vector operation)
    -> FUN_00406d50 (normalize)
    -> FUN_0056e170 (state check)
    -> FUN_004aa820 (find wheel base)
    -> FUN_004b0fb0 (sample animation)
    -> CMCBuggy__InvertMatrix
    -> CMCBuggy__UpdateWheel (recursive for child wheels)

CMCBuggy__InvertMatrix
    -> CMCBuggy__DivideVector (x2)

CMCBuggy__ApplyWheelRumble
    -> FUN_00445010 (get rumble value)
    -> fcos/fsin (rotation calculations)
    -> FUN_00401ec0 (vector construction)
    -> FUN_00401f10 (matrix from vectors)
```

## Additional Utility Promotions (Headless 2026-02-26)

| Address | Name | Purpose |
|---------|------|---------|
| 0x004956a0 | Mat34__Add | 3x4 matrix add helper (`dst = lhs + rhs`) used across mech/mesh update paths. |
| 0x00495e00 | Mat34__Subtract | 3x4 matrix subtract helper (`dst = lhs - rhs`) used across mech/mesh update paths. |

Notes:
- These two helpers were previously weak `CMCBuggy__Unk_*` symbols and were promoted by behavior-level decompile evidence plus multi-caller xref usage outside buggy-only paths.

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
*12 functions mapped from MCBuggy.cpp debug path references*
