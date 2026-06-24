# Ghidra CVBufTexture Render Helpers Wave804 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `cvbuftexture-render-helpers-wave804`

Wave804 CVBufTexture render helpers saved Ghidra comments/tags for two CVBufTexture render-path rows: `0x00472e50 CVBufTexture__DrawSpriteWithDefaultTextureFallback` and `0x00476fe0 CVBufTexture__RenderDynamicUnitPass`. The pass hardened the sprite-wrapper signature to `int __thiscall CVBufTexture__DrawSpriteWithDefaultTextureFallback(void * this, float screen_x, float screen_y, float draw_width, float draw_height, float argb_tint_bits)`, retained the dynamic-unit-pass signature, made no renames, made no function-boundary changes, and made no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00472e50 CVBufTexture__DrawSpriteWithDefaultTextureFallback` | Xref from `0x00527ba7 CGame__DrawLocalCoopControllerPrompt`; reads texture wrapper field `this+0x08`; lazily resolves fallback texture `s_meshtex_default_tga_00625498` through `CTexture__FindTexture` into `DAT_0089ce84`; forwards screen position, fixed depth `0.001`, fallback tint `0xff000000`, and width/height-derived UV scale/bounds to `CVBufTexture__DrawSpriteEx`; `RET 0x14` proves five stack arguments after `ECX=this`. |
| `0x00476fe0 CVBufTexture__RenderDynamicUnitPass` | Xref from `0x0050ab91 CVBufTexture__RenderAndRestoreStateFlag4`; walks active unit list globals `DAT_00855170`/`DAT_00855178`; dispatches `CDXEngine__BuildProjectedSprites(&DAT_009c7550, unit)`; traverses collision-map owners through `CMapWhoEntry__GetOwner`; gates `CRenderQueue__InsertSortedByDepth(&DAT_009c7550, unit, depth)` with `DAT_0089d680`, `g_MeshQualityDistance`, and `g_MeshQualityLodTable`. |

Read-back evidence:

- `ApplyCVBufTextureRenderHelpersWave804.java dry`: `updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=1 missing=0 bad=0`
- `ApplyCVBufTextureRenderHelpersWave804.java apply`: `updated=2 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=1 missing=0 bad=0`
- `ApplyCVBufTextureRenderHelpersWave804.java final dry`: `updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 2 metadata rows, 2 tag rows, 2 xref rows, 338 instruction rows, 2 decompile rows, 7 context metadata rows, and 7 context decompile rows.
- Queue after Wave804: 6098 total, 5576 commented, 522 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5576/6098 = 91.44%`, strict clean-signature proxy `5576/6098 = 91.44%`.
- Next raw commentless row is `0x00488f60 CInfantryUnit__VFunc_02_00488f60`; commentless high-signal, signature, and name-confidence queues are empty.
- Verified backup: `G:\GhidraBackups\BEA_20260524-091718_post_wave804_cvbuftexture_render_helpers_verified`, 19 files, 171314055 bytes, `DiffCount=0`.

What this proves:

- The two target rows exist in the saved Ghidra project.
- The sprite fallback wrapper has the saved thiscall/five-stack-argument signature, comment, and tags.
- The dynamic unit render pass has saved comments/tags tying the older read-only guard to the current Ghidra project.
- The observed behavior is static retail Ghidra evidence tied to decompile, instruction, xref, context metadata, and queue exports.

What remains unproven:

- Exact source identity.
- Texture wrapper, unit, collision, render-queue, material, shader, skeleton, and animation layout parity.
- Runtime rendering behavior.
- BEA patching behavior.
- Rebuild parity.
