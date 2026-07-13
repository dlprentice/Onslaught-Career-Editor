# Ghidra Decode Allocator Head Wave711 Readiness

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x0059be00` comment correction. The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: passed
Date: 2026-05-21

Wave711 decode allocator head saved seven adjacent CTexture/CDXTexture decode allocator rows with the `decode-allocator-head-wave711` and `wave711-readback-verified` tags. The pass changed Ghidra metadata only: comments, tags, and signatures. It made no renames, no function-boundary changes, and no executable-byte changes.

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x0059bae0 CDXTexture__AllocFromBank_SplitBlock` | `int __stdcall CDXTexture__AllocFromBank_SplitBlock(void * allocator_owner, int bank_index, uint requested_size_bytes)` | `RET 0xc`, split-block free-list search at allocator state `+0x34`, 8-byte alignment, and 0x10-byte block-header payload return. |
| `0x0059bc10 CDXTexture__AllocLinearBlockAndTrack` | `int __stdcall CDXTexture__AllocLinearBlockAndTrack(void * allocator_owner, int bank_index, uint requested_size_bytes)` | `RET 0xc`, linear tracked-list insertion at allocator state `+0x3c`, byte accounting at `+0x4c`, and 0x10-byte block-header payload return. |
| `0x0059bcc0 CDXTexture__AllocRowPointerTableAndRows` | `int __stdcall CDXTexture__AllocRowPointerTableAndRows(void * allocator_owner, int bank_index, uint row_stride_bytes, uint row_count)` | `RET 0x10`, row-stride product cap, split-block pointer-table allocation, linear row-batch allocation, and row pointer table fill. |
| `0x0059bd60 CDXTexture__AllocMcuRowPointerTableAndRows` | `int __stdcall CDXTexture__AllocMcuRowPointerTableAndRows(void * allocator_owner, int bank_index, int mcu_units_per_row, uint row_count)` | `RET 0x10`, `mcu_units_per_row*0x80` row stride, split-block pointer-table allocation, linear row-batch allocation, and row pointer table fill. |
| `0x0059c3f0 CDXTexture__ReleaseDecodeBankLists` | `void __stdcall CDXTexture__ReleaseDecodeBankLists(void * allocator_owner, int bank_index)` | `RET 0x8`, bank 0/1 validation, bank-1 descriptor callback cleanup, and split/linear tracked-list drains. |
| `0x0059c510 CDXTexture__InitDecodeAllocatorVtable` | `void __stdcall CDXTexture__InitDecodeAllocatorVtable(void * allocator_owner)` | `RET 0x4`, 0x54-byte allocator-state allocation, decode allocator vtable slot installation, default budget storage, and bank-list initialization. |
| `0x0059c5d0 CDXTexture__PumpDecodeAllocatorAndSetStage` | `void __stdcall CDXTexture__PumpDecodeAllocatorAndSetStage(void * decode_state)` | `RET 0x4`, allocator vtable slot `+0x24` release of bank 1, and decode stage writes to `+0x14`. |

Evidence:

- Candidate exports before mutation covered 11 metadata rows, 11 tag rows, 25 xref rows, 407 instruction rows, and 11 decompile rows.
- Deferred read-only hidden-ABI candidates: `0x0059be00 CDXTexture__CreateDecodeJobDescriptor` (`in_stack_`), `0x0059be70 CDXTexture__AllocDecodeBlockAndLink` (`in_stack_`), `0x0059c070 CTexture__ProcessRowBatchesLinearStride` (`unaff_ESI`), and `0x0059c110 CTexture__ProcessRowBatchesMcuStride128` (`unaff_ESI`).
- Selected pre exports covered 7 metadata rows, 7 tag rows, 19 xref rows, 1687 instruction rows, and 7 decompile rows.
- Dry/apply/final dry summaries: `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=7 missing=0 bad=0`; `updated=7 skipped=0 renamed=0 would_rename=0 signature_updated=7 missing=0 bad=0`; `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`.
- Post exports covered 7 metadata rows, 7 tag rows, 19 xref rows, 1687 instruction rows, and 7 decompile rows.
- Queue after Wave711: 6098 total, 4132 commented, 1966 commentless, 1216 exact-undefined signatures, 203 `param_N`, comment-backed proxy `4132/6098 = 67.76%`, and strict clean-signature proxy `4078/6098 = 66.87%`.
- Queue heads after Wave711: raw commentless head `0x0042f220 CSPtrSet__Clear`; high-signal head `0x0059c070 CTexture__ProcessRowBatchesLinearStride`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-225104_post_wave711_decode_allocator_head_verified`, 19 files, 165776263 bytes, `DiffCount=0`.
- Process note: one selected pre-metadata export captured a normal Ghidra analyzer pass before export because that first command omitted `-noanalysis`; all later selected dry/apply/final/post/queue runs used `-noanalysis`, and the saved final state is covered by post exports, queue refresh, and verified backup.

Boundary:

This is static Ghidra metadata/read-back evidence only. Exact allocator-state layout, exact decode-state layout, helper return ABI, descriptor callback contract, row-batch hidden-register ABI, runtime texture behavior, runtime image decode behavior, BEA patching, source identity, and rebuild parity remain unproven. The selected allocator helpers still document the `CDXTexture__AllocAligned16` `extraout_EAX` decompiler artifact where present, and `0x0059c510` still has a stale no-op helper label on the null path.

Probe anchors: `Wave711 decode allocator head`, `decode-allocator-head-wave711`, `0x0059bae0 CDXTexture__AllocFromBank_SplitBlock`, `0x0059c5d0 CDXTexture__PumpDecodeAllocatorAndSetStage`, `0x0059be00 CDXTexture__CreateDecodeJobDescriptor`, `0x0059be70 CDXTexture__AllocDecodeBlockAndLink`, `0x0059c070 CTexture__ProcessRowBatchesLinearStride`, `0x0059c110 CTexture__ProcessRowBatchesMcuStride128`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260521-225104_post_wave711_decode_allocator_head_verified`.
