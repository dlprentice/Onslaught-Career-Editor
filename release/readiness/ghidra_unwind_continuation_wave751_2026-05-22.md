# Ghidra Unwind Continuation Wave751 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-22
Scope: `unwind-continuation-wave751`

Wave751 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d2730 Unwind@005d2730` through `0x005d29d8 Unwind@005d29d8`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d2730 Unwind@005d2730` | DATA scope-table xref `0x0061b5a4`; calls `OID__FreeObject_Callback` for FrontEnd.cpp debug path `0x00629df0`, line `0x27`, allocation/type value `0xb3`, pointer `*(EBP-0x24)`. |
| `0x005d2760 Unwind@005d2760` | DATA scope-table xref `0x0061b5cc`; calls `CDXLandscape__DestroyResourceDescriptorArray_Thunk` on the stack-local descriptor array at `EBP-0x434`. |
| `0x005d2780 Unwind@005d2780` | DATA scope-table xref `0x0061b5f4`; calls `OID__FreeObject_Callback` for game.cpp debug path `0x0062bba4`, line `0x26`, allocation/type value `0x108`, pointer `*(EBP-0x18)`. |
| `0x005d27a9 Unwind@005d27a9` | DATA scope-table xref `0x0061b60c`; calls `OID__FreeObject_Callback` for monitor.h debug path `0x0062551c`, line `0x5e`, allocation/type value `0x18`, pointer `*(EBP-0x10)`. |
| `0x005d27f8 Unwind@005d27f8` | DATA scope-table xref `0x0061b664`; calls `CGenericActiveReader__dtor` on the subobject at `(*(EBP-0x10))+0x9f8`. |
| `0x005d2930 Unwind@005d2930` | DATA scope-table xref `0x0061b71c`; calls `CMonitor__Shutdown_Thunk` on the object at `EBP-0x114`. |
| `0x005d2950 Unwind@005d2950` | DATA scope-table xref `0x0061b744`; calls `CDXLandscape__ReleaseSurfaces` on the object at `EBP-0x44`. |
| `0x005d29d8 Unwind@005d29d8` | DATA scope-table xref `0x0061b7c4`; calls `OID__FreeObject_Callback` for game.cpp debug path `0x0062bba4`, line `0x27`, allocation/type value `0x11be`, pointer `*(EBP-0x1c)`. |

Read-back evidence:

- `ApplyUnwindContinuationWave751.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave751.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave751.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 725 instruction rows, and 25 decompile rows.
- Queue after Wave751: 6098 total, 4637 commented, 1461 commentless, 938 exact-undefined signatures, 27 `param_N`, comment-backed proxy `4637/6098 = 76.04%`, strict clean-signature proxy `4579/6098 = 75.09%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d29f1 Unwind@005d29f1`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-204801_post_wave751_unwind_continuation_verified`, 19 files, 168004487 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave751` and `wave751-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, debug-string dumps, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
