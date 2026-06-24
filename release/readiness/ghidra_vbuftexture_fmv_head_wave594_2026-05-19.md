# Ghidra VBufTexture / FMV Head Wave594 Readiness Note

Date: 2026-05-19
Status: static saved-Ghidra evidence only

Wave594 hardened the queue-head `CVBufTexture` state-cache helper and the adjacent FMV lifecycle head.

Saved rows:

| Address | Function |
| --- | --- |
| `0x0053f040` | `CVBufTexture__SetStateCacheModeByFlag` |
| `0x0053f0a0` | `CDXFMV__DestructorBody` |
| `0x0053f0f0` | `CDXFMV__ctor_base` |
| `0x0053f140` | `CDXFMV__scalar_deleting_dtor` |
| `0x0053f160` | `VFuncSlot_01_0053f160` |
| `0x0053f180` | `CDXFMV__VFunc_06_0053f180` |

What is proven:

- Ghidra now records clean signatures, function comments, and `vbuftexture-fmv-head-wave594` tags for all six rows.
- `CVBufTexture__SetStateCacheModeByFlag` is a `RET 0x4` helper called twice by `CVBufTexture__RenderAndRestoreStateFlag4`; nonzero mode dispatches `D3DStateCache__ForceSlotMode4or5(0)`, while zero mode dispatches `D3DStateCache__SetStateCached(0,1,4)`.
- `CDXFMV__DestructorBody` tears down the embedded video/device object at `this+0x10`, then reaches `CMonitor__Shutdown(this)`.
- `CDXFMV__ctor_base` is reached from the global initializer callsite at `0x0053f075` for `DAT_0089d690`; it installs the base `CFMV` vtable at `0x005e5018`, constructs the embedded `CDXFrontEndVideo` object at `this+0x10`, then installs the `CDXFMV` vtable at `0x005e4fe4`.
- `CDXFMV__scalar_deleting_dtor` is the `CDXFMV` vtable slot-1 deleting-destructor shape at `0x005e4fe4[1]`; it calls `CDXFMV__DestructorBody`, conditionally frees memory when `delete_flags & 1` is set, and returns with `RET 0x4`.
- `VFuncSlot_01_0053f160` is a shared slot-1 deleting-destructor shape through the `CFMV`/base vtable at `0x005e5018`; the exact owner remains unresolved.
- `CDXFMV__VFunc_06_0053f180` is the `CDXFMV` vtable slot-6 no-argument helper and direct-call target from `CLTShell__InitializeRuntimeAndLoadCoreResources`; it loads the platform singleton and tail-jumps `PlatformInput__ResetKeyStateTables`.
- Post-save read-back verified 6 metadata rows, 6 tag rows, 27 xref rows, 1446 instruction rows, 6 target decompile rows, 2 caller decompile rows, 126 callsite instruction rows, and 48 vtable rows.
- The queue refresh reports `6093` total functions, `3039` commented, `3054` commentless, `1347` exact-undefined signatures, and `1095` `param_N` signatures.
- Comment-backed proxy is `3039/6093 = 49.88%`; strict clean-signature proxy is `2993/6093 = 49.12%`.
- The next high-signal queue head is `0x0053f730 CDXBitmapFont__ctor_like_0053f730`.
- The live Ghidra project backup verified at `G:\GhidraBackups\BEA_20260519-144006_post_wave594_vbuftexture_fmv_head_verified` with 19 files, 160992135 bytes, `DiffCount=0`, and manifest hash `400782d6d7e464d08e427016c204c16a21adee62210c259a4e0781e613a8db1a`.

What is not proven:

- Runtime render-state, FMV playback, Bink, platform-input, teardown, and menu/video behavior remain unproven.
- Exact `CVBufTexture`, `D3DStateCache`, `CFMV`, `CDXFMV`, `CDXFrontEndVideo`, platform-input, and monitor layouts remain unproven beyond the observed fields documented in the read-back notes.
- Exact source identity remains unproven because the current tracked Stuart source snapshot does not include matching implementation bodies for these Wave594 rows.
- Full FMV vtable boundaries, base-class ownership for `VFuncSlot_01_0053f160`, BEA patching, gameplay behavior, and rebuild parity remain unproven.
