# Ghidra Texel Callback/Raw Packers Wave671 Readiness

Status: ready for public-safe release accounting
Date: 2026-05-21

## Scope

Wave671 texel callback/raw packers saved static Ghidra metadata for eight adjacent CDXTexture/CTexture texel-packer rows after Wave670:

| Address | Saved name | Saved signature |
| --- | --- | --- |
| `0x00584724` | `CDXTexture__PackTexels_CallbackPerTexel_RepeatA` | `void __thiscall CDXTexture__PackTexels_CallbackPerTexel_RepeatA(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x00584786` | `CDXTexture__PackTexels_CallbackPerTexel_RepeatB` | `void __thiscall CDXTexture__PackTexels_CallbackPerTexel_RepeatB(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x005847e9` | `CDXTexture__PackTexels_CallbackPerTexel_Once` | `void __thiscall CDXTexture__PackTexels_CallbackPerTexel_Once(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x00584831` | `CDXTexture__PackTexels_CopyRaw32` | `void __thiscall CDXTexture__PackTexels_CopyRaw32(void * this, uint output_x, uint output_y, void * source_texel_records, int unused_context)` |
| `0x00584886` | `CDXTexture__PackTexels_CopyRaw64` | `void __thiscall CDXTexture__PackTexels_CopyRaw64(void * this, uint output_x, uint output_y, void * source_texel_records, int unused_context)` |
| `0x005848e3` | `CDXTexture__PackTexels_CopyRaw128` | `void __thiscall CDXTexture__PackTexels_CopyRaw128(void * this, uint output_x, uint output_y, void * source_texel_records, int unused_context)` |
| `0x00584936` | `CDXTexture__PackTexels_NoDither_A16L16` | `void __thiscall CDXTexture__PackTexels_NoDither_A16L16(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |
| `0x00584a4c` | `CTexture__PackTexels_NoDither_Bits16_16_16` | `void __thiscall CTexture__PackTexels_NoDither_Bits16_16_16(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` |

Tag anchors: `texel-callback-raw-packers-wave671`, `wave671-readback-verified`, `static-reaudit`, `retail-binary-evidence`, `signature-hardened`, and `comment-hardened`.

Probe anchors: `0x00584724 CDXTexture__PackTexels_CallbackPerTexel_RepeatA`, `0x00584a4c CTexture__PackTexels_NoDither_Bits16_16_16`, and next queue head `0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4`.

## Evidence

- Dry mode: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=8 missing=0 bad=0`
- Apply mode: `updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=8 missing=0 bad=0`
- Final dry mode: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- All three passes reported `REPORT: Save succeeded`.
- Post exports verified `8` metadata rows, `8` tag rows, `9` xref rows, `840` instruction rows, and `8` clean decompile rows.
- Backup verified: `[maintainer-local-ghidra-backup-root]\BEA_20260521-035844_post_wave671_texel_callback_raw_packers_verified`, `19` files, `163875719` bytes, `DiffCount=0`.

## Observations

- The three callback-dispatch wrappers compute the observed output pointer from `+0x1058/+0x105c/+0x20`, use count `+0x1060`, and call observed helper `0x005759c3`.
- `0x00584724` uses mode selector `1`; `0x00584786` uses selector `2`; `0x005847e9` makes one helper call with byte count `count*4`.
- The raw-copy packers copy the first `4`, first `8`, or full `16` bytes from each observed 16-byte source record into the texture output stream.
- `0x00584936 CDXTexture__PackTexels_NoDither_A16L16` is currently named no-dither, but the current decompile still reads the shared `+0x34` dither-table term before writing an A16L16-style dword.
- `0x00584a4c CTexture__PackTexels_NoDither_Bits16_16_16` is currently named no-dither, but the current decompile still reads the shared `+0x34` dither-table term before writing three 16-bit words from observed source lanes `+8`, `+4`, and `+0`.

## Queue

Post-Wave671 queue telemetry:

- Total functions: `6098`
- Commented functions: `3730`
- Commentless functions: `2368`
- Exact-undefined signatures: `1217`
- `param_N` signatures: `587`
- Comment-backed proxy: `3730/6098 = 61.17%`
- Strict clean-signature proxy: `3680/6098 = 60.35%`
- Next queue head: `0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4`

## Boundaries

This is static metadata evidence only. Exact callback ABI, selector contract, byte-count contract, source-record contract, exact no-dither naming rationale, luminance/alpha contract, lane-order contract, runtime texture output behavior, BEA patching, and rebuild parity remain unproven.
