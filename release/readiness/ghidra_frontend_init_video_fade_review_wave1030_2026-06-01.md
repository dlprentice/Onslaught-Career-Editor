# Ghidra Frontend Init Video Fade Review Wave1030

Status: complete read-only static review
Date: 2026-06-01
Scope: `frontend-init-video-fade-review-wave1030`

Wave1030 re-read three frontend init, pre-common fade, and video-quad rows from the Wave911 residual surface. The review made no mutation: no Ghidra mutation, no rename, no signature change, no comment/tag change, no function-boundary change, and no executable-byte change.

Primary targets:

| Address | Saved state | Fresh evidence |
| --- | --- | --- |
| `0x004662a0 CFrontEnd__Init` | `int __thiscall CFrontEnd__Init(void * this, int entry, int in_loaded_system)` | Xref from `0x004684d0 CFrontEnd__Run`; body keeps the Wave467 source-bridge shape for loading ranges, `CFrontEnd__LoadSharedResources`, page init/default-size checks, controller/input setup, page selection, and `CFrontEnd__SetPage` routing. |
| `0x004679e0 CFrontEnd__RenderPreCommonFade` | `void __stdcall CFrontEnd__RenderPreCommonFade(float transition, uint argb, int destination_page)` | Xrefs from `CFEPDebriefing__RenderPreCommon`, `CFEPCredits__RenderPreCommon`, `CFEPLanguageTest__RenderPreCommon`, `CFEPOptions__RenderPreCommon`, and `CFEPScreenPos__RenderPreCommon`; body clamps fade alpha and calls `CFrontEnd__RenderVideoQuadScaledToWindow`. |
| `0x00452ce0 CFrontEnd__RenderVideoQuadScaledToWindow` | `void __stdcall CFrontEnd__RenderVideoQuadScaledToWindow(float scale, int argb, float center_x, float center_y)` | Xrefs from `CFrontEnd__RenderPreCommonFade`, `CFEPMultiplayerStart__SubObj8848__RenderPreCommon`, and `CFEPMain__RenderPreCommon`; body resolves sentinel center coordinates from `PLATFORM__GetWindowWidth/Height`, sets D3D state, and calls `CDXFrontEndVideo__Render`. |

Context evidence covered `0x00452b00 CFEPCommon__Init`, `0x00452b30 CFEPCommon__Shutdown`, `0x00452b60 CFrontEndPage__Process_NoOp`, `0x00452da0 SharedVFunc__NoOp_Ret08`, `0x00466ae0 CFrontEnd__SetPage`, `0x00468770 CFrontEnd__PlaySound`, `0x00462b70 CFEPMain__RenderPreCommon`, `0x00459e50 CFEPMultiplayerStart__SubObj8848__RenderPreCommon`, `0x00441e20 CDXFrontEndVideo__ClearByteFlag`, and `0x00441e30 CDXFrontEndVideo__SetByteFlagAndReturnOld`.

Evidence counts:

- Primary exports: 3 metadata rows, 3 tag rows, 9 xref rows, 481 body-instruction rows, and 3 decompile rows.
- Context exports: 10 metadata rows, 10 tag rows, 354 xref rows, 221 body-instruction rows, and 10 decompile rows.
- Queue closure remains `6238/6238 = 100.00%` with 0 commentless, 0 exact-undefined signatures, and 0 `param_N`.
- Wave911 focused re-audit progress after Wave1030: `621/1408 = 44.11%`; expanded static surface progress: `850/1493 = 56.93%`; Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-032415_post_wave1030_frontend_init_video_fade_review_verified`, 19 files, 173968263 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The saved frontend init, shared fade, and video-quad helper rows remain internally coherent under fresh metadata/tag/xref/instruction/decompile exports.
- The Wave467 CFrontEnd init/fade source-bridge comments and the Wave374 video-quad signature remain supported by current caller/decompile evidence.
- The rows line up with CFEPCommon video helper context, page/sound routing, and representative `CFEPMain` / `CFEPMultiplayerStart` pre-common callers.

What remains unproven:

- Runtime frontend behavior, runtime video behavior, runtime transition visuals, input behavior, or visual QA.
- Exact CFrontEnd, CFEPCommon, CFEPMain, CFEPMultiplayerStart, or CDXFrontEndVideo layouts.
- Exact source-body identity beyond static source/decompile parity.
- BEA patch behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1030; frontend-init-video-fade-review-wave1030; 0x004662a0 CFrontEnd__Init; 0x004679e0 CFrontEnd__RenderPreCommonFade; 0x00452ce0 CFrontEnd__RenderVideoQuadScaledToWindow; 621/1408 = 44.11%; 850/1493 = 56.93%; 500/500 = 100.00%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-032415_post_wave1030_frontend_init_video_fade_review_verified; no mutation.
