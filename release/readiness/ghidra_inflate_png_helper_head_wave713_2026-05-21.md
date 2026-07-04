# Ghidra Inflate / PNG Helper Head Wave713 Readiness Note

Date: 2026-05-21
Status: public-safe static RE evidence

## Scope

Wave713 inflate / PNG helper head saved comments, tags, and signatures for eleven adjacent CDXTexture inflate/PNG helper rows. Tag anchors are `inflate-png-helper-head-wave713` and `wave713-readback-verified`.

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x0059c7cc CDXTexture__InflateInitStateFromHeader` | `int __stdcall CDXTexture__InflateInitStateFromHeader(void * inflate_stream, int window_bits, void * version_text, int stream_struct_size)` | `RET 0x10`, zlib-style stream/window/version/0x38-size inputs, default callbacks, 0x18 internal-state allocation, window bits 8..15, and fixed Huffman-table setup. |
| `0x0059c8ab CDXTexture__InflateInit_WindowBits15` | `int __stdcall CDXTexture__InflateInit_WindowBits15(void * inflate_stream, void * version_text, int stream_struct_size)` | `RET 0xc` wrapper into the header initializer with fixed window bits 15. |
| `0x0059c8c1 CDXTexture__InflateStream_ProcessZlibState` | `int __stdcall CDXTexture__InflateStream_ProcessZlibState(void * inflate_stream, int flush_mode)` | `RET 0x8`, PNG IDAT/pass-row xrefs, zlib CMF/FLG/data-check/block-processing state-machine shape, and zlib-style status returns. The saved comment and tag record the remaining `extraout_EAX` gap from a downstream block-header helper. |
| `0x0059cc24 CDXTexture__AllocZeroedDecodeState` | `void * __stdcall CDXTexture__AllocZeroedDecodeState(int state_class)` | `RET 0x4`, decode-state class 1 as 0x19c bytes, class 2 as 0x40 bytes, malloc, and zero-init loop. |
| `0x0059cc68 CDXTexture__FreeDecodeState` | `void __stdcall CDXTexture__FreeDecodeState(void * decode_state)` | `RET 0x4`, non-null decode-state free through `CRT__FreeBase`, and PNG context cleanup xrefs. |
| `0x0059cc7c CDXTexture__AllocOrThrow` | `void * __stdcall CDXTexture__AllocOrThrow(void * png_decode_state, uint byte_count)` | `RET 0x8`, null/zero guards, malloc of `byte_count`, and decode-error throw on allocation failure. |
| `0x0059ccf3 CDXTexture__MemsetByte` | `void * __stdcall CDXTexture__MemsetByte(void * unused_context, void * destination_buffer, int fill_byte, uint byte_count)` | `RET 0x10`, dword-plus-tail byte fill, destination return, and intentionally unused context argument. |
| `0x0059cd26 CDXTexture__ReadU32BigEndian` | `uint __stdcall CDXTexture__ReadU32BigEndian(void * source_buffer)` | `RET 0x4`, four-byte big-endian uint32 reader used by PNG header, CRC, IHDR, gAMA, IDAT, and pass-row callers. |
| `0x0059cd4b CDXTexture__ReadChunkBytesAndUpdateCrc` | `void __stdcall CDXTexture__ReadChunkBytesAndUpdateCrc(void * png_decode_state, void * destination_buffer, uint byte_count)` | `RET 0xc`, source read into destination, then running chunk CRC update over the same span. |
| `0x0059cd62 CDXTexture__IsPngChunkCrcInvalid` | `bool __stdcall CDXTexture__IsPngChunkCrcInvalid(void * png_decode_state)` | `RET 0x4`, stored CRC read, conditional comparison with running CRC at decode-state `+0x100`, and invalid-CRC boolean return. |
| `0x0059cdbe CDXTexture__ValidateChunkTagAsciiOrLog` | `void __stdcall CDXTexture__ValidateChunkTagAsciiOrLog(void * png_decode_state, void * chunk_type_bytes)` | `RET 0x8`, four-byte chunk-tag ASCII range validation, and `"invalid chunk type"` diagnostic path. |

## Evidence

Candidate exports verified `11` metadata rows, `11` tag rows, `44` xref rows, `2871` instruction rows, and `11` decompile rows. Selected pre exports verified the same counts.

Ghidra dry/apply/final-dry read-back:

- Dry: `updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=11 comment_only_updated=0 missing=0 bad=0`.
- Apply: `updated=11 skipped=0 renamed=0 would_rename=0 signature_updated=11 comment_only_updated=0 missing=0 bad=0`.
- Final dry: `updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.

Post exports verified `11` metadata rows, `11` tag rows, `44` xref rows, `2871` instruction rows, and `11` decompile rows. All eleven targets were signature-hardened. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Post-Wave713 queue telemetry:

- `6098` total functions.
- `4154` commented functions.
- `1944` commentless functions.
- `1216` exact-undefined signatures.
- `183` `param_N` signatures.
- Comment-backed proxy: `4154/6098 = 68.12%`.
- Strict clean-signature proxy: `4098/6098 = 67.20%`.
- Raw commentless head: `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal head: `0x0059ce20 CDXTexture__ExpandPackedPixelsToScanline`.

Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-234937_post_wave713_inflate_png_helper_head_verified`, `19` files, `165972871` bytes, `DiffCount=0`.

## Boundaries

This note proves saved static retail Ghidra metadata only. Exact `z_stream`/inflate-state layout, callback ABI, zlib source identity, downstream block-header helper return ABI, PNG decode-state layout, chunk/CRC flags, allocator ownership, runtime inflate behavior, runtime PNG behavior, runtime decode/image fidelity, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave713 inflate / PNG helper head`, `inflate-png-helper-head-wave713`, `0x0059c7cc CDXTexture__InflateInitStateFromHeader`, `0x0059cdbe CDXTexture__ValidateChunkTagAsciiOrLog`, `0x0059c8c1 CDXTexture__InflateStream_ProcessZlibState`, `extraout_EAX`, `0x0059ce20 CDXTexture__ExpandPackedPixelsToScanline`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260521-234937_post_wave713_inflate_png_helper_head_verified`.
