# Ghidra Texel Unpack Head/Middle Review Wave1071 Readiness Note

Status: complete static read-only evidence
Date: 2026-06-02
Scope: `texel-unpack-head-mid-review-wave1071`

Wave1071 re-read forty-one existing Wave672/Wave673 texel unpack head/middle rows without Ghidra mutation. The pass made no rename, signature change, comment change, tag change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4` | DATA slot `0x005e9f40`; reads BGR source bytes through the Wave672 profile fields and writes float4 RGBA with alpha `1.0`. |
| `0x00584d78 CFastVB__UnpackTexels_Bits565ToFloat4` | DATA slot `0x005e9f70`; expands 5/6/5 packed lanes into RGB float4 and fills alpha `1.0`. |
| `0x00585072 CFastVB__UnpackTexels_Bits2_10_10_10_ToFloat4` | DATA-backed packed-lane unpacker in the same Wave672 table family. |
| `0x0058546f CMeshCollisionVolume__UnpackTexels_Bits16_16_16_16_ToFloat4` | DATA slot `0x005ea048`; body expands four 16-bit lanes and still has bounded owner/layout identity. The current saved owner label is retained because fresh evidence proves texture-unpack behavior but not a stronger exact class owner. |
| `0x00585576 CDXTexture__UnpackTexels_Bits332ToFloat4` | DATA-backed 3-3-2 unpacker with RGB lane expansion and alpha fill. |
| `0x005856b8 CDXTexture__UnpackTexels_Bits332A8ToFloat4` | Wave672 end anchor; expands paired 3-3-2 plus 8-bit alpha source records. |
| `0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor` | Wave673 start anchor; constructor thunk forwards the format descriptor, binds vtable `0x005e9f3c`, and bridges into the continuation profile table. |
| `0x0058579b CTexture__UnpackTexels_Bits444ToFloat4_AlphaOne` | DATA-backed 4-4-4 unpacker with alpha forced to `1.0`. |
| `0x0058586b CTexture__UnpackTexels_PaletteIndexA8ToFloat4` | Expands indexed texel data through lookup-like state and applies 8-bit alpha. |
| `0x00585bd3 CFastVB__TexelUnpackProfile_scalar_deleting_dtor` | Scalar-deleting destructor for the texel-unpack profile object family. |
| `0x00585cb0 CTexture__UnpackTexels_Signed8_8_ToFloat4_RG` | Signed 8-8 RG unpacker in the Wave673 middle tranche. |
| `0x00585e9f CDXTexture__UnpackTexels_Signed8_8_A8_ToFloat4_RG` | Signed 8-8 plus alpha unpacker with scalar alpha lane. |
| `0x00585fa3 CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4` | Wave673 end anchor before the Wave1070 tail bridge. |

Read-back evidence:

- Primary exports: `41` metadata rows, `41` tag rows, `83` xref rows, `1856` function-body instruction rows, and `41` decompile rows.
- Context exports: `7` metadata rows, `11` xref rows, `707` function-body instruction rows, and `7` decompile rows for adjacent Wave674/Wave675 profile/registry/factory rows.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1319/1560 = 84.55%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260602-031627_post_wave1071_texel_unpack_head_mid_review_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The current saved Ghidra names, signatures, comments, and tags for the forty-one primary rows remain internally coherent with fresh metadata, xref, instruction, and decompile evidence.
- The Wave672/Wave673 texel-unpack head and middle rows still line up with their observed DATA slots and source-field/lane-expansion behavior.
- The odd `0x0058546f` owner label remains intentionally bounded; the fresh evidence supports texture-unpack behavior, not a stronger exact owner claim.

What remains separate proof:

- Runtime texture output behavior.
- Runtime codec/FourCC behavior.
- Exact profile/descriptor/layout identity.
- Exact source identity.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Next candidate note: continue with the next expanded static re-audit cluster; prefer read-only review first and mutate only when fresh evidence proves a correction or normalization need.

Probe token anchor: Wave1071; texel-unpack-head-mid-review-wave1071; 0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4; 0x0058546f CMeshCollisionVolume__UnpackTexels_Bits16_16_16_16_ToFloat4; 0x005856b8 CDXTexture__UnpackTexels_Bits332A8ToFloat4; 0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor; 0x00585fa3 CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4; 812/1408 = 57.67%; 1319/1560 = 84.55%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260602-031627_post_wave1071_texel_unpack_head_mid_review_verified; read-only review.
