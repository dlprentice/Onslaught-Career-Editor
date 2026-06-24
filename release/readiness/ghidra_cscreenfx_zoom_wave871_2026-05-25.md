# Ghidra CScreenFx Zoom Wave871 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `cscreenfx-zoom-wave871`

Wave871 CScreenFx zoom saved comments/tags for three screen-effect zoom lifecycle helpers from `0x00551c90 CScreenFx__InitZoomEffectCvar` through `0x00551d40 CScreenFx__ReleaseZoomTextures`. Existing clean signatures were reviewed and left unchanged. The pass made no renames, no function-boundary changes, and no executable-byte changes.

These rows are important screen-effect renderer infrastructure, not low-importance filler.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00551c90 CScreenFx__InitZoomEffectCvar` | `CEngine__Init` callsite `0x00449cfb`; clears zoomline/reticle CVBufTexture slots, sets `state+0x10` to enabled, and registers `cg_zoomeffectenabled` with description `Is the visual effect for zooming enabled?`. |
| `0x00551cc0 CScreenFx__LoadZoomTextures` | `CEngine__InitResources` callsite `0x00449d58`; resolves `screenfx\zoomlines.tga` and `screenfx\reticle.tga` through `CScreenFx__FindTexture(texture_name, 1)`, stores pointers at `state+0/state+4`, then configures matching VB/IB formats. |
| `0x00551d40 CScreenFx__ReleaseZoomTextures` | `CEngine__Shutdown` callsite `0x0044989a`; decrements resource refcounts for non-null zoomline/reticle CVBufTexture pointers and clears both slots. |

Read-back evidence:

- `ApplyCScreenFxZoomWave871.java dry`: `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=3 missing=0 bad=0`
- `ApplyCScreenFxZoomWave871.java apply`: `updated=3 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=3 missing=0 bad=0`
- `ApplyCScreenFxZoomWave871.java final dry`: `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 3 metadata rows, 3 tag rows, 3 xref rows, 67 instruction rows, 3 decompile rows, 69 xref-site instruction rows, 4 helper metadata rows, and 4 string dumps.
- Queue after Wave871: 6105 total, 5854 commented, 251 commentless, 0 exact-undefined signatures, 0 `param_N` signatures, comment-backed proxy `5854/6105 = 95.89%`, strict clean-signature proxy `5854/6105 = 95.89%`.
- Next raw commentless row: `0x00552470 CEngine__ReleaseField6C0`.
- Verified backup: `G:\GhidraBackups\BEA_20260525-183506_post_wave871_cscreenfx_zoom_verified`, 19 files, 172460935 bytes, `DiffCount=0`.

What this proves:

- The three target function rows exist in the saved Ghidra project.
- Their saved signatures remain clean `void __fastcall ... (void * state)` forms with no `param_N` debt.
- The saved comments and tags include `cscreenfx-zoom-wave871` and `wave871-readback-verified`.
- The observed cvar, texture-load, VB/IB-format, and release-refcount bodies are static retail Ghidra evidence tied to string dumps, helper metadata, function-body exports, and code xrefs.

What remains unproven:

- Exact CScreenFx layout.
- Exact D3D enum names for the numeric VB/IB format arguments.
- Runtime zoom-line/reticle rendering behavior.
- Runtime cvar toggling behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
