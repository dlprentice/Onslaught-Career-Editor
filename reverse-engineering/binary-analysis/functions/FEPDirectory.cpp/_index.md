# FEPDirectory.cpp - Function Analysis

**Source File:** `C:\dev\ONSLAUGHT2\FEPDirectory.cpp`
**Debug Path String:** `0x0063fb4c`
**RTTI Class Name:** `.?AVCFEPDirectory@@` at `0x00629bf8`

## Overview

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

CFEPDirectory is a frontend page class for save-directory browsing. Wave856 FEPDirectory page saved static Ghidra comments/tags for the page lifecycle, selected-save control flow, save-file enumeration, delete-confirmation processing, and render handoff. This is important frontend save-directory infrastructure, not filler; source-body evidence remains sparse enough that the claims stay bounded to static retail Ghidra evidence.

Wave856 (`fepdirectory-page-wave856`, `wave856-readback-verified`) covered `0x0051aa90 CFEPDirectory__Init`, `0x0051aac0 CFEPDirectory__Shutdown`, `0x0051aaf0 CFEPDirectory__ButtonPressed`, `0x0051ac40 CFEPDirectory__Process`, `0x0051ad30 CFEPDirectory__RefreshSaveFileList`, and `0x0051b460 CFEPDirectory__Render`. Queue after Wave856: `6098` total, `5762` commented, `336` commentless, no exact-undefined signatures, no `param_N`, strict proxy `5762/6098 = 94.49%`. Next raw commentless row: `0x0051b600 CFEPMultiplayerStart__SubObj4034__ctor`. Verified backup: `G:\GhidraBackups\BEA_20260525-114000_post_wave856_fepdirectory_page_verified`.

Wave954 (`save-load-directory-review-wave954`) re-reviewed the save/load/directory handoff around `0x00461c40 CFEPLoadGame__Init`, `0x00464620 CFEPSaveGame__Init`, and `0x0051ad30 CFEPDirectory__RefreshSaveFileList` with fresh serialized Ghidra metadata/tag/xref/instruction/decompile/vtable exports. The review found no mutation was needed in Ghidra, but corrected this doc's stale delete-helper context address to live `0x00514ec0 PCPlatform__DeleteSaveFile`. Evidence includes FEPSaveGame.cpp debug string `C:\dev\ONSLAUGHT2\FEPSaveGame.cpp`, FEPDirectory.cpp debug string `C:\dev\ONSLAUGHT2\FEPDirectory.cpp`, Wave911 focused re-audit progress `283/1408 = 20.10%`, static closure `6151/6151 = 100.00%`, and verified backup `G:\GhidraBackups\BEA_20260528-100717_post_wave954_save_load_directory_review_verified`.

## Observed Layout

The saved static evidence points at a large page instance layout:

- `this+0x04` through `this+0x4000`: 0x1000-entry save-name pointer array.
- `this+0x4004`: save-file count.
- `this+0x4008`: selected save index.
- `this+0x400c`: scroll offset.
- `this+0x4010`: timestamp/animation time source.

Exact `CFEPDirectory` layout, runtime frontend save-directory behavior, runtime filesystem/delete behavior, exact save-name encoding semantics, source identity, BEA patching, and rebuild parity remain deferred.

## Wave856 Functions

| Address | Signature | Static evidence |
| --- | --- | --- |
| `0x0051aa90 CFEPDirectory__Init` | `int __fastcall CFEPDirectory__Init(void * this)` | CFEPDirectory vtable `0x005db800` slot 2 / DATA xref `0x005db808`; clears the save-name pointer array and observed count/selection/scroll/timestamp fields. |
| `0x0051aac0 CFEPDirectory__Shutdown` | `void __fastcall CFEPDirectory__Shutdown(void * this)` | Vtable slot 3 / DATA xref `0x005db80c`; frees each non-null save-name buffer through `CDXMemoryManager__Free(&DAT_009c3df0, entry)`. |
| `0x0051aaf0 CFEPDirectory__ButtonPressed` | `void __thiscall CFEPDirectory__ButtonPressed(void * this, int button, float val)` | Vtable slot 5 / DATA xref `0x005db814`; handles up/down, selected-save activation, delete confirmation, selected-save globals `DAT_008a1168` / `DAT_008a116c`, and return-to-page flow. |
| `0x0051ac40 CFEPDirectory__Process` | `void __thiscall CFEPDirectory__Process(void * this, int state)` | Vtable slot 4 / DATA xref `0x005db810`; refreshes the list outside state 3 and consumes delete-confirmation result id 6 before calling `PCPlatform__DeleteSaveFile`. |
| `0x0051ad30 CFEPDirectory__RefreshSaveFileList` | `void __thiscall CFEPDirectory__RefreshSaveFileList(void * this, int force_refresh)` | Called by `CFEPDirectory__Process` and `CFEPVirtualKeyboard__Process`; checks `PCPlatform__GetStorageDeviceInfo`, enumerates `savegames\\*.bes` through `EnumerateSaveFiles_1` / `EnumerateSaveFiles_2`, uses FEPDirectory.cpp debug string `0x0063fb4c`, allocates/fills/frees 0x200-byte buffers, and clamps selection. |
| `0x0051b460 CFEPDirectory__Render` | `void __thiscall CFEPDirectory__Render(void * this, float transition, int dest)` | Vtable slot 7 / DATA xref `0x005db81c`; calls `CFEPDirectory__RenderSaveFileList`, dispatches button `0x2c` on save-list selection, draws title token `0x0f` or `0x0e`, and calls `CFrontEnd__RenderOverlayEffects`. |

## Related Functions

| Address | Function | Notes |
|---------|----------|-------|
| `0x0051ae70` | `CFEPDirectory__RenderSaveFileList` | Shared save-list renderer used by both `CFEPDirectory__Render` and `CFEPVirtualKeyboard__Render`; performs row draw, scroll/selection mouse hit-tests, and returns clicked save index or `0`. |
| `0x00514960` | `PCPlatform__GetStorageDeviceInfo` | Storage availability helper used before save enumeration. |
| `0x005149c0` | `EnumerateSaveFiles_1` | Gets save-file count for `savegames\\*.bes`. |
| `0x00514a80` | `EnumerateSaveFiles_2` | Gets save-file name by index. |
| `0x00514ec0` | `PCPlatform__DeleteSaveFile` | Delete helper reached by `CFEPDirectory__Process` after confirmation; Wave954 corrected this doc from the stale `0x00514cc0` context address. |
| `0x005202d0` | `CFEPVirtualKeyboard__Process` | Calls `CFEPDirectory__RefreshSaveFileList` during keyboard page processing. |

## Memory And Globals

- `DAT_008a9694`: storage device id / platform slot passed into save enumeration and delete helpers.
- `DAT_008a1168`: selected-save index global set by `CFEPDirectory__ButtonPressed`.
- `DAT_008a116c`: selected-save name buffer filled before page transition.
- Save-name buffers are 0x200-byte allocations tied to the `C:\dev\ONSLAUGHT2\FEPDirectory.cpp` debug path at `0x0063fb4c`.

## Version Info

- **Latest analysis date:** 2026-05-25
- **Latest evidence:** Wave856 static Ghidra read-back artifacts and verified backup
- **Binary:** BEA.exe (Steam PC release)
