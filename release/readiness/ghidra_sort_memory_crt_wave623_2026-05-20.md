# Ghidra Sort/Memory/CRT Wave623 Readiness Note

Status: complete
Date: 2026-05-20

## Scope

Wave623 hardened twelve adjacent generic sort, memory, wide-string, math, heap, and stream I/O helper rows in the saved Ghidra project:

- `0x0055e7ae Sort__QuickSortGeneric`
- `0x0055e902 Sort__ShortSortGeneric`
- `0x0055e950 Memory__SwapByteRange`
- `0x0055eb00 CRT__WcsNcpyZeroPad`
- `0x0055eb3d CRT__RoundToIntegerRespectingControlWord`
- `0x0055ec4a CRT__HeapAllocBase`
- `0x0055ed50 CRT__MemMoveOverlapSafe`
- `0x0055f085 CRT__FreeBase`
- `0x0055f19d CRT__FWriteCore`
- `0x0055f2e8 CRT__WcsCmp`
- `0x0055f39d CRT__AcosCoreWithFpuGuards`
- `0x0055f506 CRT__FReadCore`

The pass saved bounded signatures, comments, and tags. It corrected one stale or misleading label: `CDXEngine__InsertionSortGeneric` is now the owner-neutral `Sort__ShortSortGeneric`, because the only current named caller is `Sort__QuickSortGeneric` and the body is the qsort-style small-partition sorter, not a DX engine method. It made no function-boundary changes and no executable byte changes.

## Evidence

- Dry/apply/final-dry logs reported `updated=0 skipped=12 renamed=0 would_rename=1 missing=0 bad=0`, then `updated=12 skipped=0 renamed=1 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=12 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post-state exports verified `12` metadata rows, `12` tag rows, `147` xref rows, `1260` instruction rows, and `12` decompile rows.
- Generic sort evidence covers a qsort-style worklist sorter, the small-partition short-sort helper, and byte-range swapping. Xrefs include display-device sorting, render overlay candidate sorting, texture symbol-table finalization, and world-file enumeration.
- Wide-string evidence covers `WcsNcpyZeroPad` and `WcsCmp` callsites in text wrapping, save-list rendering, virtual keyboard rendering, message-box portrait selection, and save-file enumeration.
- Math evidence covers FPU-control-word-aware rounding and the split-double acos core path behind `CRT__AcosClassifyAndDispatch`.
- Heap evidence covers small-block heap allocation/free paths under lock 9 and fallback `HeapAlloc`/`HeapFree` routing.
- Stream evidence covers core `fwrite`/`fread` helpers that handle buffered bytes, fd text-mode read/write paths, and EOF/error flags.
- Backup verified: `[maintainer-local-ghidra-backup-root]\BEA_20260520-052133_post_wave623_sort_memory_crt_verified` with `19` files, `161909639` bytes, and `DiffCount=0`.

## Queue Telemetry

Post-Wave623 queue telemetry:

- Total functions: `6093`
- Commented functions: `3256`
- Commentless functions: `2837`
- Exact `undefined` signatures: `1218`
- `param_N` signatures: `1024`
- Comment-backed proxy: `3256/6093 = 53.44%`
- Strict clean-signature proxy: `3204/6093 = 52.58%`

Delta from Wave622: `+12` commented, `-12` commentless, `0` exact-undefined signatures, `-12` `param_N`, and `+12` strict clean-signature rows.

The next high-signal queue head is `0x0055f5ee Win32__FindFirstFileWithMeta`.

## Boundaries

This is static saved-Ghidra sort/memory/CRT helper evidence only. Exact CRT identity/version, full comparator/locale/math/heap/stream semantics, runtime file I/O or UI text behavior, BEA patching, and rebuild parity remain deferred.
