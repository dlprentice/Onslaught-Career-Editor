# ThunderHead.cpp Functions

> Source File: ThunderHead.cpp | Binary: BEA.exe
> Debug Path: 0x00633240

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

CThunderHead is a large bipedal enemy mech unit. Current saved Ghidra evidence covers three CThunderHead factory/vtable helpers plus two CThunderheadGuide helpers. Wave519 (2026-05-18) hardened the signatures/comments/tags for the three factory helpers, corrected `CThunderheadGuide__Init`, and recovered the guide vtable slot-3 boundary at `0x004f4e40`.

This page is static retail-binary evidence only. `ThunderHead.cpp` is not present in the current `references/Onslaught/` snapshot, so exact source-body identity, concrete object layouts, runtime targeting/combat behavior, BEA patching, and rebuild parity remain unproven.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004f4730 | [CThunderHead__CreateLegMotion](./CThunderHead__CreateLegMotion.md) | Creates CMCMech-family leg-motion controller when `"LegMotion"` is present | ~256 bytes |
| 0x004f4830 | [CThunderHead__CreateWarspite](./CThunderHead__CreateWarspite.md) | Allocates and initializes Warspite-style component | ~112 bytes |
| 0x004f48a0 | [CThunderHead__CreateGuide](./CThunderHead__CreateGuide.md) | Allocates CThunderheadGuide and stores it at `this+0x208` | ~96 bytes |
| 0x004f4e00 | [CThunderheadGuide__Init](./CThunderheadGuide__Init.md) | Initializes guide base, vtable, and copied owner state | ~64 bytes |
| 0x004f4e40 | [CThunderheadGuide__VFunc_03_004f4e40](./CThunderheadGuide__VFunc_03_004f4e40.md) | Recovered guide vtable slot-3 boundary; current exact semantic name unknown | ~884 bytes |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d5280 | Unwind@005d5280 | 0x20 (32) | Cleanup for leg motion (0xf0/240 byte allocation) |
| 0x005d52a0 | Unwind@005d52a0 | 0x2b (43) | Cleanup for Warspite (0x60/96 byte allocation) |
| 0x005d52c0 | Unwind@005d52c0 | 0x31 (49) | Cleanup for guide (0x30/48 byte allocation) |

## Key Observations

- CThunderHead vtable `0x005e11b0` slots 1, 2, and 3 point to the three factory helpers at `0x004f4730`, `0x004f4830`, and `0x004f48a0`.
- `CThunderHead__CreateLegMotion` looks up `"LegMotion"`, allocates `0xf0` bytes from pool `0x1b`, constructs a CMCMech-family controller, stores it at `this+0x70`, and seeds parameters from `init_context+0x3bc`.
- `CThunderHead__CreateWarspite` allocates `0x60` bytes from pool `0x16`, calls `CWarspite__Init`, and stores the returned pointer or NULL at `this+0x13c`.
- `CThunderHead__CreateGuide` allocates `0x30` bytes from pool `0x17`, calls `CThunderheadGuide__Init`, and stores the returned pointer or NULL at `this+0x208`.
- CThunderheadGuide vtable `0x005df8d4` slot 3 points to the recovered function boundary at `0x004f4e40`; the body returns at `0x004f51b4`, before a following non-function data-initializer block at `0x004f51c0`.

## CThunderHead Object Layout (Partial)

| Offset | Field | Notes |
|--------|-------|-------|
| 0x00 | vtable | Virtual function table |
| 0x08 | (inherited) | CUnit base class fields |
| 0x30 | mSomeController | Pointer to controller with method at +0x24 |
| 0x70 | mLegMotion | Pointer to leg motion system (240 bytes) |
| 0x13c | mWarspite | Pointer to CWarspite AI controller (96 bytes) |
| 0x208 | mGuide | Pointer to guidance system (48 bytes) |

## Wave768 ThunderHead.cpp Unwind Continuation

Wave768 static read-back (`unwind-continuation-wave768`, `wave768-readback-verified`) hardened the adjacent ThunderHead.cpp unwind cleanup callbacks as `void __cdecl Unwind@...(void)`. Exact anchors include `0x005d5280 Unwind@005d5280`, `0x005d52e0 Unwind@005d52e0`, and `0x005d5300 Unwind@005d5300`. Evidence includes DATA scope-table xrefs `0x0061db4c` through `0x0061dbec`, ThunderHead.cpp debug path `0x00633240`, three `OID__FreeObject_Callback` rows, `CDXLandscape__DestroyResourceDescriptorArray_Thunk`, and `CThing__dtor_base`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-171555_post_wave768_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Wave519 Evidence

- Mutation script: `tools/ApplyThunderHeadWave519.java`.
- Focused probe: `tools/ghidra_thunderhead_wave519_probe.py`.
- Read-back artifacts: `subagents/ghidra-static-reaudit/wave519-thunderhead-004f4730/`.
- Post read-back verified `5` metadata rows, `5` tag rows, `5` xref rows, `1425` instruction rows, `345` focused boundary rows, `5` decompile exports, and `256` vtable-slot rows.
- Queue after Wave519: `6079` functions, `2457` commented, `3622` commentless, `1598` exact-undefined signatures, and `1394` `param_N` signatures.

## Related Classes

- **CMCThunderHead** (`.?AVCMCThunderHead@@` at 0x00633228) - Mission Control variant
- **CThunderHeadBehaviourType** (0x00627d88) - AI behavior type definition
- **CThunderheadGuide** (0x00633288) - Guidance system class

## Related Strings

- `"LegMotion"` (0x00623074) - Animation asset name
- `"Thunderhead Main Gun"` (0x006247e0) - Weapon name
- `"Thunderhead Flamethrower"` (0x00633264) - Secondary weapon
- `"m_thunderhead.msh"` (0x0062d304) - Mesh file name
- `"CThunderHead"` (0x0063d868) - Class name string

## Related Files

- Mech.cpp - Player mech uses similar leg motion system
- Warspite.cpp - CWarspite AI controller implementation
- Unit.cpp - Base class for all units
- BattleEngine.cpp - Combat system integration

---
*Discovered via ThunderHead.cpp xref analysis (Dec 2025)*
