# Ghidra Unwind Continuation Wave748 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-22
Scope: `unwind-continuation-wave748`

Wave748 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d1fc8 Unwind@005d1fc8` through `0x005d222b Unwind@005d222b`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d1fc8 Unwind@005d1fc8` | DATA scope-table xref `0x0061ae64`; calls `CGenericActiveReader__dtor` on the embedded reader at `(*(EBP-0x10))+0x854`. |
| `0x005d1ff0 Unwind@005d1ff0` | DATA scope-table xref `0x0061ae94`; calls `OID__FreeObject_Callback` on `EBP-0x111c` with Cutscene.cpp debug path `0x0062811c`, line `0xcb`, allocation/type value `0x1c`. |
| `0x005d2070 Unwind@005d2070` | DATA scope-table xref `0x0061af0c`; calls `CDXLandscape__DestroyResourceDescriptorArray_Thunk` on the stack-local descriptor array at `EBP-0x434`. |
| `0x005d2170 Unwind@005d2170` | DATA scope-table xref `0x0061b064`; calls `OID__FreeObject_Callback` on `EBP-0x14` with DestructableSegmentsController.cpp debug path `0x006287b4`, line `0x1a8`, allocation/type value `0x55`. |
| `0x005d222b Unwind@005d222b` | DATA scope-table xref `0x0061b0e4`; calls `OID__FreeObject_Callback` on `EBP+4` with DestructableSegmentsController.cpp debug path `0x006287b4`, line `0x1f2`, allocation/type value `0x55`. |

Read-back evidence:

- `ApplyUnwindContinuationWave748.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave748.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave748.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 575 instruction rows, and 25 decompile rows.
- Queue after Wave748: 6098 total, 4562 commented, 1536 commentless, 1013 exact-undefined signatures, 27 `param_N`, comment-backed proxy `4562/6098 = 74.81%`, strict clean-signature proxy `4504/6098 = 73.86%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d2250 Unwind@005d2250`.
- Verified backup: `G:\GhidraBackups\BEA_20260522-183258_post_wave748_unwind_continuation_verified`, 19 files, 167742343 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave748` and `wave748-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, debug-string dumps, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
