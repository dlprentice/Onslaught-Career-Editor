# Ghidra Texture Core Tail Wave876 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `texture-core-tail-wave876`

Wave876 texture core tail saved comments, tags, and clean signatures for twelve texture-resource and render-format connector rows from `0x00556cc0 CTexture__ctor` through `0x0055a170 CEngine__TextureFormatD3DToIndex`. The pass made no renames, no function-boundary changes, no executable-byte changes, did not launch BEA, and did not mutate the installed game.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00556cc0 CTexture__ctor` | Calls `CTextureBase__Init(this+0x08)`, installs `CDXSurf__vtable`, initializes texture/resource fields and CShaderBase state; xrefs include `CTexture__FindTexture`, `CDXBattleLine`, `CDXCompass`, `CDXFont`, and `CDXTexture__Deserialize`. |
| `0x00556f50 CTexture__Release` | Clears render-state cache slots 0-3, then dispatches the object vtable release/delete slot when `this` is non-null; xrefs include shell/frontend shutdown, `CTexture__FindTexture`, `CTexture__ClearOut`, and `CTexture__FreeLevelResources`. |
| `0x00557060 CTextureSequence__EnsureLoaded` | Uses global device/resource state `DAT_00888c8c`, flag `this+0x14c`, Wave849 texture-format helpers, `this+0xac/+0xb0/+0x148/+0x150`, and `CEngine__CreateTextureOrFatal` to ensure a texture pointer at `this+0xb8`. |
| `0x005572c0 CTextureSequence__ReleaseIfLoaded` | Releases non-null `this+0xb8` through vtable slot `+0x08`, clears it, and returns zero. |
| `0x00557a00 CDXTexture__FormatToString` | Maps observed internal texture-format indices 0-10 to string-table names including `UNKNOWN`, `A1R5G5B5`, `A4R4G4B4`, `X8R8G8B8`, `A8R8G8B8`, `R5G6B5`, compressed-format entries, and `Q8W8V8U8`. |
| `0x00557a90 CDXTexture__LoadTextureFromFile_Core` | Handles empty-name/procedural/ordinary texture names, lower-cased `data\Textures` paths, animated-frame detection, per-frame `CDXTexture__LoadTextureFromFile`, mapped-file decode through `CDXTexture__DecodeMappedFileToTexture`, and width/height/format updates. The decompile still exposes an `unaff_EBX` format-reconciliation path, so exact ABI/layout remains bounded. |
| `0x00558690 CDXTexture__GetAnimatedFrame` | 53 xrefs; returns the single frame at `this+0xb8` or selects a time-scaled modulo frame pointer from `this+0xb8 + frame*4`. |
| `0x00558870 CDXTexture__DumpAllTexturesToTga` | `con_dumptextures` helper; creates `TextureDump`, walks global texture list `DAT_0083d9b0` via `+0xa0`, and dumps selected entries through `CDXTexture__DumpTextureToRGBA`. |
| `0x005588f0 CVBufTexture__RenderModePass` | Configures CVBufTexture render-mode D3DStateCache/RenderState state for observed modes 0-5 and is called by `CVBufTexture__Render`, `CMeshRenderer__RenderMeshWithLayerPasses`, and Wave875 `CVBufTexture__DrawSpriteEx`. |
| `0x00558ef0 CVBufTexture__SetupSecondaryBlend` | Secondary texture-stage blend helper called three times from `CVBufTexture__RenderModePass`; checks `CDXTexture__IsResourceHandleValid(DAT_009cc118)`, `DAT_009cc124`, stage-1 state, and render-state color `0x3c`. |
| `0x0055a0f0 CEngine__TextureFormatIndexToD3D` | Maps internal format indices 1-10 to D3D/FourCC constants `0x19`, `0x1a`, `0x16`, `0x15`, `0x17`, `0x31545844`, `0x32545844`, `0x34545844`, `0x3c`, and `0x3f`. |
| `0x0055a170 CEngine__TextureFormatD3DToIndex` | Inverse D3D/FourCC to internal texture-format index mapper called by `CEngine__TextureFormatField32FD4ToIndex`. |

Read-back evidence:

- `ApplyTextureCoreTailWave876.java dry`: `updated=0 skipped=12 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyTextureCoreTailWave876.java apply`: `updated=12 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyTextureCoreTailWave876.java final dry`: `updated=0 skipped=12 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: 12 metadata rows, 12 tag rows, 86 xref rows, 1491 instruction rows, 12 decompile rows, 10 context metadata rows, and 10 context decompile rows.
- Queue after Wave876: 6113 total, 5885 commented, 228 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed and strict clean-signature proxy `5885/6113 = 96.27%`.
- Next raw commentless row: `0x0055b0e0 CWaterRenderSystem__ctor`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-212045_post_wave876_texture_core_tail_verified`, 19 files, 172690311 bytes, `DiffCount=0`.

What this proves:

- The twelve target function rows exist in the saved Ghidra project with the saved signatures, comments, and `texture-core-tail-wave876` / `wave876-readback-verified` tags.
- The observed behavior is static retail Ghidra decompile/xref/instruction evidence tied to prior Wave832, Wave849, and Wave875 context.
- These are high-importance texture/resource/render connector rows with low local evidence density, not low-importance filler.

What remains unproven:

- Exact `CTexture`, `CDXTexture`, `CVBufTexture`, `CTextureSequence`, and `CEngine` field layouts.
- Exact enum names for texture formats, render modes, and D3D state values.
- Runtime texture load/decode/animation/render/dump behavior.
- BEA patching behavior.
- Rebuild parity.
