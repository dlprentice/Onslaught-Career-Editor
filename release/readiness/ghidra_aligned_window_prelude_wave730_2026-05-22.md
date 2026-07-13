# Ghidra Aligned Window Prelude Wave730 Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x005b1e16` comment correction. The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: passed
Date: 2026-05-22

Wave730 aligned window prelude saved six adjacent CDXTexture aligned allocation, byte-budget, host I/O callback, default-budget, and decode-window reset rows with the `aligned-window-prelude-wave730` and `wave730-readback-verified` tags. The pass hardened six visible signatures/parameter names and made no renames, no function-boundary changes, and no executable-byte changes.

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x005b1c00 CDXTexture__AllocAligned16` | `void * __stdcall CDXTexture__AllocAligned16(void * allocator_owner, uint requested_size_bytes)` | RET `0x8` callers push allocator owner and requested size; the helper allocates `requested_size_bytes + 0x10`, returns a 16-byte-aligned payload pointer, and stores the base-pointer byte delta at `aligned_payload - 1` for the paired free callback. |
| `0x005b1c30 CDXTexture__FreeAligned16` | `void __stdcall CDXTexture__FreeAligned16(void * allocator_owner, void * aligned_payload, uint tracked_size_bytes)` | RET `0xc` callers pass allocator owner, aligned payload, and tracked byte count; the helper reads the byte delta at `aligned_payload - 1`, recovers the original malloc base pointer, and frees it through `CRT__FreeBase`. |
| `0x005b1c50 CDXTexture__GetBufferTailAvailable` | `int __stdcall CDXTexture__GetBufferTailAvailable(void * allocator_owner, int row_count_hint, int minimum_chunk_bytes, int committed_size_bytes)` | RET `0x10` caller context pushes allocator owner, row-count hint, minimum chunk bytes, and committed byte count; the helper reads allocator state at owner `+4`, uses state `+0x2c`, and returns `budget_or_cap - committed_size_bytes`. |
| `0x005b1d50 CDXTexture__InitHostIoCallbacks` | `void __stdcall CDXTexture__InitHostIoCallbacks(void * decode_context, void * host_io_callbacks, uint window_size_bytes)` | RET `0xc` caller context passes decode context, callback table, and window size; the helper opens a temporary binary stream, stores it at callback table `+0xc`, reports error code `0x3f` on failure, and installs helper entries at `0x005b1c70`, `0x005b1cd0`, and `0x005b1d30`. |
| `0x005b1da0 CDXTexture__GetDefaultDecodeBudgetBytes` | `int __cdecl CDXTexture__GetDefaultDecodeBudgetBytes(void)` | No-argument helper returns default decode allocator budget `1000000`, consumed by `CDXTexture__InitDecodeAllocatorVtable` before aligned allocation of the `0x54`-byte allocator state. |
| `0x005b1db0 CDXTexture__ResetDecodeWindowState` | `void __stdcall CDXTexture__ResetDecodeWindowState(void * inflate_state, void * host_io_state, void * previous_cookie_out)` | RET `0xc` callers include async-decode begin, fixed-Huffman setup, async handle close, and zlib stream processing; the helper snapshots the cookie, releases modes `4`/`5` and mode `6`, resets output pointers and accumulator fields, and may invoke the state callback at `+0x38`. |

Validation evidence:

- Dry/apply/final dry reported `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=6 missing=0 bad=0`, then `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=6 missing=0 bad=0`, then `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post exports verified `6` metadata rows, `6` tag rows, `15` xref rows, `3246` instruction rows, and `6` decompile rows.
- Queue refresh passed with `6098` total functions, `4296` commented, `1802` commentless, `1216` exact-undefined signatures, `81` `param_N` signatures, comment-backed proxy `4296/6098 = 70.45%`, and strict clean-signature proxy `4238/6098 = 69.50%`.
- Earliest raw commentless row is `0x0042f220 CSPtrSet__Clear`; next commentless high-signal row is `0x005b1e16 CDXTexture__InflateBuildFixedHuffmanTables`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-085034_post_wave730_aligned_window_prelude_verified`, `19` files, `166693767` bytes, `DiffCount=0`.

Scope boundary: this wave proves saved static retail Ghidra metadata only. Exact allocator-owner/state layout, row-batch schema, budget semantics, callback table layout, temp-file policy, error surface, inflate-state layout, callback ABI, mode enum, runtime texture behavior, runtime zlib/decode behavior, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave730 aligned window prelude`, `aligned-window-prelude-wave730`, `0x005b1c00 CDXTexture__AllocAligned16`, `0x005b1c30 CDXTexture__FreeAligned16`, `0x005b1c50 CDXTexture__GetBufferTailAvailable`, `0x005b1d50 CDXTexture__InitHostIoCallbacks`, `0x005b1da0 CDXTexture__GetDefaultDecodeBudgetBytes`, `0x005b1db0 CDXTexture__ResetDecodeWindowState`, `0x005b1e16 CDXTexture__InflateBuildFixedHuffmanTables`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-085034_post_wave730_aligned_window_prelude_verified`.
