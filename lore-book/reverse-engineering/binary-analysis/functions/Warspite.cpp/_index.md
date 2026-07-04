# Warspite.cpp Functions

> Source File: Warspite.cpp | Binary: BEA.exe
> Debug Path: 0x0063d12c

## Overview

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

Naval AI controller implementation. CWarspite manages battleship/capital ship AI behavior including pathfinding (waypoints) and combat engagement. Named after HMS Warspite.

Wave1217 (`wave1217-lifecycle-cleanup-tail-current-risk-review`) re-read and comment/tag-normalized `CWarspite__ScalarDeletingDestructor` with adjacent `CWarspite__Destructor` context. Fresh evidence preserves the scalar-deleting wrapper contract for vtable `0x005dfbdc`, with no rename, signature, function-boundary, or executable-byte change. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-110625_post_wave1217_lifecycle_cleanup_tail_current_risk_review_verified`. Runtime Warspite controller cleanup behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x00504460 | CWarspite__Create | Wave536 `RET 0x4` factory: allocates 0x60 controller from pool 0x16, calls `CWarspite__Init`, installs vtable `0x005dfbdc`, and stores it at `this+0x13c` | read-back documented |
| 0x005044f0 | CWarspite__ScalarDeletingDestructor | Wave536 scalar-deleting destructor wrapper; calls `CWarspite__Destructor`, frees through the global memory manager when `delete_flags & 1`, and returns `this` | read-back documented |
| 0x004fe710 | CWarspite__Init | Wave528 `RET 0x8` init helper taking `owner_unit` and `init_context`; returns `this` | read-back documented |
| 0x004fde70 | CWarspite__TransitionToUndeploying | Wave839 state/animation transition helper: if `this+0x244 equals 4`, writes state 5, looks up `s_undeploying_006239d8`, and dispatches vfunc `+0xf0` with the resolved animation index | read-back documented |
| 0x00504510 | CWarspite__Destructor | Wave536 register-only destructor: restores base controller vtable, unregisters tracked pointer cells at `+0x28/+0x24/+0x0c`, then calls `CMonitor__Shutdown` | read-back documented |
| 0x004fef40 | CWarspite__Update | Wave528 ECX-only vtable update returning a float-like x87 value | read-back documented |

## Exception Handlers

Wave770 static read-back (`unwind-continuation-wave770`, `wave770-readback-verified`) hardened the Warspite.cpp allocation/monitor/active-reader cleanup rows as `void __cdecl Unwind@...(void)`. DATA scope-table xrefs `0x0061dfd4` through `0x0061e00c` point at `0x005d5770 Unwind@005d5770`, `0x005d5790 Unwind@005d5790`, `0x005d5798 Unwind@005d5798`, and `0x005d57a3 Unwind@005d57a3`. Evidence includes Warspite.cpp debug path `0x0063d12c`, `OID__FreeObject_Callback` on `*(EBP-0x10)` with line token `0x0a` and allocation/type value `0x16`, `CMonitor__Shutdown(*(EBP-0x10))`, and `CGenericActiveReader__dtor` on offsets `+0x0c` and `+0x24`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-180835_post_wave770_unwind_continuation_verified`. This is saved static retail Ghidra evidence only; exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d5770 | Unwind@005d5770 | 10 | Cleanup for 96-byte allocation |

## Key Observations

- **Pool ID 0x16** - Uses memory pool 22, object size 96 bytes (0x60)
- **State machine** - Event-driven with 3 modes:
  - Fighting (event 0x7d3/2003)
  - Waypoint following (event 0xbb9/3001)
  - Custom target (event 0xbba/3002)
