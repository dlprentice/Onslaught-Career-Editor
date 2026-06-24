# WarspiteDome.cpp Functions

> Source File: WarspiteDome.cpp | Binary: BEA.exe
> Debug Path: 0x0063d170

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Dome component for the Warspite battleship boss. CWarspiteDome is a destructible component attached to the main CWarspite battleship, representing one of its protective dome structures. It initializes through the CGroundUnit path and allocates nested Warspite-style controller and motion-controller helpers. The exact concrete layout remains partial.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x005047e0 | CWarspiteDome__Init | Wave536 `RET 0x4` init helper: seeds init-context flags, calls `CGroundUnit__Init`, allocates nested controller helpers, and stores a CMCWarspiteDome pointer at `this+0x70` | read-back documented |
| 0x00504990 | CWarspiteDome__ScalarDeletingDestructor | Wave536 scalar-deleting destructor wrapper for the `0x005dfc14` table; wraps `CWarspiteDome__Destructor` and conditionally frees | read-back documented |
| 0x005049b0 | CWarspiteDome__Destructor | Wave536 register-only destructor: restores base vtable, unregisters tracked pointer cells, then calls `CMonitor__Shutdown` | read-back documented |

## Related Motion Controller Functions

Wave435 recovered the adjacent `CMCWarspiteDome` motion-controller table near the tentacle controller cluster. These are distinct from the `CWarspiteDome` unit/object lifecycle functions above.

Wave1021 (`motion-controller-constructor-review-wave1021`) re-read `0x0049ef80 CMCWarspiteDome__Constructor` with no mutation. Fresh xrefs still show `CWarspiteDome__Init` callers at `0x00504918` and `0x00504924`; instruction evidence calls `CMotionController__ctor_base`, installs vtable `0x005dc484`, stores the owner dome pointer at `+0x08`, and returns with `RET 0x4`. Verified backup: `G:\GhidraBackups\BEA_20260531-222637_post_wave1021_motion_controller_constructor_review_verified`. Runtime dome motion behavior, exact source-body identity, concrete layouts, BEA patching, and rebuild parity remain separate proof.

| Address | Name | Purpose |
| --- | --- | --- |
| `0x0049ef80` | `CMCWarspiteDome__Constructor` | Installs motion-controller vtable `0x005dc484` and stores the owner dome pointer. |
| `0x0049efa0` | `CMCWarspiteDome__ScalarDeletingDestructor` | Delete-flags wrapper for the dome motion-controller destructor. |
| `0x0049efc0` | `CMCWarspiteDome__Destructor` | Clears owner/cached fields and tails into the base motion-controller destructor. |
| `0x0049efe0` | `CMCWarspiteDome__VFunc_04_UpdateDomeTransform_0049efe0` | Vtable slot 4; updates dome mesh-part transform outputs from owner-driven state. |

Read-back verified vtable `0x005dc484` slot 1 at `0x0049efa0` and slot 4 at `0x0049efe0`. Runtime dome motion behavior remains unproven by this static correction.

## Exception Handlers

Wave770 static read-back (`unwind-continuation-wave770`, `wave770-readback-verified`) hardened the WarspiteDome.cpp allocation-cleanup rows as `void __cdecl Unwind@...(void)`. DATA scope-table xrefs `0x0061e034`, `0x0061e03c`, and `0x0061e044` point at `0x005d57c0 Unwind@005d57c0`, `0x005d57d6 Unwind@005d57d6`, and `0x005d57ec Unwind@005d57ec`; instruction/decompile evidence calls `OID__FreeObject_Callback` on `*(EBP+0x4)` with WarspiteDome.cpp debug path `0x0063d170`, line tokens `0x19`, `0x1a`, and `0x1d`, and allocation/type values `0x17`, `0x16`, and `0x1b`. Verified backup: `G:\GhidraBackups\BEA_20260523-180835_post_wave770_unwind_continuation_verified`. This is saved static retail Ghidra evidence only; exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d57c0 | Unwind@005d57c0 | 0x19 (25) | Cleanup for 32-byte allocation (pool 0x17) |
| 0x005d57d6 | Unwind@005d57d6 | 0x1a (26) | Cleanup for 96-byte allocation (pool 0x16) |
| 0x005d57ec | Unwind@005d57ec | 0x1d (29) | Cleanup for 12-byte allocation (pool 0x1b) |

## Key Observations

