# Ghidra MemoryManager / CMemoryHeap Wave438 Correction

Status: public-safe static Ghidra evidence note
Date: 2026-05-16
Scope: saved retail `BEA.exe` Ghidra name/signature/comment/tag correction

## Summary

Wave438 corrected ten allocator-family targets from stale `CMemoryManager__*` labels to source-parity `CMemoryHeap__*` method names where static retail evidence and Stuart `MemoryManager.cpp` agree. The pass also separated `0x004a1c30` as a compiler EH cleanup helper that releases the heap mutex, not a source-level heap method body.

This is public-safe static evidence only. It does not launch or patch `BEA.exe`, does not mutate the installed Steam game, and does not include raw decompile text or private runtime proof.

## Saved Ghidra Changes

| Address | Saved state | Static evidence summary |
| --- | --- | --- |
| `0x004a13b0` | `CMemoryHeap__Init` | `MEM_MANAGER__Init` calls this heap initializer four times; it clears counters/free lists, links into `DAT_009c3df0`, allocates/aligned the base block, and optionally builds the tiny heap. |
| `0x004a15a0` | `CMemoryHeap__ReallocTiny` | `CPolyBucket__ReallocFromPool` reaches this tiny-heap realloc path; it checks the `+0x8c0..+0x8c8` range, frees the old tiny block, allocates replacement storage, and writes through `out_result`. |
| `0x004a1640` | `CMemoryHeap__Cleanup` | Called from `CMemoryHeap__Alloc`, `CMemoryHeap__SetMerge`, and `MEM_MANAGER__Cleanup`; it optionally guards with the heap mutex, coalesces free blocks, and rebuilds free lists. |
| `0x004a17b0` | `CMemoryHeap__Shutdown` | Unlinks the heap from the global heap list, frees the heap base allocation, releases the retail mutex/HANDLE slot at `+0x8bc`, and clears that field. |
| `0x004a1810` | `CMemoryHeap__Alloc` | Core allocation path covering tiny heap, small buckets, main free list, cleanup retry, OOM diagnostics, block split/consume, and counter updates. |
| `0x004a1c30` | `CMemoryHeap__ReleaseMutexUnwindCleanup` | EH unwind helper referenced by allocator/free unwind records at `0x005d3540` and `0x005d3560`; it releases the mutex HANDLE stored through its argument. |
| `0x004a1c40` | `CMemoryHeap__ReAlloc` | Allocates replacement storage using the old block's memory type, copies `min(old_size, new_size)` bytes from `block+0x10`, frees the old block, and returns the new pointer. |
| `0x004a1ca0` | `CMemoryHeap__Free` | Updates free/used/per-type counters from the block header, clears used/base-set flags, delegates to `CMemoryHeap__AddToFreeList`, and releases the heap mutex. |
| `0x004a1d60` | `CMemoryHeap__AddToFreeList` | Reinserts free blocks into small buckets or the main free list, with optional adjacent-block coalescing when merge mode is enabled. |
| `0x004a1ea0` | `CMemoryHeap__SetMerge` | When enabling merge from disabled state, calls `CMemoryHeap__Cleanup`, selection-sorts the main free list by block size, and stores the merge flag at `+0x874`. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| Headless `ApplyMemoryManagerWave438.java` dry/apply/verify | PASS | Dry found `10` targets with `would_rename=10`; apply reported `updated=10`, `renamed=10`, `missing=0`, `bad=0`; verify dry reported `updated=0`, `skipped=10`, `would_rename=0`, `missing=0`, `bad=0`. |
| Post-apply metadata/tag/xref/instruction/decompile read-back | PASS | Verified `10` metadata rows, `10` tag rows, `31` xref rows, `490` instruction rows, and `10` target decompile exports. |
| `py -3 -m py_compile tools\ghidra_memorymanager_wave438_probe.py tools\ghidra_memorymanager_wave438_probe_test.py` | PASS | Focused probe modules compile. |
| `py -3 tools\ghidra_memorymanager_wave438_probe_test.py` | PASS | Focused tests passed `4/4`. |
| `py -3 tools\ghidra_memorymanager_wave438_probe.py --check --json` | PASS | Focused probe returned `status: PASS` for all `10` saved targets. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS | Queue reports `6055` total functions, `1818` commented functions, `4237` commentless functions, `1792` undefined signatures, and `1747` `param_N` signatures. |

## Current Queue Telemetry

The refreshed static re-audit queue currently reports:

- Total function objects: `6055`
- Commented function objects: `1818`
- Commentless function objects: `4237`
- `undefined` signatures: `1792`
- Signatures still using `param_N`: `1747`

Telemetry-only proxies are comment-backed `1818/6055 = 30.02%` and strict clean-signature `1756/6055 = 29.00%`. These are not certification and are not completion gates.

## Not Proven

This wave does not prove runtime allocator behavior; exact concrete `CMemoryHeap` / `CMemoryBlock` layouts beyond observed offsets; exact local variable names/types; exact Steam-vs-source mutex lifetime; full `MemoryManager.cpp` coverage; source-to-retail rebuild parity; BEA launch behavior; game patching; or runtime gameplay behavior.
