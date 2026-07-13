# Ghidra Inflate Utility Head Wave731 Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x005b1e16` comment correction; `0x005b2860` comment correction. The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: passed
Date: 2026-05-22

Wave731 inflate utility head saved five adjacent CDXTexture inflate utility rows with the `inflate-utility-head-wave731` and `wave731-readback-verified` tags. The pass hardened five visible signatures/parameter names, corrected `CDXTexture__InflateProcessBlockHeader` to an `int` status return from caller EAX use, and made no renames, no function-boundary changes, and no executable-byte changes.

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x005b1e16 CDXTexture__InflateBuildFixedHuffmanTables` | `void * __stdcall CDXTexture__InflateBuildFixedHuffmanTables(void * inflate_stream, void * state_callback, uint window_size_bytes)` | RET `0xc` caller `CDXTexture__InflateInitStateFromHeader` passes inflate stream, state callback, and window size; the helper allocates a `0x40`-byte state, a `0x5a0`-byte fixed Huffman table, and a window buffer, then returns the state pointer or null. |
| `0x005b1e94 CDXTexture__InflateProcessBlockHeader` | `int __stdcall CDXTexture__InflateProcessBlockHeader(void * inflate_state, void * inflate_stream, int status_code)` | RET `0xc` caller `CDXTexture__InflateStream_ProcessZlibState` passes inflate state, stream, and status/flush code, then consumes EAX as a zlib-style status. The helper walks stored, fixed-Huffman, and dynamic-Huffman block paths and writes stream error strings including `invalid block type` and `too many length or distance symbols`. |
| `0x005b25e0 CDXTexture__CloseAsyncDecodeHandles` | `int __stdcall CDXTexture__CloseAsyncDecodeHandles(void * inflate_state, void * inflate_stream)` | RET `0x8` caller `CDXTexture__FinishAsyncDecodeJob` passes inflate state and stream; the helper resets window state, frees the window buffer, frees the table/state allocations through stream callbacks, and returns `0`. |
| `0x005b2613 CDXTexture__Adler32_Update` | `uint __stdcall CDXTexture__Adler32_Update(uint adler, void * source_buffer, uint byte_count)` | RET `0xc` helper updates Adler-32 over chunks capped at `0x15b0` bytes, reduces both accumulators modulo `0xfff1`, returns the packed checksum, and returns initial checksum `1` for a null source. |
| `0x005b272e CDXTexture__InflateDefaultAllocCallback` | `void * __stdcall CDXTexture__InflateDefaultAllocCallback(void * opaque, uint item_count, uint item_size)` | RET `0xc` helper ignores opaque, multiplies item count by item size, calls `GetProcessHeap`, allocates with `HeapAlloc` flag `8`, and returns the allocated pointer in EAX. |

Validation evidence:

- Dry/apply/final dry reported `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=5 missing=0 bad=0`, then `updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=5 missing=0 bad=0`, then `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post exports verified `5` metadata rows, `5` tag rows, `6` xref rows, `2705` instruction rows, and `5` decompile rows; caller context exports verified `3` decompile rows and `1143` caller instruction rows.
- Queue refresh passed with `6098` total functions, `4301` commented, `1797` commentless, `1216` exact-undefined signatures, `76` `param_N` signatures, comment-backed proxy `4301/6098 = 70.53%`, and strict clean-signature proxy `4243/6098 = 69.58%`.
- Earliest raw commentless row is `0x0042f220 CSPtrSet__Clear`; next commentless high-signal row is `0x005b2860 CDXTexture__InitJpegEncoderComponentBuffers`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-092519_post_wave731_inflate_utility_head_verified`, `19` files, `166726535` bytes, `DiffCount=0`.

Scope boundary: this wave proves saved static retail Ghidra metadata only. Exact z_stream layout, inflate-state layout, callback ABI, downstream helper ABIs, allocator ownership and lifetime, block enum names, checksum source identity, runtime inflate behavior, runtime decode behavior, runtime heap behavior, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave731 inflate utility head`, `inflate-utility-head-wave731`, `0x005b1e16 CDXTexture__InflateBuildFixedHuffmanTables`, `0x005b1e94 CDXTexture__InflateProcessBlockHeader`, `0x005b25e0 CDXTexture__CloseAsyncDecodeHandles`, `0x005b2613 CDXTexture__Adler32_Update`, `0x005b272e CDXTexture__InflateDefaultAllocCallback`, `0x005b2860 CDXTexture__InitJpegEncoderComponentBuffers`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-092519_post_wave731_inflate_utility_head_verified`.