- **Composite pattern** - CWarspiteDome initialization allocates a nested CWarspite-style controller and stores it at `this+0x13c`
- **Inherits from CGroundUnit** - Calls `CGroundUnit__Init(param_1)` during initialization
- **Multiple memory pools used**:
  - Pool 0x17 (23): 32 bytes (0x20) - Unknown component
  - Pool 0x16 (22): 96 bytes (0x60) - CWarspite AI controller
  - Pool 0x1b (27): 12 bytes (0x0c) - Small utility object
- **VTable at 0x005dfc14** - Observed table for the allocated 0x60 Warspite-style controller stored at `this+0x13c`; do not over-promote it to a complete dome-object layout without more evidence
- **Parent VTable at 0x005d8d1c** - Set during destruction (base class vtable)
- **Flags 0x0a000120** - OR'd into the init-context field at `init_context+0x70` before `CGroundUnit__Init`; the copied destination remains layout debt

## CWarspiteDome Object Layout (Partial)

| Offset | Field | Type | Notes |
|--------|-------|------|-------|
| 0x00 | vtable | void* | Exact dome-object vtable remains deferred; `0x005dfc14` is proven for the nested controller table |
| 0x70 | mDomeMotionController | CMCWarspiteDome* | Wave536 stores the allocated motion-controller pointer here after base init |
| 0x7c | mField7C | int | Set to 2 |
| 0x80 | mField80 | int | Set to 2 |
| 0x12c | mField12C | int | Set to 0 |
| 0x130 | mField130 | int | Set to 0 |
| 0x134 | mField134 | int | Set to 0 |
| 0x13c | mAI | CWarspite* | Nested Warspite-style controller |
| 0x208 | mField208 | void* | Component from pool 0x17 |
| 0x260 | mField260 | int | Set to 0 |
| 0x264 | mField264 | int | Set to 0 |
| 0x268 | mArray268[6] | int[6] | Array zeroed on init |
| 0x280 | mField280 | int | Set to 0 |
| 0x284 | mField284 | int | Set to 0 |
| 0x288 | mArray288[6] | int[6] | Array zeroed on init (offset +0x20 from 0x268) |
| 0x3bc | mParentPtr | void* | Parent object pointer |

## Initialization Flow

1. Set fields 0x7c and 0x80 to 2
2. OR `init_context+0x70` with 0x0a000120 before base init
3. Set parent->0x1a0 to 1
4. Call `CGroundUnit__Init()`
5. Allocate 32-byte component (pool 0x17), store at 0x208
6. Allocate 96-byte CWarspite AI (pool 0x16), call `CWarspite__Init()`, store at 0x13c
7. Allocate 12-byte CMCWarspiteDome object (pool 0x1b), call `CMCWarspiteDome__Constructor`, store at `this+0x70`
8. Call `FUN_0050b010()` - additional initialization
9. Zero out arrays at 0x268 and 0x288 (6 elements each)

## Destruction Flow

1. Set vtable to parent class (0x005d8d1c)
2. Release component at offset 0x28 if valid
3. Release component at offset 0x24 if valid
4. Release component at offset 0x0c if valid
5. Call base monitor shutdown helper (`CMonitor__Shutdown`, former `FUN_004bac40`)

## Wave 536 WarspiteDome Lifecycle (2026-05-18)

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x005047e0 | CWarspiteDome__Init | `RET 0x4` proves one explicit `init_context` stack argument after ECX `this`. The body seeds init-context flags, initializes through `CGroundUnit__Init`, allocates/initializes the nested Warspite-style controller at `this+0x13c`, constructs a `CMCWarspiteDome` motion controller, stores it at `this+0x70`, and zeros adjacent state arrays. |
| 0x00504990 | CWarspiteDome__ScalarDeletingDestructor | Vtable `0x005dfc14` slot 1 points here. `RET 0x4` plus the `delete_flags` bit test identifies the MSVC scalar-deleting destructor wrapper; it calls `CWarspiteDome__Destructor`, conditionally frees through `CDXMemoryManager__Free`, and returns `this`. |
| 0x005049b0 | CWarspiteDome__Destructor | Register-only destructor restores base controller vtable `0x005d8d1c`, unregisters pointer cells at `this+0x28`, `this+0x24`, and `this+0x0c` from their owning `CSPtrSet`, then calls `CMonitor__Shutdown`. |

This pass saved signatures/comments/tags only. Runtime dome motion behavior, exact dome/controller layout, exact source-body identity, allocator ownership beyond the observed wrapper free path, and rebuild parity remain unproven.

## Related Files

- Warspite.cpp - Parent AI controller class
- GroundUnit.cpp - Base class for ground-based units
- BattleEngine.cpp - Combat system

## Class Hierarchy

```
CGroundUnit
    |
    +-- CWarspiteDome (contains CWarspite AI)
```

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
