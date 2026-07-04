# Ghidra Unwind Continuation Wave756 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave756`

Wave756 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d3392 Unwind@005d3392` through `0x005d360c Unwind@005d360c`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d3392 Unwind@005d3392` | DATA scope-table xref `0x0061c0ac`; calls `OID__FreeObject_Callback` on `*(EBP-0x174)` with MCTentacle.cpp debug path `0x0062e06c`, line token `0x1b`, and allocation/type value `0x6d`. |
| `0x005d33c0 Unwind@005d33c0` | DATA scope-table xref `0x0061c0d4`; calls `OID__FreeObject_Callback` on `*(EBP-0x10)` with Mech.cpp debug path `0x0062e0e0`, line token `0x1b`, and allocation/type value `0x3d`. |
| `0x005d3420 Unwind@005d3420` | DATA scope-table xref `0x0061c14c`; same Mech.cpp allocation-cleanup shape with pointer `*(EBP+0x4)`, line token `0x5c`, and allocation/type value `0x57`. |
| `0x005d3480 Unwind@005d3480` | DATA scope-table xref `0x0061c1c4`; jumps to `CMonitor__Shutdown` with `ECX=*(EBP-0x10)`. |
| `0x005d34b0 Unwind@005d34b0` | DATA scope-table xref `0x0061c1fc`; jumps to `CMonitor__Shutdown_Thunk` with `ECX=*(EBP-0x10)`. |
| `0x005d3540 Unwind@005d3540` | DATA scope-table xref `0x0061c29c`; jumps to `CMemoryHeap__ReleaseMutexUnwindCleanup` for the mutex handle pointer at `EBP-0x10`. |
| `0x005d3580 Unwind@005d3580` | DATA scope-table xref `0x0061c2ec`; jumps to `CDXMemBuffer__dtor_base` for the large stack-local buffer at `EBP-0x6844`. |
| `0x005d35a0 Unwind@005d35a0` | DATA scope-table xref `0x0061c314`; calls `OID__FreeObject_Callback` on `*(EBP-0x2210)` with MemoryManager.cpp debug path `0x0062f590`, line token `0x64`, and allocation/type value `0x708`. |
| `0x005d35f0 Unwind@005d35f0` | DATA scope-table xref `0x0061c344`; calls `OID__FreeObject_Callback` on `*(EBP-0x10)` with MenuItem.cpp debug path `0x0062f7d8`, line token `0x80`, and allocation/type value `0xad`. |
| `0x005d360c Unwind@005d360c` | DATA scope-table xref `0x0061c34c`; jumps to `CMenuItem__RestoreCompactVTable` with `ECX=*(EBP-0x10)`. |

Read-back evidence:

- `ApplyUnwindContinuationWave756.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave756.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave756.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 925 instruction rows, 25 decompile rows, and 13 helper metadata rows.
- Queue after Wave756: 6098 total, 4762 commented, 1336 commentless, 813 exact-undefined signatures, 27 `param_N`, comment-backed proxy `4762/6098 = 78.09%`, strict clean-signature proxy `4704/6098 = 77.14%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d3614 Unwind@005d3614`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-112625_post_wave756_unwind_continuation_verified`, 19 files, 168496007 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave756` and `wave756-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, debug-string dumps, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
