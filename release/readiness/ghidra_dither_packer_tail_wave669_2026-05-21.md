# Ghidra Dither Packer Tail Wave669 Readiness

Status: ready for public-safe release accounting
Date: 2026-05-21

## Scope

Wave669 dither packer tail saved static Ghidra metadata for twelve adjacent CDXTexture/CFastVB/CTexture dither-packer rows after Wave668:

| Address | Saved name | Saved signature |
| --- | --- | --- |
| `0x00582ef8` | `CDXTexture__PackTexels_Dither_Bits2_10_10_10` | `void __thiscall CDXTexture__PackTexels_Dither_Bits2_10_10_10(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x00583041` | `CDXTexture__PackTexels_Dither_Bits8888` | `void __thiscall CDXTexture__PackTexels_Dither_Bits8888(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x0058318a` | `CDXTexture__PackTexels_Dither_Bits888` | `void __thiscall CDXTexture__PackTexels_Dither_Bits888(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x005832af` | `CDXTexture__PackTexels_Dither_Bits1616` | `void __thiscall CDXTexture__PackTexels_Dither_Bits1616(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x005833a6` | `CDXTexture__PackTexels_Dither_Bits2_10_10_10_Alt` | `void __thiscall CDXTexture__PackTexels_Dither_Bits2_10_10_10_Alt(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x005834ef` | `CDXTexture__PackTexels_Dither_Bits16_16_16_16` | `void __thiscall CDXTexture__PackTexels_Dither_Bits16_16_16_16(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x00583670` | `CDXTexture__PackTexels_Dither_PaletteIndexA8` | `void __thiscall CDXTexture__PackTexels_Dither_PaletteIndexA8(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x005837b7` | `CDXTexture__PackTexels_Dither_PaletteIndex8` | `void __thiscall CDXTexture__PackTexels_Dither_PaletteIndex8(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x00583891` | `CFastVB__PackTexels_Dither_L8` | `void __thiscall CFastVB__PackTexels_Dither_L8(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x00583979` | `CFastVB__PackTexels_Dither_A8L8` | `void __thiscall CFastVB__PackTexels_Dither_A8L8(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x00583a94` | `CTexture__PackTexels_Dither_A4L4` | `void __thiscall CTexture__PackTexels_Dither_A4L4(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x00583ba4` | `CTexture__PackTexels_Dither_L16` | `void __thiscall CTexture__PackTexels_Dither_L16(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |

Tag anchors: `dither-packer-tail-wave669`, `wave669-readback-verified`, `static-reaudit`, `retail-binary-evidence`, `signature-hardened`, and `comment-hardened`.

Probe anchors: `0x00582ef8 CDXTexture__PackTexels_Dither_Bits2_10_10_10`, `0x00583ba4 CTexture__PackTexels_Dither_L16`, and next queue head `0x00583c8e CTexture__PackTexels_Dither_Bits8_8`.

## Evidence

- Dry mode: `updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=12 missing=0 bad=0`
- Apply mode: `updated=12 skipped=0 renamed=0 would_rename=0 signature_updated=12 missing=0 bad=0`
- Final dry mode: `updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- All three passes reported `REPORT: Save succeeded`.
- Post exports verified `12` metadata rows, `12` tag rows, `12` xref rows, `444` instruction rows, and `12` clean decompile rows.
- Backup verified: `G:\GhidraBackups\BEA_20260521-030557_post_wave669_dither_packer_tail_verified`, `19` files, `163810183` bytes, `DiffCount=0`.

## Queue

Post-Wave669 queue telemetry:

- Total functions: `6098`
- Commented functions: `3713`
- Commentless functions: `2385`
- Exact-undefined signatures: `1217`
- `param_N` signatures: `604`
- Comment-backed proxy: `3713/6098 = 60.89%`
- Strict clean-signature proxy: `3663/6098 = 60.07%`
- Next queue head: `0x00583c8e CTexture__PackTexels_Dither_Bits8_8`

## Boundaries

This is static metadata evidence only. Exact dither table provenance, texel-pack callback ABI, channel-order enum contracts, palette metric/layout, luminance contract, runtime texture output behavior, BEA patching, and rebuild parity remain unproven.
