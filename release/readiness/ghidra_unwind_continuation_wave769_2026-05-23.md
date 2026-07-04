# Ghidra Unwind Continuation Wave769 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave769`

Wave769 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d5350 Unwind@005d5350` through `0x005d5519 Unwind@005d5519`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d5350 Unwind@005d5350` | DATA scope-table xref `0x0061dc3c`; calls `OID__FreeObject_Callback` on `*(EBP-0x40)` with tree.cpp debug path `0x00633a84`, line token `0xf0`, and allocation/type value `0x07`. |
| `0x005d5380 Unwind@005d5380` | DATA scope-table xref `0x0061dc64`; jumps to `CLine__SetBaseVtable_00426360` on stack-local object `EBP-0x50`. |
| `0x005d5388 Unwind@005d5388` | DATA scope-table xref `0x0061dc6c`; jumps to `CParticleManager__RemoveFromGlobalList_Thunk` on stack-local node `EBP-0x90`. |
| `0x005d53a0 Unwind@005d53a0` | DATA scope-table xref `0x0061dc94`; loads `ECX` from `*(EBP-0x10)` and jumps to `DeviceObject__ctor_like_00512d50`; exact helper semantics remain unproven. |
| `0x005d53e0 Unwind@005d53e0` | DATA scope-table xref `0x0061dce4`; jumps to `CActor__dtor_base` on `*(EBP-0x50)`. |
| `0x005d53e8 Unwind@005d53e8` | DATA scope-table xref `0x0061dcec`; jumps to `CGenericActiveReader__dtor` on `(*(EBP-0x50))+0x144`. |
| `0x005d5404 Unwind@005d5404` | DATA scope-table xref `0x0061dcfc`; begins the first pointer-set cleanup run, clearing embedded sets from `(*(EBP-0x50))+0x17c` through `+0x1d4`. |
| `0x005d5470 Unwind@005d5470` | DATA scope-table xref `0x0061dd4c`; second object cleanup run jumps to `CActor__dtor_base` on `*(EBP-0x10)`. |
| `0x005d5494 Unwind@005d5494` | DATA scope-table xref `0x0061dd64`; begins the second pointer-set cleanup run, clearing embedded sets from `(*(EBP-0x10))+0x17c` through `+0x1d4`. |
| `0x005d5500 Unwind@005d5500` | DATA scope-table xref `0x0061ddb4`; calls `OID__FreeObject_Callback` on `*(EBP-0x70)` with Unit.cpp debug path `0x00633b6c`, line token `0xc0`, and allocation/type value `0x61`. |
| `0x005d5519 Unwind@005d5519` | DATA scope-table xref `0x0061ddbc`; calls `OID__FreeObject_Callback` on `*(EBP-0x6c)` with Unit.cpp debug path `0x00633b6c`, line token `0x139`, and allocation/type value `0x61`. |

Read-back evidence:

- `ApplyUnwindContinuationWave769.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave769.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave769.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 2225 instruction rows, 25 decompile rows, and 7 helper metadata rows.
- Queue after Wave769: 6098 total, 5087 commented, 1011 commentless, 488 exact-undefined signatures, 27 `param_N`, comment-backed proxy `5087/6098 = 83.42%`, strict clean-signature proxy `5029/6098 = 82.47%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d5532 Unwind@005d5532`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-174151_post_wave769_unwind_continuation_verified`, 19 files, 169708423 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave769` and `wave769-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, debug-string dumps, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