- **Ship oscillation** - Random parameters for visual bobbing effect
- **VTable at 0x005dfbdc** - CWarspite virtual function table
- Wave523 corrected the old `CWarspite__UpdateAimTransformAndAttachTargetReader` label at `0x004fb650` to `CUnit__ForwardAimTransformAndAttachTargetReader`. The helper is still called from `CWarspite__Update`, but the body is a generic `this+0x140` forwarder also reached from non-Warspite unit-family paths.
- Wave524 hardened `0x004fbc90` as `CWarspite__GetMountedUnitPitchOrZero`, an ECX-only helper returning the active linked unit/profile float at `this+0x140 -> +0xa0 -> +0x88` or a global fallback. The strongest named caller remains `CWarspite__Update`, but runtime pitch/use semantics and the exact field meaning remain unproven.
- Wave528 hardened `0x004fe710` as `void * __thiscall CWarspite__Init(void * this, void * owner_unit, void * init_context)` and `0x004fef40` as `float __fastcall CWarspite__Update(void * this)`. The pass confirms stack shape, event scheduling, active-reader initialization, support-selection refresh, and x87 return behavior as static retail evidence only.
- Wave536 hardened `0x00504460`, `0x005044f0`, and `0x00504510` as the factory, scalar-deleting destructor wrapper, and destructor body for the `0x005dfbdc` CWarspite controller vtable. Runtime AI behavior, allocator ownership beyond observed free paths, exact source-body identity, and rebuild parity remain unproven.
- Wave839 hardened `0x004fde70 CWarspite__TransitionToUndeploying` with comment/tags only. Static evidence ties it to an important Warspite state/animation transition helper: `this+0x244 equals 4`, writes state 5, asks the owner/unit pointer at `this+0x30` for `s_undeploying_006239d8`, calls `CMesh__FindAnimationIndexByName`, and reaches `0x004ff2ae CWarspite__Update`. Exact Warspite state enum names, concrete owner/unit animation-resource type, runtime AI/animation behavior, BEA patching, and rebuild parity remain deferred. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-023901_post_wave839_warspite_transition_verified`.

## Wave 839 Warspite Transition (2026-05-25)

Wave839 Warspite Transition saved comment/tags for `0x004fde70 CWarspite__TransitionToUndeploying` with the `warspite-transition-wave839` and `wave839-readback-verified` tags. The existing signature remains `void __thiscall CWarspite__TransitionToUndeploying(void * this)`.

| Address | Static read-back evidence |
|---------|---------------------------|
| 0x004fde70 | Checks whether `this+0x244 equals 4`; if false, returns without changing state. |
| 0x004fde82 | Writes state 5 to `this+0x244`. |
| 0x004fde92 | Pushes `s_undeploying_006239d8` for the undeploying animation resource lookup. |
| 0x004fde97 | Calls owner/unit vfunc `+0x24` through the pointer at `this+0x30`, with args `1` and `0`. |
| 0x004fde9c | Calls `CMesh__FindAnimationIndexByName`. |
| 0x004fdea4 | Dispatches receiver vfunc `+0xf0` with the resolved animation index. |

Named caller xref `0x004ff2ae CWarspite__Update` ties this helper to the Warspite update path. Additional raw controller/AI xrefs are `0x00416870`, `0x0044655f`, `0x00446671`, `0x0044671a`, and `0x00534f99`. Post-Wave839 queue telemetry is `6098` total, `5663` commented, `435` commentless, `0` exact-undefined signatures, `0` `param_N`, comment-backed proxy `5663/6098 = 92.87%`, and strict clean-signature proxy `5663/6098 = 92.87%`. The next raw commentless row is `0x005016b0 InitShaderCapabilityFlagsAndCVar`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-023901_post_wave839_warspite_transition_verified`.

This is saved static retail Ghidra evidence only. Exact Warspite state enum names, concrete owner/unit animation-resource type, runtime AI/animation behavior, BEA patching, and rebuild parity remain unproven.

## Wave 536 Warspite Lifecycle (2026-05-18)

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x00504460 | CWarspite__Create | `RET 0x4` proves one explicit `init_context` stack argument after ECX `this`/owner unit. The body allocates 0x60 bytes from pool 0x16 with Warspite.cpp line 10 provenance, calls `CWarspite__Init`, installs vtable `0x005dfbdc`, and writes the controller pointer to `this+0x13c`, clearing that slot on allocation failure. |
| 0x005044f0 | CWarspite__ScalarDeletingDestructor | Vtable `0x005dfbdc` slot 1 points here. `RET 0x4` plus the `delete_flags` bit test identifies the MSVC scalar-deleting destructor wrapper; it calls `CWarspite__Destructor`, conditionally frees through `CDXMemoryManager__Free`, and returns `this`. |
| 0x00504510 | CWarspite__Destructor | Register-only destructor restores base controller vtable `0x005d8d1c`, unregisters pointer cells at `this+0x28`, `this+0x24`, and `this+0x0c` from their owning `CSPtrSet`, then calls `CMonitor__Shutdown`. |

This pass saved one rename plus signatures/comments/tags only. Runtime destruction ordering, concrete Warspite layout, exact source-body identity, allocator ownership beyond the observed wrapper free path, and rebuild parity remain unproven.

## Wave 528 Warspite Init / Update (2026-05-18)

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x004fe710 | CWarspite__Init | `RET 0x8` proves `owner_unit` and `init_context` after ECX. The helper returns `this`, initializes active readers at `+0x24/+0x28` from init-context fields `+0xa4/+0x3b4`, schedules events `0x7d3`, `0xbb9`, and `0xbba`, and randomizes oscillation fields when profile `+0x19c` exists. |
| 0x004fef40 | CWarspite__Update | ECX-only vtable update returning a float-like value through the x87 path. The body advances base state, checks owner-unit vfunc `+0x150`, updates target/reader state, calls `CUnit__ForwardAimTransformAndAttachTargetReader`, refreshes support selection through `CSquadNormal__SelectBestSupportOrEscort`, and may call `CWarspite__TransitionToUndeploying`. |

This pass saved signatures/comments/tags only. Runtime AI behavior, exact return contract, exact source-body identity, concrete Warspite/layout state, local names/types, and rebuild parity remain unproven.

## AI State Machine

| State Index | Mode | Event | Notes |
|-------------|------|-------|-------|
| -1 | Idle | - | Default state |
| 0 | Fighting | 0x7d3 | Combat engagement, 3000ms delay |
| 1 | Waypoint | 0xbb9 | Navigation mode |
| 2 | Target | 0xbba | Custom target, 10s timeout |

## Debug Strings

- `"%s CANT start fighting cos it already was !!!"`
- `"%s CANT start following waypoints cos it already was !!!"`

## CWarspite Object Layout (96 bytes)

| Offset | Field | Notes |
|--------|-------|-------|
| 0x00 | vtable | Virtual function table |
| 0x08 | mParent | Parent battle engine |
| 0x20 | mStateIndex | Current AI state (-1, 0, 1, 2) |
| 0x44 | mTimeoutTime | Timeout timestamp |
| 0x48-0x5C | mOscillation[6] | Ship oscillation params |

## Related Files

- Unit.cpp - Base unit class
- BattleEngine.cpp - Combat system

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
