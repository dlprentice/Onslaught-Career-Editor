# Ghidra CFastVB Render Immediate Wave854 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `cfastvb-render-immediate-wave854`

Wave854 CFastVB render immediate saved a corrected name, signature, comment, and tags for the raw queue head at `0x0051a6a0`, changing stale `CFastVB__RenderIndexedImmediate` to `CFastVB__RenderTriangleStripImmediate`. The pass made one rename, one signature correction, no function-boundary change, and no executable-byte change.

Representative anchors:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x0051a6a0 CFastVB__RenderTriangleStripImmediate` | `void __thiscall CFastVB__RenderTriangleStripImmediate(void * this)` | Unlocks the CVBuffer at `this+0x00`, binds the vertex stream through Direct3D device vtable `+0x190` using stride `0x1c`, sets raw vertex shader/FVF handle `0x144`, then calls the device draw entry at vtable `+0x144` with primitive type `5`, start vertex `this+0x06`, and primitive count `this+0x08-2`. |
| Caller context | Loading/render/sprite immediate strips | Xrefs from `CConsole__RenderLoadingScreen`, `CRenderQueue__RenderAll` twice, and `CVBufTexture__DrawSpriteEx`; callers lock or fill the global CFastVB instance before this immediate non-indexed draw path. |
| Contrast with `CFastVB__Render` | Non-indexed path | Unlike `CFastVB__Render`, this row does not bind shared CIBuffer `DAT_00897a90`; it resets `this+0x06` to `0xffff` and `this+0x08` to `0` after drawing. |

Read-back evidence:

- `ApplyCFastVBRenderImmediateWave854.java dry`: `updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=1 missing=0 bad=0`
- `ApplyCFastVBRenderImmediateWave854.java apply`: `updated=1 skipped=0 renamed=1 would_rename=1 signature_updated=1 comment_only_updated=1 missing=0 bad=0`
- `ApplyCFastVBRenderImmediateWave854.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: `1` metadata row, `1` tag row, `4` xref rows, `221` instruction rows, and `1` decompile row.
- Additional read-only evidence: `7` context metadata rows, `7` context decompile rows, `3` caller metadata rows, `3` caller decompile rows, and FastVB.cpp debug-string dump `C:\dev\ONSLAUGHT2\FastVB.cpp` at `0x0063fb24`.
- Queue after Wave854: `6098` total functions, `5755` commented, `343` commentless, `0` exact-undefined signatures, `0` `param_N`, comment-backed proxy `5755/6098 = 94.38%`, strict clean-signature proxy `5755/6098 = 94.38%`.
- Next raw commentless row: `0x0051a970 CFEPCredits__TransitionNotification`.
- Verified backup: `G:\GhidraBackups\BEA_20260525-104123_post_wave854_cfastvb_render_immediate_verified`, `19` files, `172166023` bytes, `DiffCount=0`.

What this proves:

- The target row exists in the saved Ghidra project with the Wave854 name, signature, comment, and tags.
- The row is an important renderer connector for immediate CFastVB triangle-strip drawing used by loading UI, render queue overlay paths, and sprite drawing.

What remains unproven:

- Exact `CFastVB` and global render-state layouts.
- Exact Direct3D interface version or method identity beyond observed vtable slots.
- Runtime render output.
- Exact source-body identity.
- BEA patching behavior.
- Rebuild parity.
