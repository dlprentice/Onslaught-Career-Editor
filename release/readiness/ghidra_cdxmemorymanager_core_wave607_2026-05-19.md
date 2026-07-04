# Ghidra CDXMemoryManager Core Wave607

Status: ready
Date: 2026-05-19

## Scope

Wave607 saved signature/comment/tag hardening and owner corrections for the next memory-manager core tranche:

- `0x00548ec0 CMemoryManager__DeleteTagList_CtorUnwind`
- `0x00548f90 CDXMemoryManager__Init`
- `0x005490c0 CDXMemoryManager__Shutdown`
- `0x005490e0 CDXMemoryManager__Alloc`
- `0x005491b0 CDXMemoryManager__ReAlloc`
- `0x005492d0 CDXMemoryManager__CalcAndShowDeltas`
- `0x00549400 CMemoryManager__DeleteTagList`

The pass corrected stale landscape, OID, PolyBucket, and global wrapper labels into the `CDXMemoryManager` / `CMemoryManager` context. It used retail-binary evidence from xrefs, caller/callee instructions, decompiles, queue telemetry, and Stuart source context in `DXMemoryManager.cpp` and `MemoryManager.*`.

## What Changed

- `CMemoryManager__DeleteTagList_CtorUnwind` now records the constructor EH/unwind tag-list cleanup path. It walks `CMemoryManager::mFirstTag`, reads `CMemoryTag::mNext`, and frees tags through the memory-manager free path.
- `CDXMemoryManager__Init` now has a `uint __thiscall` signature with one stack `heap_size` argument. It initializes the default/dump/sound/thing heaps and memory-type heap routing from `CLTShell__WinMain`.
- `CDXMemoryManager__Shutdown` now records the PC retail shutdown path: clear global `mInit` at `0x009c6334`, then tail-jump to default heap shutdown.
- `CDXMemoryManager__Alloc` now replaces the stale `OID__AllocObject` label. It is the high-fan-out global allocator with `RET 0x10`, 1384 xrefs, type-heap dispatch, and OOM codes `0xcd` through `0xd0`.
- `CDXMemoryManager__ReAlloc` now replaces the stale `CPolyBucket__ReallocFromPool` label. CPolyBucket and FlexArray are callers of the global realloc helper, not owners.
- `CDXMemoryManager__CalcAndShowDeltas` now records the debug memory-delta trace over default, dump, and thing heaps.
- `CMemoryManager__DeleteTagList` now records the simple tag-list delete helper reached from memory-manager unwind metadata.

## Evidence

- Apply script: `tools/ApplyCDXMemoryManagerCoreWave607.java`
- Focused probe: `tools/ghidra_cdxmemorymanager_core_wave607_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave607-memory-landscape-00548ec0/`
- Dry/apply/final dry:
  - dry: `updated=0 skipped=7 renamed=0 would_rename=6 missing=0 bad=0`
  - apply: `updated=7 skipped=0 renamed=6 would_rename=0 missing=0 bad=0`
  - final dry: `updated=0 skipped=7 renamed=0 would_rename=0 missing=0 bad=0`
- Read-back exports verified `7` metadata rows, `7` tag rows, 1402 xref rows, 2695 instruction rows, and `7` decompile rows.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-211737_post_wave607_cdxmemorymanager_core_verified`
  - `fileCount=19`
  - `totalBytes=161418119`
  - `DiffCount=0`

## Queue Delta

Post-Wave607 queue telemetry:

- Total functions: `6093`
- Commented functions: `3116`
- Commentless functions: `2977`
- Exact-undefined signatures: `1304`
- `param_N` signatures: `1065`
- Comment-backed proxy: `3116/6093 = 51.14%`
- Strict clean-signature proxy: `3071/6093 = 50.40%`
- Next queue head: `0x0054b800 CHudComponent__RenderPassEntry`

Delta from Wave606:

- `+7` commented rows
- `-7` commentless rows
- `-1` exact-undefined signature
- `-6` `param_N` signatures

## Limits

This is static retail evidence only. Complete `CMemoryTag`/`CMemoryHeap`/`CDXMemoryManager` layouts, exact memory-type enum names, allocator statistics side effects, runtime allocation/OOM behavior, Xbox-only heap differences, BEA patching, and rebuild parity remain unproven.
