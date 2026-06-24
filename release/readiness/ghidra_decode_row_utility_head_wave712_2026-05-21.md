# Ghidra Decode Row Utility Head Wave712 Readiness

Status: passed
Date: 2026-05-21

Wave712 decode row utility head saved eleven adjacent CTexture/CDXTexture/CFastVB row utility and decode helper rows with the `decode-row-utility-head-wave712` and `wave712-readback-verified` tags. The pass changed Ghidra metadata only: comments, tags, and signatures for nine visible-ABI helpers; comments and tags only for two hidden-ABI row walkers. It made no renames, no function-boundary changes, and no executable-byte changes.

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x0059c070 CTexture__ProcessRowBatchesLinearStride` | `void __stdcall CTexture__ProcessRowBatchesLinearStride(int param_1, int param_2)` | Comment/tag-only by design; `RET 0x8`, hidden `unaff_ESI` row-batch descriptor, linear row pointers, and callback slots `[0xc]` / `[0xd]`. |
| `0x0059c110 CTexture__ProcessRowBatchesMcuStride128` | `void __stdcall CTexture__ProcessRowBatchesMcuStride128(int param_1, int param_2)` | Comment/tag-only by design; `RET 0x8`, hidden `unaff_ESI` row-batch descriptor, 0x80 byte-offset scaling, and callback slots `[0xc]` / `[0xd]`. |
| `0x0059c630 CTexture__AllocJpegQuantTableDescriptor` | `void __stdcall CTexture__AllocJpegQuantTableDescriptor(void * decode_state)` | `RET 0x4`, JPEG quant-table callers, 0x84-byte descriptor allocation through `decode_state +4`, store to `+0x20`, and clear `descriptor +0x80`. |
| `0x0059c650 CTexture__AllocJpegHuffmanTableDescriptor` | `void __stdcall CTexture__AllocJpegHuffmanTableDescriptor(void * decode_state)` | `RET 0x4`, JPEG Huffman-table callers, 0x118-byte descriptor allocation through `decode_state +4`, store to `+0x24`, and clear `descriptor +0x114`. |
| `0x0059c670 CDXTexture__CeilDiv` | `int __stdcall CDXTexture__CeilDiv(int value, int divisor)` | `RET 0x8`, JPEG/decode geometry callers, and `(value + divisor - 1) / divisor` helper shape. |
| `0x0059c690 CDXTexture__AlignUpToMultiple` | `int __stdcall CDXTexture__AlignUpToMultiple(int value, int multiple)` | `RET 0x8`, workspace/resource callers, and align-up by subtracting the remainder from `value + multiple - 1`. |
| `0x0059c6b0 CTexture__CopyRowsFromPointerTable` | `void __stdcall CTexture__CopyRowsFromPointerTable(void * src_row_table, int src_row_index, void * dst_row_table, int dst_row_index, int row_count, uint bytes_per_row)` | `RET 0x18`, source/destination row pointer tables, row count, and dword-plus-tail row copy. |
| `0x0059c700 CFastVB__CopyBlockRows128Bytes` | `void __stdcall CFastVB__CopyBlockRows128Bytes(void * src, void * dst, int block_row_count)` | `RET 0xc`, caller at `0x005ac57f`, and copy of `block_row_count << 7` bytes from source to destination. |
| `0x0059c730 CDXTexture__ZeroBufferBytes` | `void __stdcall CDXTexture__ZeroBufferBytes(void * buffer, uint byte_count)` | `RET 0x8`, row/decode callers, and dword-plus-tail zero fill. |
| `0x0059c750 CDXTexture__BeginAsyncDecodeJob` | `int __stdcall CDXTexture__BeginAsyncDecodeJob(void * decode_job)` | `RET 0x4`, null input returns `-2`, job/state field clears, async status seed, and `CDXTexture__ResetDecodeWindowState` call. |
| `0x0059c78f CDXTexture__FinishAsyncDecodeJob` | `int __stdcall CDXTexture__FinishAsyncDecodeJob(void * decode_job)` | `RET 0x4`, null input/callback returns `-2`, async handle closes, completion callback invocation, and decode-state pointer clear. |

Evidence:

- Candidate exports before mutation covered 11 metadata rows, 11 tag rows, 57 xref rows, 2651 instruction rows, and 11 decompile rows.
- Selected pre exports covered 11 metadata rows, 11 tag rows, 57 xref rows, 2651 instruction rows, and 11 decompile rows.
- Dry/apply/final dry summaries: `updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=9 comment_only_updated=2 missing=0 bad=0`; `updated=11 skipped=0 renamed=0 would_rename=0 signature_updated=9 comment_only_updated=2 missing=0 bad=0`; `updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports covered 11 metadata rows, 11 tag rows, 57 xref rows, 2651 instruction rows, and 11 decompile rows.
- Queue after Wave712: 6098 total, 4143 commented, 1955 commentless, 1216 exact-undefined signatures, 194 `param_N`, comment-backed proxy `4143/6098 = 67.94%`, and strict clean-signature proxy `4087/6098 = 67.02%`.
- Queue heads after Wave712: raw commentless head `0x0042f220 CSPtrSet__Clear`; high-signal head `0x0059c7cc CDXTexture__InflateInitStateFromHeader`.
- Verified backup: `G:\GhidraBackups\BEA_20260521-232045_post_wave712_decode_row_utility_head_verified`, 19 files, 165874567 bytes, `DiffCount=0`.

Boundary:

This is static Ghidra metadata/read-back evidence only. The two row-batch walkers intentionally retain `param_1`/`param_2` and visible `unaff_ESI` in post decompile because their hidden-register ABI is not solved. Exact row-batch descriptor layout, callback ABI, descriptor schemas, allocator contract, async job/state layout, runtime JPEG/PNG/decode behavior, runtime texture behavior, BEA patching, source identity, and rebuild parity remain unproven.

Probe anchors: `Wave712 decode row utility head`, `decode-row-utility-head-wave712`, `0x0059c070 CTexture__ProcessRowBatchesLinearStride`, `0x0059c78f CDXTexture__FinishAsyncDecodeJob`, `0x0059c110 CTexture__ProcessRowBatchesMcuStride128`, `0x0059c7cc CDXTexture__InflateInitStateFromHeader`, `0x0042f220 CSPtrSet__Clear`, `G:\GhidraBackups\BEA_20260521-232045_post_wave712_decode_row_utility_head_verified`.
