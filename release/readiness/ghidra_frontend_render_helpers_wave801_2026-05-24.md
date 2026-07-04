# Ghidra Frontend Render Helpers Wave801 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `frontend-render-helpers-wave801`

Wave801 frontend render helpers saved comments/tags/signatures for eight raw commentless frontend/render helper rows from `0x0044a0c0 CDXMeshVB__GetGlobalZeroDouble` through `0x00465f00 CVBufTexture__GetGlobalEnableByte`. The pass made one rename, from the stale `0x004659a0 CDXEngine__DrawTextScaledWithShadow` label to `0x004659a0 CDXFont__DrawTextScaledWithShadow`, hardened two signatures, made no function-boundary changes, and made no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0044a0c0 CDXMeshVB__GetGlobalZeroDouble` | Saved as `double __cdecl ...`; body returns global double `DAT_00672fd0`; 14 xrefs span HUD target overlay, mesh rendering, texture animation, AYA/resource cache, and render queue paths. |
| `0x00456780 CFEPDebriefing__Initialize` | DATA xref `0x005db9c0`; allocates the debriefing node array and backing buffer using the FEPDebriefing.cpp debug path `0x0062913c`, lines `0x30` and `0x31`, then clears state fields. |
| `0x0045d730 CFEPLevelSelect__UpdateMouseEdgeSlide` | Called by level-select processing; gates on `CFrontEnd__IsMouseInputReady`, cursor globals `DAT_0089bda8/DAT_0089bda4`, cubic scale `_DAT_00679af8 * delta^3 * _DAT_005d8bbc`, and clamps the target value. |
| `0x00465710 CDXFont__DrawTextDynamic` | 67 current xrefs; copies wide text into a capped stack buffer, computes per-character ARGB/fade arrays, then draws shadow and foreground through `CDXFont__DrawTextScaled`. |
| `0x004659a0 CDXFont__DrawTextScaledWithShadow` | Corrected stale owner label; ECX is forwarded to two `CDXFont__DrawTextScaled` calls, first as alpha-only `x+1/y+1` shadow and then as foreground. |
| `0x00465c10 CDXBitmapFont__BuildGlyphRemapTables` | Called by bitmap-font construction; scans `DAT_005db5fc`, updates fallback byte `DAT_00679af4`, fills direct remap `DAT_006799f4`, clears overflow remap `DAT_006799d4`, and skips duplicates in `DAT_005db738`. |
| `0x00465dd0 CFEPVirtualKeyboard__IsInputAccepted` | If `this+0x15c` is nonzero returns 1; otherwise calls the first virtual function with `input_ctx` and compares the result against low byte `DAT_00679af4`. |
| `0x00465f00 CVBufTexture__GetGlobalEnableByte` | Returns the low byte from `DAT_00679b40` in `AL`; upper `EAX` preservation is treated as a decompiler artifact, not proven semantic state. |

Read-back evidence:

- `ApplyFrontendRenderHelpersWave801.java dry`: `updated=0 skipped=8 renamed=0 would_rename=1 signature_updated=2 comment_only_updated=6 missing=0 bad=0`
- `ApplyFrontendRenderHelpersWave801.java apply`: `updated=8 skipped=0 renamed=1 would_rename=0 signature_updated=2 comment_only_updated=6 missing=0 bad=0`
- `ApplyFrontendRenderHelpersWave801.java final dry`: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 8 metadata rows, 8 tag rows, 134 xref rows, 296 instruction rows, and 8 decompile rows.
- Queue after Wave801: 6098 total, 5564 commented, 534 commentless, 0 exact-undefined signatures, 0 param_N signatures, strict clean-signature proxy `5564/6098 = 91.24%`.
- Next raw commentless row: `0x0044d390 CFEPSaveGame__InitDialogAndLayoutState`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-073450_post_wave801_frontend_render_helpers_verified`, 19 files, 171314055 bytes, `DiffCount=0`.

Deferred from this wave:

- `0x0044d390 CFEPSaveGame__InitDialogAndLayoutState`, because the current no-argument signature is too weak for a broad sweep and the body has a larger dialog/layout ABI surface.
- `0x00465640 CLTShell__InvokeWithLoadingTransitionGate`, because the current no-argument signature hides an ECX receiver plus multiple stack arguments around the loading-transition dispatch gate.

What remains unproven:

- Exact source-body identity for these helpers.
- Concrete class/font/frontend/render layout beyond the stated offsets/globals.
- Runtime frontend, mouse, text-render, keyboard, texture, or debriefing behavior.
- BEA patching behavior.
- Rebuild parity.
