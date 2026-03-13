# FEPMultiplayerStart.cpp - Function Analysis

## Overview

**Source File:** `FEPMultiplayerStart.cpp`  
**Debug Path String:** `C:\dev\ONSLAUGHT2\FEPMultiplayerStart.cpp` at `0x0063fc24`  
**Class:** `CFEPMultiplayerStart` (RTTI: `.?AVCFEPMultiplayerStart@@` string at `0x00629bd0`, type descriptor at `0x00629bc8`)  
**Primary Vtable:** `0x005db8d0` (COL `0x00613830` at `0x005db8cc`)

FEP = Front End Page. This page handles the multiplayer setup/start flow in the front-end menu system.

Correction (2026-02-13):
- The vtable at `0x005db7e0` is **not** `CFEPMultiplayerStart`; it is `CFEPLanguageTest` (RTTI `. ?AVCFEPLanguageTest@@`). See `FEPLanguageTest.cpp/_index.md`.

## Vtable Analysis (0x005db8d0)

RTTI CompleteObjectLocator:
- `0x005db8cc` -> `0x00613830`
- `0x00613830 + 0x0c` -> type descriptor `0x00629bc8` (`.?AVCFEPMultiplayerStart@@`)

Primary vtable at `0x005db8d0`:

| Slot | Address | Function | Status |
|------|---------|----------|--------|
| 0 | `0x0051dba0` | `CFEPMultiplayerStart__Init` | Recovered (manual UI `F`), renamed/signed |
| 1 | `0x0051dd90` | `CFEPMultiplayerStart__Shutdown` | Recovered (manual UI `F`), renamed/signed |
| 2 | `0x0051ded0` | `CFEPMultiplayerStart__Process` | Recovered (manual UI `F`), renamed/signed |
| 3 | `0x0051de60` | `CFEPMultiplayerStart__ButtonPressed` | Recovered (manual UI `F`), renamed/signed |
| 4 | `0x0051e120` | `CFEPMultiplayerStart__RenderPreCommon` | Recovered (manual UI `F`), renamed/signed |
| 5 | `0x0051e1b0` | `CFEPMultiplayerStart__Render` | Recovered (manual UI `F`), renamed/signed |
| 6 | `0x0051f350` | `CFEPMultiplayerStart__TransitionNotification` | Recovered (manual UI `F`), renamed/signed |
| 7 | `0x004014c0` | (inherited) | No function object currently |
| 8 | `0x00459990` | (inherited) | No function object currently |

### Embedded Subobject Vtable (0x005db4fc, this+0x8848)

Recovered in headless mode on 2026-02-25 (function-object creation + vtable-slot naming/signatures):

| Slot | Address | Function | Status |
|------|---------|----------|--------|
| 0 | `0x004599a0` | `CFEPMultiplayerStart__SubObj8848__Init` | Recovered (headless create), renamed/signed |
| 1 | `0x00460490` | `CFEPLevelSelect__SyncSelectionFromCurrentWorld` | Existing mapped helper |
| 2 | `0x00459b00` | `CFEPMultiplayerStart__SubObj8848__Process` | Recovered (headless create), renamed/signed |
| 3 | `0x00459c10` | `CFEPMultiplayerStart__SubObj8848__ButtonPressed` | Recovered (headless create), renamed/signed |
| 4 | `0x00459e50` | `CFEPMultiplayerStart__SubObj8848__RenderPreCommon` | Recovered (headless create), renamed/signed |
| 5 | `0x00459ee0` | `CFEPMultiplayerStart__SubObj8848__Render` | Recovered (headless create), renamed/signed |
| 6 | `0x00459aa0` | `CFEPMultiplayerStart__SubObj8848__TransitionNotification` | Renamed from legacy `...__ResetSelectionGrid`; signed |
| 7 | `0x00459a60` | `CFEPMultiplayerStart__SubObj8848__ActiveNotification` | Recovered (headless create), renamed/signed |
| 8 | `0x00459990` | `CFrontEndPage__DeActiveNotification` | Inherited/base-style helper |

## Debug Path References (Asserts)

The debug path string at `0x0063fc24` is referenced from:
- `0x0051dbd9`
- `0x0051dcb2`

These addresses are within the `CFEPMultiplayerStart__Init` body at `0x0051dba0` (confirmed after manual function-object recovery).

## Known Helpers

