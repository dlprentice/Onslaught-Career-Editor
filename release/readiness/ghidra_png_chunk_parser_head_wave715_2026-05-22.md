# Ghidra PNG Chunk Parser Head Wave715 Readiness Note

Date: 2026-05-22

Status: static Ghidra metadata saved and read back; no executable-byte change.

## Summary

Wave715 PNG chunk parser head saved comments, tags, names, and signatures for eight adjacent CDXTexture PNG chunk parser/IDAT rows. Tag anchors are `png-chunk-parser-head-wave715` and `wave715-readback-verified`.

The pass included two guarded renames backed by raw dispatch constants from `game/BEA.exe`: `0x005ee8e4` is `49 45 4e 44` / `IEND`, so `0x0059d992` is now `CDXTexture__ParsePngChunk_IEND`; `0x005ee904` is `74 52 4e 53` / `tRNS`, so `0x0059dbbb` is now `CDXTexture__ParsePngChunk_tRNS`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0059d699 CDXTexture__ParsePngChunk_IHDR` | `void __stdcall CDXTexture__ParsePngChunk_IHDR(void * png_decode_state, void * png_image_context, uint chunk_data_length)` | `RET 0xc`, `ParsePngHeadersUntilIdat` xref, 13-byte IHDR read, CRC finalization, dimension/bit-depth/color-type/compression/filter/interlace checks, decode-state field stores, and format descriptor finalization. |
| `0x0059d879 CDXTexture__ParsePngChunk_PLTE` | `void __stdcall CDXTexture__ParsePngChunk_PLTE(void * png_decode_state, void * png_image_context, uint chunk_data_length)` | `RET 0xc`, palette ordering checks, 3-byte palette entry allocation/read loop, decode-state palette pointer/count stores, image-context scan-parameter handoff, and indexed tRNS count clamp. |
| `0x0059d992 CDXTexture__ParsePngChunk_IEND` | `void __stdcall CDXTexture__ParsePngChunk_IEND(void * png_decode_state, void * png_image_context, uint chunk_data_length)` | `RET 0xc`, `IEND` dispatch constant bytes `49 45 4e 44`, prior IHDR/IDAT state requirement, terminal flag mark, nonzero-length warning, and CRC finalization. |
| `0x0059d9d8 CDXTexture__ParsePngChunk_gAMA` | `void __stdcall CDXTexture__ParsePngChunk_gAMA(void * png_decode_state, void * png_image_context, uint chunk_data_length)` | `RET 0xc`, `gAMA` ordering/duplicate policy, 4-byte big-endian gamma read, CRC-before-apply flow, sRGB/gAMA consistency warning, decode-state gamma float store, and image-context option handoff. |
| `0x0059dad9 CDXTexture__ParsePngChunk_sRGB` | `void __stdcall CDXTexture__ParsePngChunk_sRGB(void * png_decode_state, void * png_image_context, uint chunk_data_length)` | `RET 0xc`, `sRGB` ordering/duplicate policy, one-byte rendering intent read, CRC-before-apply flow, intent range check, gAMA/sRGB consistency warning, and image-context option handoff. |
| `0x0059dbbb CDXTexture__ParsePngChunk_tRNS` | `void __stdcall CDXTexture__ParsePngChunk_tRNS(void * png_decode_state, void * png_image_context, uint chunk_data_length)` | `RET 0xc`, `tRNS` dispatch constant bytes `74 52 4e 53`, indexed palette alpha allocation/read path, grayscale/RGB big-endian transparent sample handling, decode-state transparency count/parameter stores, and option handoff after CRC validation. |
| `0x0059dd5c CDXTexture__HandlePngChunkAfterIdat` | `void __stdcall CDXTexture__HandlePngChunkAfterIdat(void * png_decode_state, void * png_image_context, uint chunk_data_length)` | `RET 0xc`, fallback chunk-tag validation/logging, unknown critical chunk diagnostic, post-IDAT unknown-chunk flag mark, and payload drain through CRC finalizer. |
| `0x0059dda2 CDXTexture__ProcessIdatChunkDataAndQueueDecode` | `void __stdcall CDXTexture__ProcessIdatChunkDataAndQueueDecode(void * png_decode_state)` | `RET 0x4`, both call sites push only the decode-state stack argument, ECX is pushed/popped as scratch local storage, IDAT chunk continuation reads, zlib pump, row/pass advancement, async decode job begin, and IDAT completion flagging. |

Read-back evidence verified `8` metadata rows, `8` tag rows, `9` xref rows, `4584` post-instruction rows, and `8` post-decompile rows. Caller post-decompile verified the corrected dispatch labels (`IHDR`, `PLTE`, `IEND`, `gAMA`, `sRGB`, `tRNS`, fallback) and clean one-argument `CDXTexture__ProcessIdatChunkDataAndQueueDecode(png_decode_state_00)` calls.

Dry/apply/final dry reported:

- Dry: `updated=0 skipped=8 renamed=0 would_rename=2 signature_updated=8 comment_only_updated=0 missing=0 bad=0`.
- Apply: `updated=8 skipped=0 renamed=2 would_rename=0 signature_updated=8 comment_only_updated=0 missing=0 bad=0`.
- Final dry: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.

Post-Wave715 queue telemetry:

- `6098` total functions.
- `4167` commented.
- `1931` commentless.
- `1216` exact-undefined signatures.
- `170` `param_N` signatures.
- Comment-backed proxy: `4167/6098 = 68.33%`.
- Strict clean-signature proxy: `4111/6098 = 67.42%`.
- Delta from Wave714: `+8` commented, `-8` commentless, `0` exact-undefined, `-8` `param_N`, `+8` strict clean-signature rows.
- Raw commentless head: `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal head: `0x0059dfb2 CDXTexture__Crc32_Update`.

Verified backup: `G:\GhidraBackups\BEA_20260522-005631_post_wave715_png_chunk_parser_head_verified`, `19` files, `166038407` bytes, `DiffCount=0`.

## Boundaries

Wave715 proves static retail Ghidra metadata only. Exact PNG decode-state layout, image-context layout, chunk/flag enum, CRC/source-read bounds, gamma/sRGB/tRNS policy provenance, transparency field schema, zlib stream layout, async job contract, runtime PNG behavior, runtime decode/image fidelity, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave715 PNG chunk parser head`, `png-chunk-parser-head-wave715`, `0x0059d992 CDXTexture__ParsePngChunk_IEND`, `0x0059dbbb CDXTexture__ParsePngChunk_tRNS`, `49 45 4e 44`, `74 52 4e 53`, `CDXTexture__ProcessIdatChunkDataAndQueueDecode(png_decode_state_00)`, `0x0059dfb2 CDXTexture__Crc32_Update`, `0x0042f220 CSPtrSet__Clear`, `G:\GhidraBackups\BEA_20260522-005631_post_wave715_png_chunk_parser_head_verified`.
