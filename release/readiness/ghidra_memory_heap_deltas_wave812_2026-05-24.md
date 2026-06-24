# Ghidra Memory Heap Deltas Wave812 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `memory-heap-deltas-wave812`

Wave812 memory heap deltas saved a one-row owner/name/signature/comment/tag correction for `0x004a25c0 CMemoryHeap__CalcAndShowDeltas` after serialized headless dry/apply/read-back. The pass replaced stale `CLTShell__ValidateAndRollHeapDeltas`, hardened `void __thiscall CMemoryHeap__CalcAndShowDeltas(void * this)`, and made no function-boundary changes or executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x004a25c0 CMemoryHeap__CalcAndShowDeltas` | Iterates `0x81` memory-type counter rows, compares current counters against last-counter arrays, uses type-name table `0x009c2dd0`, emits `DebugTrace` through format string `0x0062f6d0` (`Heap Delta: ...`), and then copies current counters into the last-counter arrays. |
| `0x005492d0 CDXMemoryManager__CalcAndShowDeltas` | Calls the corrected helper three times at callsites `0x005492e6`, `0x005492f1`, and `0x005492fc`, passing `this+0x214`, `this+0xae0`, and `this+0x13ac` for default, dump, and thing heap subobjects per Wave607/source parity. |
| `references/Onslaught/MemoryManager.cpp` | Source parity includes `CMemoryHeap::CalcAndShowDeltas`, the same heap-delta format, and copy-back from `mTypeSize`/`mTypeBlocks` to `mLastTypeSize`/`mLastTypeBlocks`. |

Read-back evidence:

- `ApplyMemoryHeapDeltasWave812.java dry`: `updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=1 missing=0 bad=0`
- `ApplyMemoryHeapDeltasWave812.java apply`: `updated=1 skipped=0 renamed=1 would_rename=1 signature_updated=1 comment_only_updated=1 missing=0 bad=0`
- `ApplyMemoryHeapDeltasWave812.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 3 xref rows, 241 instruction rows, 1 decompile row, 3 context metadata rows, and 3 context decompile rows.
- Queue after Wave812: 6098 total, 5587 commented, 511 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5587/6098 = 91.62%`, strict clean-signature proxy `5587/6098 = 91.62%`.
- Next raw commentless row: `0x004a52b0 CMesh__ClearAllUsageMarkers`.
- Commentless high-signal, signature, and name-confidence queues are empty.
- Verified backup: `G:\GhidraBackups\BEA_20260524-132640_post_wave812_memory_heap_deltas_verified`, 19 files, 171346823 bytes, `DiffCount=0`.

What this proves:

- The target function row exists in the saved Ghidra project as `0x004a25c0 CMemoryHeap__CalcAndShowDeltas`.
- The saved signature is `void __thiscall CMemoryHeap__CalcAndShowDeltas(void * this)`.
- The saved comment and tags include `memory-heap-deltas-wave812` and `wave812-readback-verified`.
- The stale CLTShell owner/name was replaced by a memory-heap owner/name based on static retail decompile/xref/string evidence and Stuart source parity.

What remains unproven:

- Exact `CMemoryHeap`/`CDXMemoryManager` layouts.
- Full memory-type enum/table identity.
- Runtime trace/delta behavior.
- BEA patching behavior.
- Rebuild parity.
