# Ghidra Texel Packer Continuation Wave670 Readiness

Status: ready for public-safe release accounting
Date: 2026-05-21

## Scope

Wave670 texel packer continuation saved static Ghidra metadata for nine adjacent CTexture/CFastVB texel-packer rows after Wave669:

| Address | Saved name | Saved signature |
| --- | --- | --- |
| `0x00583c8e` | `CTexture__PackTexels_Dither_Bits8_8` | `void __thiscall CTexture__PackTexels_Dither_Bits8_8(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x00583d89` | `CTexture__PackTexels_Dither_Bits5_5_5` | `void __thiscall CTexture__PackTexels_Dither_Bits5_5_5(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x00583eb3` | `CTexture__PackTexels_Dither_Bits8_8_8_Alt` | `void __thiscall CTexture__PackTexels_Dither_Bits8_8_8_Alt(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x00583fe5` | `CTexture__PackTexels_Dither_Bits8_8_8_8_Alt` | `void __thiscall CTexture__PackTexels_Dither_Bits8_8_8_8_Alt(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x00584144` | `CFastVB__PackTexels_NoDither_Bits16_16` | `void __thiscall CFastVB__PackTexels_NoDither_Bits16_16(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x0058423f` | `CFastVB__PackTexels_NoDither_Bits2_10_10_10` | `void __thiscall CFastVB__PackTexels_NoDither_Bits2_10_10_10(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x0058439e` | `CFastVB__PackTexels_NoDither_Bits16_16_16_16` | `void __thiscall CFastVB__PackTexels_NoDither_Bits16_16_16_16(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x00584535` | `CTexture__PackTexels_Dither_Bits8_8_FromAuxLookup` | `void __thiscall CTexture__PackTexels_Dither_Bits8_8_FromAuxLookup(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x0058463a` | `CTexture__PackTexels_Dither_L16_Alt` | `void __thiscall CTexture__PackTexels_Dither_L16_Alt(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |

Tag anchors: `texel-packer-continuation-wave670`, `wave670-readback-verified`, `static-reaudit`, `retail-binary-evidence`, `signature-hardened`, and `comment-hardened`.

Probe anchors: `0x00583c8e CTexture__PackTexels_Dither_Bits8_8`, `0x0058463a CTexture__PackTexels_Dither_L16_Alt`, and next queue head `0x00584724 CDXTexture__PackTexels_CallbackPerTexel_RepeatA`.

## Evidence

- Dry mode: `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=9 missing=0 bad=0`
- Apply mode: `updated=9 skipped=0 renamed=0 would_rename=0 signature_updated=9 missing=0 bad=0`
- Final dry mode: `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- All three passes reported `REPORT: Save succeeded`.
- Post exports verified `9` metadata rows, `9` tag rows, `9` xref rows, `729` instruction rows, and `9` clean decompile rows.
- Backup verified: `[maintainer-local-ghidra-backup-root]\BEA_20260521-033410_post_wave670_texel_packer_continuation_verified`, `19` files, `163842951` bytes, `DiffCount=0`.

## Observations

- All nine rows share the saved callback shape `void __thiscall <name>(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)`.
- The CTexture dither rows use the observed output pointer fields `+0x1058/+0x105c/+0x20`, count `+0x1060`, dither table `+0x34`, optional domain conversion `+0x1050`, and optional normalization `+0x10`.
- The three CFastVB rows are currently named `NoDither_*`, but the current decompile still reads the shared dither-table term at `+0x34` before rounding.
- `0x00584535 CTexture__PackTexels_Dither_Bits8_8_FromAuxLookup` calls the observed indirect helper `0x00575d99` before writing two local float lanes.
- `0x0058463a CTexture__PackTexels_Dither_L16_Alt` uses weighted RGB constants at `0x005e72dc/0x005e72e0/0x005e72e4`.

## Queue

Post-Wave670 queue telemetry:

- Total functions: `6098`
- Commented functions: `3722`
- Commentless functions: `2376`
- Exact-undefined signatures: `1217`
- `param_N` signatures: `595`
- Comment-backed proxy: `3722/6098 = 61.04%`
- Strict clean-signature proxy: `3672/6098 = 60.22%`
- Next queue head: `0x00584724 CDXTexture__PackTexels_CallbackPerTexel_RepeatA`

## Boundaries

This is static metadata evidence only. Exact dither table provenance, exact no-dither naming rationale, exact texel-pack callback ABI, channel-order enum contracts, indirect helper target, auxiliary lookup contract, luminance contract, runtime texture output behavior, BEA patching, and rebuild parity remain unproven.
