# Ghidra Dither Packer Head Wave668 Readiness

Status: ready for public-safe release accounting
Date: 2026-05-21

## Scope

Wave668 dither packer head saved static Ghidra metadata for twelve adjacent decoded-texel post-process and dither-packer rows after Wave667:

| Address | Saved name | Saved signature |
| --- | --- | --- |
| `0x0058210e` | `CTexture__PostProcessDecodedTexels_GammaOrSquare` | `void __thiscall CTexture__PostProcessDecodedTexels_GammaOrSquare(void * this, float * texel_vec4_array, uint unused_context)` |
| `0x00582244` | `CFastVB__PackTexels_Dither_Bits8_8_8_BGR` | `void __thiscall CFastVB__PackTexels_Dither_Bits8_8_8_BGR(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x00582355` | `CFastVB__PackTexels_Dither_Bits8_8_8_8_ARGB` | `void __thiscall CFastVB__PackTexels_Dither_Bits8_8_8_8_ARGB(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x0058249e` | `CFastVB__PackTexels_Dither_Bits8_8_8_RGB` | `void __thiscall CFastVB__PackTexels_Dither_Bits8_8_8_RGB(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x005825c3` | `CFastVB__PackTexels_Dither_Bits5_6_5` | `void __thiscall CFastVB__PackTexels_Dither_Bits5_6_5(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x005826e8` | `CFastVB__PackTexels_Dither_Bits5_5_5` | `void __thiscall CFastVB__PackTexels_Dither_Bits5_5_5(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x0058280d` | `CFastVB__PackTexels_Dither_A1R5G5B5` | `void __thiscall CFastVB__PackTexels_Dither_A1R5G5B5(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x00582950` | `CFastVB__PackTexels_Dither_A4R4G4B4` | `void __thiscall CFastVB__PackTexels_Dither_A4R4G4B4(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x00582a99` | `CTexture__PackTexels_Dither_Bits332` | `void __thiscall CTexture__PackTexels_Dither_Bits332(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x00582bbe` | `CTexture__PackTexels_Dither_Bits8` | `void __thiscall CTexture__PackTexels_Dither_Bits8(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x00582c8a` | `CTexture__PackTexels_Dither_Bits565` | `void __thiscall CTexture__PackTexels_Dither_Bits565(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x00582dd3` | `CTexture__PackTexels_Dither_Bits444` | `void __thiscall CTexture__PackTexels_Dither_Bits444(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |

Tag anchors: `dither-packer-head-wave668`, `wave668-readback-verified`, `static-reaudit`, `retail-binary-evidence`, `signature-hardened`, and `comment-hardened`.

Probe anchors: `0x0058210e CTexture__PostProcessDecodedTexels_GammaOrSquare`, `0x00582dd3 CTexture__PackTexels_Dither_Bits444`, and next queue head `0x00582ef8 CDXTexture__PackTexels_Dither_Bits2_10_10_10`.

## Evidence

- Dry mode: `updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=12 missing=0 bad=0`
- Apply mode: `updated=12 skipped=0 renamed=0 would_rename=0 signature_updated=12 missing=0 bad=0`
- Final dry mode: `updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- All three passes reported `REPORT: Save succeeded`.
- Post exports verified `12` metadata rows, `12` tag rows, `52` xref rows, `444` instruction rows, and `12` clean decompile rows.
- Backup verified: `G:\GhidraBackups\BEA_20260521-024019_post_wave668_dither_packer_head_verified`, `19` files, `163744647` bytes, `DiffCount=0`.

## Queue

Post-Wave668 queue telemetry:

- Total functions: `6098`
- Commented functions: `3701`
- Commentless functions: `2397`
- Exact-undefined signatures: `1217`
- `param_N` signatures: `616`
- Comment-backed proxy: `3701/6098 = 60.69%`
- Strict clean-signature proxy: `3651/6098 = 59.87%`
- Next queue head: `0x00582ef8 CDXTexture__PackTexels_Dither_Bits2_10_10_10`

## Boundaries

This is static metadata evidence only. Exact dither table provenance, texel-pack callback ABI, channel-order enum contracts, gamma/curve identity, runtime texture output behavior, BEA patching, and rebuild parity remain unproven.
