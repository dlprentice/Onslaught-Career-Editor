# Ghidra CRT Small-Block Heap Wave634

Status: read-back verified
Date: 2026-05-20

Wave634 hardened sixteen adjacent CRT heap bootstrap, small-block heap, and deferred region-pool rows in the saved Ghidra project:

- `0x00566294 CRT__InitializeHeapSubsystem`
- `0x005662f1 CRT__InitSmallBlockHeap`
- `0x00566339 CRT__FindSmallBlockHeapEntryForPtr`
- `0x00566364 CRT__SmallBlockHeapFreeBlock`
- `0x0056668d CRT__SbHeapAllocBlock`
- `0x00566996 CRT__SbHeapGrowRegionTable`
- `0x00566a47 CRT__SbHeapCommitRegion`
- `0x00566b42 CRT__SmallBlockHeapReallocInPlace`
- `0x00566e38 CRT__SbHeapCreateRegionPool`
- `0x00566f7c CRT__SmallBlockHeapReleaseRegion`
- `0x00566fd2 CRT__SmallBlockHeapDecommitPages`
- `0x00567094 CRT__SmallBlockHeapLocateBlock`
- `0x005670eb CRT__SbHeapReleasePageBlock`
- `0x00567130 CRT__SbHeapAllocDeferredBlock`
- `0x00567338 CRT__SbHeapAllocChunkFromRegion`
- `0x0056745c CRT__SbHeapResizeChunkInRegion`

The pass corrected `CRT__SbHeapAllocChunkFromRegion_00567338` to `CRT__SbHeapAllocChunkFromRegion`, corrected `CRT__SbHeapResizeChunkInRegion_0056745c` to `CRT__SbHeapResizeChunkInRegion`, saved signatures/comments/tags for all sixteen rows, and made no function-boundary or executable-byte changes.

## Evidence

- Dry run: `updated=0 skipped=16 renamed=0 would_rename=2 signature_updated=0 varargs=0 missing=0 bad=0`
- Apply: `updated=16 skipped=0 renamed=2 would_rename=0 signature_updated=16 varargs=0 missing=0 bad=0`
- Final dry: `updated=0 skipped=16 renamed=0 would_rename=0 signature_updated=0 varargs=0 missing=0 bad=0`
- Post exports: `16` metadata rows, `16` tag rows, `31` xref rows, `1168` instruction rows, `16` decompile rows
- Queue refresh: `6093` total, `3370` commented, `2723` commentless, `1217` exact-undefined signatures, `926` `param_N` signatures
- Strict clean-signature proxy: `3316/6093 = 54.43%`
- Verified backup: `G:\GhidraBackups\BEA_20260520-104156_post_wave634_crt_small_block_heap_verified` (`19` files, `162401159` bytes, `DiffCount=0`)

The next high-signal queue head is `0x00567505 CRT__WriteFdTextMode_Locking_00567505`.

## Limits

This is static saved-Ghidra evidence only. Exact MSVC CRT version, exact small-block heap region-table/page-record/chunk layouts, heap strategy enum names, runtime heap allocation/free/realloc/decommit behavior, BEA patching, and rebuild parity remain unproven.
