# Ghidra DX Font / CDXFrontEnd Head Wave596 Readiness Note

Date: 2026-05-19
Status: static saved-Ghidra evidence only

Wave596 hardened the next queue head after Wave595: two DX bitmap-font rows and five CDXFrontEnd wrapper/vtable rows.

Saved rows:

| Address | Function |
| --- | --- |
| `0x00540840` | `CDXBitmapFont__Deserialize` |
| `0x00540970` | `CDXBitmapFont__HasAnimatedTexture` |
| `0x00540b60` | `CDXFrontEnd__DestructorBody` |
| `0x00540bf0` | `CDXFrontEnd__Constructor` |
| `0x00540c10` | `CDXFrontEnd__scalar_deleting_dtor` |
| `0x00540f70` | `CDXFrontEnd__RenderStart` |
| `0x00540fb0` | `CDXFrontEnd__VFunc_07_00540fb0` |

What is proven:

- Ghidra now records clean signatures, function comments, and `dxfont-frontend-head-wave596` tags for all seven rows.
- `CDXBitmapFont__Deserialize` is called four times by `PCPlatform__DeserializeFontsAndAssets`. `RET 0x4` proves one stack argument after `this`; the body reads serialized texture/font tables from the chunk reader, caches the texture at `this+0x170`, fills font metadata/glyph data, clears the GDI-font flag, and initializes CVBufTexture vertex/index formats.
- `CDXBitmapFont__HasAnimatedTexture` is called by `CConsole__RenderLoadingScreen`; it checks the cached texture at `this+0x170` and returns true only when `CDXTexture__GetAnimatedFrame` returns a non-null frame.
- `CDXFrontEnd__DestructorBody` is the non-freeing destructor body called by `CDXFrontEnd__scalar_deleting_dtor`; it unwinds waiting-thread/SPtrSet/device-object style members, installs the fallback vtable at `this+8`, and calls `CMonitor__Shutdown(this)`.
- `CDXFrontEnd__Constructor` is called from raw startup/init code, runs `CFEPMultiplayerStart__ctor`, installs the CDXFrontEnd vtable at `0x005e5054`, and returns `this`.
- `CDXFrontEnd__scalar_deleting_dtor` is CDXFrontEnd vtable `0x005e5054` slot 1. `RET 0x4` proves one stack argument after `this`; the body calls `CDXFrontEnd__DestructorBody(this)` and frees only when `delete_flags` bit 0 is set.
- `CDXFrontEnd__RenderStart` is CDXFrontEnd vtable `0x005e5054` slot 6, reached by `CFrontEnd__Render`; it resets world render state, initializes transform caches, clears the screen, enables render state `0x1b`, and forwards `this` into `CFrontEnd__RenderStart`.
- `CDXFrontEnd__VFunc_07_00540fb0` is CDXFrontEnd vtable `0x005e5054` slot 7, reached by `CFrontEnd__Render`. `RET 0x4` proves one stack parameter; when `render_particles` is nonzero it calls `CDXFrontEnd__SetupRenderMatricesAndProjection`, then forwards into `CFrontEnd__RenderCursorEndSceneAndAsyncSave`.
- Post-save read-back verified 7 metadata rows, 7 tag rows, 13 xref rows, 679 instruction rows, 7 decompile rows, and 48 vtable-slot rows.
- The queue refresh reports `6093` total functions, `3053` commented, `3040` commentless, `1343` exact-undefined signatures, and `1085` `param_N` signatures.
- Comment-backed proxy is `3053/6093 = 50.11%`; strict clean-signature proxy is `3008/6093 = 49.37%`.
- The next high-signal queue head is `0x00541200 CDXFrontEndVideo__CDXFrontEndVideo`.
- The live Ghidra project backup verified at `[maintainer-local-ghidra-backup-root]\BEA_20260519-155113_post_wave596_dxfont_frontend_head_verified` with 19 files, 161057671 bytes, `DiffCount=0`, and manifest hash `eb9f038af50b5a97a210b4447f8692b993547d896f5c51d622b89c73718672a2`.

What is not proven:

- Runtime font deserialization, loading-screen text behavior, frontend construction/teardown, frontend render-start/render-tail behavior, particle/projection behavior, and save scheduling remain unproven.
- Exact `CDXBitmapFont`, `CDXTexture`, `CVBufTexture`, `CDXFrontEnd`, `CFrontEnd`, frontend page, waiting-thread, and device-object layouts remain unproven beyond the observed fields documented in the read-back notes.
- Exact source identity remains unproven because the current tracked Stuart source snapshot does not include matching `DXFont.cpp`/CDXFrontEnd implementation bodies.
- BEA patching, gameplay behavior, packaged release behavior, and rebuild parity remain unproven.
