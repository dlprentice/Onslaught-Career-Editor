# PlatformInput.cpp - Platform Input Helpers

## Overview

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

This page tracks platform-input helpers where saved Ghidra rows are bounded by retail static evidence.

## Wave851 PC Platform/Controller Tail

Wave851 PC platform/controller tail (`pc-platform-controller-tail-wave851`, `wave851-readback-verified`) saved comments/tags for late platform key-state/key-sink wrappers. Exact anchors: `0x00515970 PlatformInput__GetKeyOn`, `0x00515980 PlatformInput__ConsumeKeyOnce`, `0x005159b0 PlatformInput__ResetKeyStateTables`, and `0x005159c0 PLATFORM__SetKeySink`. Probe token anchor: `Wave851 PC platform/controller tail`; `0x00515970 PlatformInput__GetKeyOn`; `0x005159c0 PLATFORM__SetKeySink`; `PlatformInput__ConsumeKeyOnce`; `PlatformInput__ResetKeyStateTables`; `5729/6098 = 93.95%`; `0x00515ab0 D3DDevice__SetViewport`; `G:\GhidraBackups\BEA_20260525-085618_post_wave851_pc_platform_controller_tail_verified`.

| Address | Function | Static evidence |
| --- | --- | --- |
| `0x00515970` | `PlatformInput__GetKeyOn` | Returns `DAT_00888c94[key]`; source-reference `PCPlatform::KeyOn -> LT.xKeyOn`; reached by `CController__DoMappings` and `CPCController__GetKeyOn`. |
| `0x00515980` | `PlatformInput__ConsumeKeyOnce` | Reads and clears `DAT_00888d94[key]`; source-reference `PCPlatform::KeyOnce -> LT.xKeyOnce`; reached by frontend/game render paths. |
| `0x005159b0` | `PlatformInput__ResetKeyStateTables` | Calls `PlatformInput__ClearAllKeyStateTables(&DAT_00855bb0)` from frontend init, level init, and FMV reset contexts. |
| `0x005159c0` | `PLATFORM__SetKeySink` | Forwards to Wave848-readback `PlatformInput__SetKeySinkCore(&DAT_00855bb0,key_sink)`; source-reference `PCPlatform::SetKeytrap -> LT.SetKeytrap`. |

Queue after Wave851: `6098` total, `5729` commented, `369` commentless, `0` exact-undefined signatures, `0` `param_N`, strict proxy `5729/6098 = 93.95%`; next raw commentless row `0x00515ab0 D3DDevice__SetViewport`. Runtime input behavior, exact key-table/key-sink callback ABI, BEA patching, and rebuild parity remain deferred.

## Wave848 Platform Input Core

Wave848 platform input core (`platform-input-core-wave848`, `wave848-readback-verified`) saved comments/tags/signatures for three important PlatformInput rows and one adjacent screenshot row in `engine.cpp`/`ltshell.cpp` evidence. Exact anchors: `0x00513120 PlatformInput__InitDirectInput`, `0x00513370 PlatformInput__PollPadState`, and `0x005135f0 PlatformInput__SetKeySinkCore`. Verified backup: `G:\GhidraBackups\BEA_20260525-070518_post_wave848_platform_input_core_verified`. Exact DirectInput interface layout, exact pad-state/key-sink layouts, runtime controller behavior, runtime screenshot output/filesystem behavior, runtime virtual-keyboard behavior, BEA patching, and rebuild parity remain deferred.

| Address | Function | Signature | Static evidence |
| --- | --- | --- | --- |
| `0x00513120` | `PlatformInput__InitDirectInput` | `int __thiscall PlatformInput__InitDirectInput(void * this, void * window_handle)` | Source-reference `PCLTShell::InitDirectInput(HWND)`; calls `DirectInput8Create`, enumerates game controllers through callback `0x00512ff0`, caps joypads to four, sets deadzone `0x96`, sorts new-type pads, and prints `Found %d joypads`. |
| `0x00513370` | `PlatformInput__PollPadState` | `int __thiscall PlatformInput__PollPadState(void * this, int pad_index, bool rotate_buttons)` | Source-reference `PCLTShell::UpdateJoystick(int)`; polls/reacquires DirectInput device state, swaps current/old buffers when requested, and rotates button bytes `0x30` through `0x33` for new-type pads. |
| `0x005135f0` | `PlatformInput__SetKeySinkCore` | `void __thiscall PlatformInput__SetKeySinkCore(void * this, void * key_sink)` | Called from `PLATFORM__SetKeySink`, `CFEPVirtualKeyboard__Shutdown`, and `CFEPVirtualKeyboard__Process`; stores `key_sink` at `this+0x33458` and returns with `RET 0x4`. |

Queue after Wave848: `6098` total, `5678` commented, `420` commentless, `0` exact-undefined signatures, `0` `param_N`, strict proxy `5678/6098 = 93.11%`; next raw commentless row `0x00513640 CEngine__GetConstant32`.

## Wave567 Saved Rows

| Address | Function | Signature | Notes |
| --- | --- | --- | --- |
| `0x005234d0` | `PlatformInput__SetGlobalInputState` | `void __cdecl PlatformInput__SetGlobalInputState(int global_input_state)` | `PlatformInput__InitMouse` pushes `1`, `PlatformInput__ShutdownMouse` pushes `0`, and the body writes `DAT_0089bdf0`. `Input__HandleMouseWindowMessage` checks that global before refreshing stored mouse x/y and normalized window coordinates. |

## Evidence And Limits

Wave567 verified the saved signature/comment/tags through dry/apply/final-dry Ghidra mutation, metadata/tag read-back, xrefs, decompile, and callsite instructions. Runtime capture semantics, exact variable names, BEA patching, and rebuild parity remain unproven.
