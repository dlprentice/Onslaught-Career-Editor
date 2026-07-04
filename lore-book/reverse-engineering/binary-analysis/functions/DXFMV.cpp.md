# DXFMV.CPP Functions

> Source File: DXFMV.CPP | Binary: BEA.exe
> Debug Path: 0x00650644 (`[maintainer-local-source-export-root]\DXFMV.CPP`)

## Overview

DirectX full-motion-video wrapper around the front-end video implementation. Wave594 is the first static saved-Ghidra pass that documents this file's adjacent retail FMV lifecycle head.

Wave802 static read-back (`frontend-save-multiplayer-wave802`, `wave802-readback-verified`) corrected `0x00465640 CLTShell__InvokeWithLoadingTransitionGate` to `0x00465640 CFMV__PlayFullscreenWithLoadingGate`. `RET 0x1c` proves seven explicit stack arguments after `ECX=this`; the body stores/toggles a loading gate at `this+0x0c`, calls `CController__SetNonInteractiveSection(true/false)`, conditionally forwards `g_LanguageIndex`, and dispatches vtable slot `+0x2c`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-081932_post_wave802_frontend_save_multiplayer_verified`. Exact CFMV layout, vtable slot contract, runtime FMV playback/localization behavior, BEA patching, and rebuild parity remain deferred.

## Debug Path Location

- **Address**: 0x00650644
- **String**: `[maintainer-local-source-export-root]\DXFMV.CPP`

## 2026-05-19 Wave594 VBufTexture / FMV Head Read-Back

Wave594 saved signatures, comments, and tags for five adjacent FMV rows and one adjacent `CVBufTexture` state-cache helper. The FMV rows are:

| Address | Name | Evidence |
| --- | --- | --- |
| `0x0053f0a0` | `CDXFMV__DestructorBody` | SEH-wrapped teardown body; reaches the embedded video/device object at `this+0x10`, then `CMonitor__Shutdown(this)` |
| `0x0053f0f0` | `CDXFMV__ctor_base` | Called from the global initializer at `0x0053f075` for `DAT_0089d690`; installs base `CFMV` vtable `0x005e5018`, constructs embedded `CDXFrontEndVideo` at `this+0x10`, then installs `CDXFMV` vtable `0x005e4fe4` |
| `0x0053f140` | `CDXFMV__scalar_deleting_dtor` | `CDXFMV` vtable `0x005e4fe4` slot 1; calls `CDXFMV__DestructorBody`, conditionally frees on `delete_flags & 1`, returns with `RET 0x4` |
| `0x0053f160` | `VFuncSlot_01_0053f160` | Shared slot-1 deleting-destructor shape through the `CFMV`/base table at `0x005e5018`; exact owner remains unresolved |
| `0x0053f180` | `CDXFMV__VFunc_06_0053f180` | `CDXFMV` vtable slot 6 and direct-call target from `CLTShell__InitializeRuntimeAndLoadCoreResources`; tail-jumps `PlatformInput__ResetKeyStateTables` |

Read-back evidence verified 6 metadata rows, 6 tag rows, 27 xref rows, 1446 instruction rows, 6 target decompile rows, 2 caller decompile rows, 126 callsite instruction rows, and 48 vtable rows across the whole Wave594 tranche. Queue after Wave594: `6093` total, `3039` commented, `3054` commentless, `1347` exact-undefined signatures, `1095` `param_N`, comment-backed proxy `3039/6093 = 49.88%`, strict proxy `2993/6093 = 49.12%`, and next head `0x0053f730 CDXBitmapFont__ctor_like_0053f730`.

This is static retail evidence only. Runtime FMV/Bink behavior, exact `CFMV`/`CDXFMV`/`CDXFrontEndVideo` layouts, exact source identity, full vtable boundaries, BEA patching, and rebuild parity remain unproven.

## Notes

- Wave594 replaces the older stub status with static read-back for the five FMV head rows above.
- Referenced in the _index.md as having 8 functions (CDXFMV, CBinkOpenThread - Bink video playback, async loading)
- Part of the DX rendering subsystem
- Uses RAD Game Tools Bink Video SDK
- Functions may be inlined or require manual Ghidra analysis
- Related to: DXFrontEndVideo.cpp, Cutscene.cpp

## Expected Functionality

- CDXFMV class - main FMV player
- CBinkOpenThread - async video loading thread
- Bink SDK integration
- Video texture surface management
- Audio sync

## TODO

1. [ ] Find xrefs to debug path string 0x00650644
2. [ ] Analyze CDXFMV class
3. [ ] Document Bink SDK usage
4. [ ] Map threading model

---

*Stub created: 2025-12-16 - Pending xref discovery*
