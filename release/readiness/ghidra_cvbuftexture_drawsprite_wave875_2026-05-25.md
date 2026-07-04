# Ghidra CVBufTexture DrawSprite Wave875 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `cvbuftexture-drawsprite-wave875`

Wave875 CVBufTexture DrawSprite saved the signature, comment, and tags for `0x00555be0 CVBufTexture__DrawSpriteEx`, the raw commentless queue head after Wave874. The pass made no rename, no function-boundary change, no executable-byte change, and no BEA/runtime launch. Probe anchors include `91 xrefs`, `texture+0xac`, `texture+0xb0`, and `texture+0xb2`.

This row is high-importance renderer/HUD/frontend connective infrastructure with low local evidence density, not low-importance filler. Static xrefs show it is the shared sprite-quad emitter behind loading-screen, game-interface, HUD, briefing-log, message-log, pause-menu, menu item, battle-line, compass, imposter, mouse-cursor, and surface rendering paths.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00555be0 CVBufTexture__DrawSpriteEx` | Saved as `void __cdecl CVBufTexture__DrawSpriteEx(float screen_x, float screen_y, float depth_z, void * texture, int anchor_or_blend_mode, int uv_mode, float uv_or_tile_scale, float rotation_radians, float argb_tint_bits, float width_scale, float height_scale, float u0, float u1, float v0, float v1)`. |
| Texture metadata | Reads texture dimensions/shift fields at `texture+0xac`, `texture+0xb0`, and `texture+0xb2`; exact `CVBufTexture`/texture layout remains unproven. |
| Vertex payload | Builds four 7-float vertices as `x/y/z/w/color/u/v`, handles anchor cases `1-8`, uv-mode cases `0-4`, optional `fcos`/`fsin` rotation, and optional platform window scaling. |
| Render handoff | Calls texture vtable slot `+0x20`, `CDXEngine__ApplyPendingRenderState`, `CVBufTexture__RenderModePass`, global `CFastVB` at `DAT_00897a98`, and `CFastVB__RenderTriangleStripImmediate`. |
| Xref spread | Post export verified `91` xrefs from `CConsole__RenderLoadingScreen`, `CGameInterface__Render`, `CHud__...`, `HudOverlay__DrawSpriteQuad`, `CLevelBriefingLog__Render`, `CDXEngine__RenderMouseCursorSprite`, `CMessageLog__...`, `CPauseMenu__Render`, `CMenuItemDropdown__Render`, `CDXBattleLine__Render`, `CDXCompass__Render`, `CDXImposter__RenderAll`, `CDXSurf__RenderSurface`, and `CMenuItem__RenderValueBar`. |

Read-back evidence:

- `ApplyCVBufTextureDrawSpriteWave875.java dry`: `updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyCVBufTextureDrawSpriteWave875.java apply`: `updated=1 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyCVBufTextureDrawSpriteWave875.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 91 xref rows, 516 instruction rows, 1 decompile row, 7 context metadata rows, and 7 context decompile rows.
- Queue after Wave875: 6,113 total functions, 5,873 commented, 240 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5873/6113 = 96.07%`, strict clean-signature proxy `5873/6113 = 96.07%`.
- Next raw commentless row: `0x00556cc0 CTexture__ctor`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-205138_post_wave875_cvbuftexture_drawsprite_verified`, 19 files, 172,624,775 bytes, `DiffCount=0`.

What this proves:

- The target function row exists in the saved Ghidra project.
- The saved signature has no `undefined` return and no `param_N` names.
- The saved comment and tags include `cvbuftexture-drawsprite-wave875` and `wave875-readback-verified`.
- The observed body is static retail Ghidra evidence tied to xrefs, decompile, instruction exports, and context caller exports.

What remains unproven:

- Exact `CVBufTexture` and texture object layouts.
- Exact enum names for anchor/blend mode and uv mode.
- Exact uv/tile semantics for all callers.
- Runtime visual output.
- BEA patching behavior.
- Rebuild parity.