| Address | Name | Notes |
|---------|------|------|
| `0x0051da60` | `CFEPMultiplayerStart__InitSelection` | Signature normalized: `void CFEPMultiplayerStart__InitSelection(void * this, int mode)`; initializes per-player selection state and timeouts. |
| `0x0051ddd0` | `CFEPMultiplayerStart__HandleInput` | Signature normalized: `void CFEPMultiplayerStart__HandleInput(void * this, int button, int player_index)`; handles directional input for per-player selection arrays (called from `0x0051ee7b` / `0x0051ef9e`). |
| `0x00465f10` | `CFEPMultiplayerStart__ctor` | Signature normalized: `void * CFEPMultiplayerStart__ctor(void * this)`; page constructor wrapper setting vtable/members and embedded page helpers. |
| `0x004661e0` | `CFEPMultiplayerStart__ClearSecondaryPlayerSet` | Constructor-adjacent cleanup helper; clears a second `SPtrSet` field in the multiplayer-start page state (mirrors `...__ClearJoinedPlayerSet` style helper). |
| `0x004661f0` | `CFEPMultiplayerStart__InitWaitingThreadSubsystem` | Constructor-adjacent wrapper that initializes waiting-thread subsystem state via `CWaitingThread__ctor_like_00528bf0`. |
| `0x00459920` | `CFEPMultiplayerStart__SubObj8848__ctor` | Embedded helper constructor (ECX=`this+0x8848`) used by `CFEPMultiplayerStart__ctor`; sets vtable `0x005db4fc`, zeros selection tables, seeds default selection constants. |
| `0x00459aa0` | `CFEPMultiplayerStart__SubObj8848__TransitionNotification` | Embedded subobject transition-notification path; records timestamp then clears a 300-entry selection grid and sets mode-dependent default highlight (`from_page==5 || from_page==6`). |
| `0x004599a0` | `CFEPMultiplayerStart__SubObj8848__Init` | Embedded subobject vtable slot 0 initializer (`int` return) recovered via headless function-create + rename/signature pass. |
| `0x00459a60` | `CFEPMultiplayerStart__SubObj8848__ActiveNotification` | Embedded subobject active-notification hook (`from_page`) recovered via headless function-create + rename/signature pass. |
| `0x00459b00` | `CFEPMultiplayerStart__SubObj8848__Process` | Embedded subobject process hook (`menu_state`) recovered via headless function-create + rename/signature pass. |
| `0x00459c10` | `CFEPMultiplayerStart__SubObj8848__ButtonPressed` | Embedded subobject button handler recovered via headless function-create + rename/signature pass. |
| `0x00459e50` | `CFEPMultiplayerStart__SubObj8848__RenderPreCommon` | Embedded subobject pre-render hook (`transition`) recovered via headless function-create + rename/signature pass. |
| `0x00459ee0` | `CFEPMultiplayerStart__SubObj8848__Render` | Embedded subobject render hook (`transition`, `dest`) recovered via headless function-create + rename/signature pass. |
| `0x00459810` | `CFEPMultiplayerStart__SubObj39B8__QueuePageId` | Embedded helper method (ECX=`this+0x39b8`) that queues the startup page id (`DAT_0066304c`) during `CFrontEnd__Init`. |
| `0x0051b600` | `CFEPMultiplayerStart__SubObj4034__ctor` | Embedded helper constructor (ECX=`this+0x4034`) that installs vtable `0x005e49b4` and initializes runtime field defaults. |
| `0x0051b610` | `CFEPMultiplayerStart__SubObj4034__ResetFlags` | Embedded helper resetting runtime flags (`+0x0c/+0x10`) and global gate `DAT_00677614` with platform-state guard (`DAT_0083d448`). |
| `0x0051be70` | `CFEPMultiplayerStart__SubObj4034__InitRuntimeState` | Embedded helper seeding runtime timestamp (`PLATFORM__GetSysTimeFloat`), clearing transition/scene globals, and resetting subobject state at `+0x18`. |

Naming note:
- The `SubObjXXXX` labels are intentional offset-stable names for embedded helpers where source-parity class names are not yet available in the reference drop.

## Recovery Status

The vtable entrypoints were previously missing as Ghidra function objects and could not be created safely via MCP without risking UI deadlock/timeouts. They were recovered via manual CodeBrowser create (`F` in Listing) and then renamed/signed/commented via MCP with immediate read-back verification (2026-02-13).

Additional recovery (2026-02-25):
- Embedded subobject vtable `0x005db4fc` missing entrypoints (`0x004599a0`, `0x00459a60`, `0x00459b00`, `0x00459c10`, `0x00459e50`, `0x00459ee0`) were created in headless mode and then renamed/signed with decompile read-back verification.
