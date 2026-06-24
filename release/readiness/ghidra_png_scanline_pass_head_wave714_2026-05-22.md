# Ghidra PNG Scanline / Pass Head Wave714 Readiness Note

Date: 2026-05-22
Status: public-safe static RE evidence

## Scope

Wave714 PNG scanline / pass head saved comments, tags, and signatures for five adjacent CDXTexture PNG scanline/pass rows. Tag anchors are `png-scanline-pass-head-wave714` and `wave714-readback-verified`.

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x0059ce20 CDXTexture__ExpandPackedPixelsToScanline` | `void __stdcall CDXTexture__ExpandPackedPixelsToScanline(void * png_decode_state, void * output_scanline, uint pass_pixel_mask)` | `RET 0xc`, row-decoder xrefs, full-mask copy path, and 1/2/4-bit or byte-aligned packed-pixel expansion into optional workspaces. |
| `0x0059d036 CDXTexture__ExpandAdam7PassRowInPlace` | `void __stdcall CDXTexture__ExpandAdam7PassRowInPlace(void * row_layout_descriptor, void * row_buffer, int adam7_pass_index)` | `RET 0xc`, null guards, `DAT_005f39d8` pass-width table use, backward in-place row expansion, and descriptor width/byte-count updates. |
| `0x0059d301 CDXTexture__ApplyPngScanlineFilter` | `void __stdcall CDXTexture__ApplyPngScanlineFilter(void * png_decode_state, void * row_layout_descriptor, void * current_scanline, void * previous_scanline, int filter_type)` | `RET 0x14`, row-layout byte count and pixel-byte stride use, filter types 1..4 matching Sub/Up/Average/Paeth-style predictors, and warning/clear path for unknown filters. |
| `0x0059d47a CDXTexture__InitPngImageBuffersAndPassGeometry` | `void __stdcall CDXTexture__InitPngImageBuffersAndPassGeometry(void * png_decode_state)` | `RET 0x4`, post-decode transform application, normal/Adam7 row geometry and output bit-width computation, row-buffer allocation, previous-row clear, and initialization flag set. |
| `0x0059d614 CDXTexture__FinalizePngChunkAndVerifyCrc` | `int __stdcall CDXTexture__FinalizePngChunkAndVerifyCrc(void * png_decode_state, uint remaining_chunk_bytes)` | `RET 0x8`, remaining chunk payload drain, CRC helper call, `"CRC error"` log/warn paths, and nonzero invalid-CRC status. The post decompile still has the expected `extraout_var` artifact from the upstream bool-return CRC helper. |

## Evidence

Candidate exports verified `5` metadata rows, `5` tag rows, `22` xref rows, `185` instruction rows, and `5` decompile rows. Selected pre exports verified the same counts.

Ghidra dry/apply/final-dry read-back:

- Dry: `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=5 comment_only_updated=0 missing=0 bad=0`.
- Apply: `updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=5 comment_only_updated=0 missing=0 bad=0`.
- Final dry: `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.

Post exports verified `5` metadata rows, `5` tag rows, `22` xref rows, `185` instruction rows, and `5` decompile rows. All five targets were signature-hardened. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Post-Wave714 queue telemetry:

- `6098` total functions.
- `4159` commented functions.
- `1939` commentless functions.
- `1216` exact-undefined signatures.
- `178` `param_N` signatures.
- Comment-backed proxy: `4159/6098 = 68.20%`.
- Strict clean-signature proxy: `4103/6098 = 67.28%`.
- Raw commentless head: `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal head: `0x0059d699 CDXTexture__ParsePngChunk_IHDR`.

Verified backup: `G:\GhidraBackups\BEA_20260522-002212_post_wave714_png_scanline_pass_head_verified`, `19` files, `165972871` bytes, `DiffCount=0`.

## Boundaries

This note proves saved static retail Ghidra metadata only. Exact PNG decode-state layout, row-layout descriptor schema, Adam7 table/mask semantics, chunk/CRC flag enum, row-workspace/buffer ownership, source-read bounds, warning/error policy, runtime PNG behavior, runtime decode/image fidelity, BEA patching, and rebuild parity remain unproven. The `0x0059d614 CDXTexture__FinalizePngChunkAndVerifyCrc` post decompile intentionally retains the documented `extraout_var` artifact from the upstream bool-return helper.

Probe anchors: `Wave714 PNG scanline / pass head`, `png-scanline-pass-head-wave714`, `0x0059ce20 CDXTexture__ExpandPackedPixelsToScanline`, `0x0059d614 CDXTexture__FinalizePngChunkAndVerifyCrc`, `extraout_var`, `0x0059d699 CDXTexture__ParsePngChunk_IHDR`, `0x0042f220 CSPtrSet__Clear`, `G:\GhidraBackups\BEA_20260522-002212_post_wave714_png_scanline_pass_head_verified`.
