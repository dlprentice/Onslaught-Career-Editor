# Ghidra Texel Unpack Tail Review Wave1070 Readiness Note

Status: complete static read-only evidence
Date: 2026-06-02
Scope: `texel-unpack-tail-review-wave1070`

Wave1070 re-read twelve existing Wave674/Wave675 texel unpack, callback, raw-copy, L16A16, and row-window codec rows without Ghidra mutation. The pass made no rename, signature change, comment change, tag change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor` | Constructor thunk reached from `0x00588098 CFastVB__CreateTexelUnpackProfileByFormat`; binds vtable `0x005ea020` after the shared descriptor initializer. |
| `0x005860ba CTexture__UnpackTexels_Signed16_16_ToFloat4_RG` | DATA slot `0x005ea0fc`; reads source fields `+0x1058/+0x105c/+0x20`, advances two 16-bit words per texel, sign-scales R/G, and fills Z/A as `1.0`. |
| `0x005861b4 CDXTexture__UnpackTexels_Signed2_10_10_10_ToFloat4` | DATA slot `0x005ea10c`; sign-extends/scales three 10-bit lanes and scales the top two-bit lane into alpha. |
| `0x00586305 CDXTexture__UnpackTexels_Signed16_16_16_16_ToFloat4` | DATA slot `0x005ea11c`; sign-scales four 16-bit lanes into RGBA. |
| `0x00586438 CTexture__UnpackTexels_NormalXY_Signed8_8_ReconstructZ` | DATA slot `0x005ea12c`; sign-scales X/Y normals and reconstructs Z with `sqrt(max(0, 1 - x*x - y*y))`. |
| `0x00586609 CDXTexture__UnpackTexels_CallbackPerTexel_Stride2_SetRGBAOne` | DATA slot `0x005ea16c`; calls `CDXTexture__UnpackTexels_DispatchIndirect_00575a65` per two-byte source texel and forces G/B/A to `1.0`. |
| `0x005866d2 CFastVB__UnpackTexels_CallbackPerTexel_Stride4_SetZAOne` | DATA slot `0x005ea19c`; calls the same indirect unpack dispatcher per dword source texel and forces Z/A to `1.0`. |
| `0x0058677b CDXTexture__UnpackTexels_CallbackSingleTexel` | DATA slot `0x005ea1ac`; forwards a single texel through `CDXTexture__UnpackTexels_DispatchIndirect_00575a65` before key-color/post-process gates. |
| `0x0058686f CTexture__UnpackTexels_CopyRaw128` | DATA slot `0x005ea1f8`; copies 16 bytes per texel directly into the destination vec4 array before key-color/post-process gates. |
| `0x005868d1 CFastVB__UnpackTexels_L16A16_ToFloat4` | DATA slot `0x005ea208`; expands 16-bit luminance into RGB and 16-bit alpha into A. |
| `0x00586bb7 CFastVB__FlushPendingConvertedRows16` | Called by `0x00586f37 CFastVB__DecodeRowWindowToScratchPairs` and `0x00587daf CFastVB__TexelPackProfile_scalar_deleting_dtor`; writes dirty scratch pairs back to 16-bit row storage and clears the dirty flag. |
| `0x00586f37 CFastVB__DecodeRowWindowToScratchPairs` | Called by `0x0058735a CFastVB__StoreDecodedBlockToScratch` and `0x005873f8 CFastVB__LoadDecodedBlockFromScratch`; flushes stale dirty rows and decodes packed two-pixel RGBG/GBGR/YUY2/UYVY-style windows into float4 scratch pairs. |

Read-back evidence:

- Primary exports: `12` metadata rows, `12` tag rows, `14` xref rows, `1100` instruction rows, and `12` decompile rows.
- Context exports: `7` metadata rows, `10` xref rows, `254` instruction rows, and `7` decompile rows for adjacent Wave673-Wave675 profile/registry rows.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1278/1560 = 81.92%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260602-022701_post_wave1070_texel_unpack_tail_review_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The current saved Ghidra names, signatures, comments, and tags for the twelve primary rows remain internally coherent with fresh metadata, xref, instruction, and decompile evidence.
- The Wave674/Wave675 texel-unpack callbacks still line up with their vtable DATA slots and observed `RET` stack cleanup.
- The Wave675 row-window codec helpers still line up with the dirty-row flush/decode/store/load call graph.

What remains separate proof:

- Runtime texture output behavior.
- Runtime codec/FourCC behavior.
- Exact profile/descriptor/row-window layouts.
- Exact source identity.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Next candidate note: continue with the next expanded static re-audit cluster; prefer read-only review first and mutate only when fresh evidence proves a correction or normalization need.

Probe token anchor: Wave1070; texel-unpack-tail-review-wave1070; 0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor; 0x005860ba CTexture__UnpackTexels_Signed16_16_ToFloat4_RG; 0x005861b4 CDXTexture__UnpackTexels_Signed2_10_10_10_ToFloat4; 0x00586305 CDXTexture__UnpackTexels_Signed16_16_16_16_ToFloat4; 0x00586438 CTexture__UnpackTexels_NormalXY_Signed8_8_ReconstructZ; 0x00586609 CDXTexture__UnpackTexels_CallbackPerTexel_Stride2_SetRGBAOne; 0x005866d2 CFastVB__UnpackTexels_CallbackPerTexel_Stride4_SetZAOne; 0x0058677b CDXTexture__UnpackTexels_CallbackSingleTexel; 0x0058686f CTexture__UnpackTexels_CopyRaw128; 0x005868d1 CFastVB__UnpackTexels_L16A16_ToFloat4; 0x00586bb7 CFastVB__FlushPendingConvertedRows16; 0x00586f37 CFastVB__DecodeRowWindowToScratchPairs; 812/1408 = 57.67%; 1278/1560 = 81.92%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260602-022701_post_wave1070_texel_unpack_tail_review_verified; read-only review.
