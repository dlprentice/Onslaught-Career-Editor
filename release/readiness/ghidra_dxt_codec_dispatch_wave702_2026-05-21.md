# Ghidra DXT Codec / Dispatch Wave702 Readiness

Status: validated
Date: 2026-05-21
Scope: saved Ghidra metadata only; no executable bytes, function boundaries, original game files, copied profiles, runtime proof, or public asset payloads changed.

## What Changed

Wave702 DXT codec / dispatch saved signatures, parameter names, comments, and tags for eleven adjacent DXT codec and dispatch-table rows.

Probe anchors: `0x0059764a CDXTexture__DecodeDxt1ColorBlockToRgba`, `0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags`, and next queue head `0x00598702 CTexture__NodePayloadBaseCtor`.

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x0059764a` | `int __stdcall CDXTexture__DecodeDxt1ColorBlockToRgba(float * rgba_float_block16_out, void * dxt1_color_block)` | Decodes two RGB565 endpoints, builds the DXT1 color palette, and writes sixteen RGBA float4 rows from the two-bit selector mask. |
| `0x0059778a` | `int __stdcall CTexture__DecodeDxt3BlockToFloatRgba(float * rgba_float_block16_out, void * dxt3_block)` | Reuses the DXT1 color decoder at `block+8`, then expands two explicit 4-bit alpha dwords into sixteen output alpha lanes. |
| `0x0059780d` | `int __stdcall CTexture__DecodeDxt5BlockToFloatRgba(float * rgba_float_block16_out, void * dxt5_block)` | Reuses the DXT1 color decoder at `block+8`, builds the DXT5 alpha ladder, and applies two 24-bit selector groups. |
| `0x00597949` | `int __stdcall CTexture__EncodeDxt5AlphaIndices_ErrorDiffusion(void * dxt_color_block_out, float * rgba_float_block16)` | Error-diffuses alpha samples, rounds corrected values, and calls the scalar selector quantizer with the observed alpha-mode marker. |
| `0x00597a61` | `void __stdcall CFastVB__PackScalarBlock_4BitEndpoints(void * dxt3_block_out, float * rgba_float_block16)` | Packs explicit 4-bit alpha nibbles with residual diffusion and then quantizes the color block at `output+8`. |
| `0x00597b87` | `int __stdcall CFastVB__PackScalarBlock_InterpolatedEndpoints(void * dxt5_block_out, float * rgba_float_block16)` | Solves/interpolates DXT5 alpha endpoints, handles edge cases, and packs selector bytes with residual diffusion. |
| `0x00598056` | `void __stdcall CTexture__EncodeDxt3AlphaBlock(void * dxt3_block_out)` | Premultiplies a hidden source block into stack storage and forwards it to the DXT3 scalar-block packer. |
| `0x0059808a` | `int __stdcall CTexture__EncodeDxt5AlphaBlock(void * dxt5_block_out)` | Premultiplies a hidden source block into stack storage and forwards it to the DXT5 scalar-block packer. |
| `0x005980be` | `void __cdecl CFastVB__InitDispatchTableVariant_005980be(void * math_dispatch_table)` | Seeds one math dispatch-table variant with observed scalar/base transform, matrix, quaternion, half-float, and batch helper pointers. |
| `0x0059822c` | `void __cdecl CFastVB__InitDispatchTableVariant_0059822c(void * math_dispatch_table)` | Seeds an alternate math dispatch-table variant with alternate matrix/quaternion/batch helpers and SIMD half-float conversion slots. |
| `0x00598474` | `void __cdecl CFastVB__InitDispatchOpsFromFeatureFlags(void * math_dispatch_table)` | Queries `CFastVB__DetectCpuFeatureMask` and conditionally replaces dispatch slots for observed feature-mask bits. |

Tag anchor: `dxt-codec-dispatch-wave702`; read-back tag: `wave702-readback-verified`.

## Evidence

- Pre-export found all `11` targets: `11` metadata rows, `11` tag rows, `17` xref rows, `1067` instruction rows, and `11` decompile rows.
- `ApplyDxtCodecDispatchWave702.java` dry run: `updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=11 missing=0 bad=0`.
- Apply run: `updated=11 skipped=0 renamed=0 would_rename=0 signature_updated=11 missing=0 bad=0`.
- Final dry run: `updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`.
- Post-export verified all `11` saved signatures/tags/comments with `17` xref rows, `1067` instruction rows, and `11` clean decompile rows.
- Queue refresh after Wave702: `6098` total functions, `4056` commented, `2042` commentless, `1216` exact-undefined signatures, `270` `param_N` signatures, comment-backed proxy `4056/6098 = 66.51%`, strict clean-signature proxy `4002/6098 = 65.63%`.
- Next queue head: `0x00598702 CTexture__NodePayloadBaseCtor`.
- Verified Ghidra backup: `G:\GhidraBackups\BEA_20260521-175105_post_wave702_dxt_codec_dispatch_verified`, `19` files, `165251975` bytes, `DiffCount=0`.

## Boundaries

This wave proves saved static retail Ghidra metadata only. Exact DXT block ABI, alpha selector ordering, residual diffusion policy, dispatch-table slot schema, CPU feature-bit names, runtime texture fidelity, runtime compression quality, BEA patching, and rebuild parity remain unproven.

The installed Steam game and original `BEA.exe` were not modified.
