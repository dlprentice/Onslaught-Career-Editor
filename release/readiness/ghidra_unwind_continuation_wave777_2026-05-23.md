# Ghidra Unwind Continuation Wave777 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave777`

Wave777 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d636a Unwind@005d636a` through `0x005d65cb Unwind@005d65cb`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d636a Unwind@005d636a` | DATA scope-table xref `0x0061ea04`; `OID__FreeObject_Callback` on `*(EBP+0x4)`. |
| `0x005d6383 Unwind@005d6383` | DATA scope-table xref `0x0061ea0c`; `CUnit__dtor_base` on `*(EBP+0x4)`. |
| `0x005d63a0 Unwind@005d63a0` | DATA scope-table xref `0x0061ea34`; `CUnit__dtor_base` on `*(EBP-0x10)`. |
| `0x005d63a8 Unwind@005d63a8` | DATA scope-table xref `0x0061ea3c`; `CParticleManager__RemoveFromGlobalList_Thunk` on `(*(EBP-0x10))+0x258`. |
| `0x005d6430 Unwind@005d6430` | DATA scope-table xref `0x0061eaec`; `CComplexThing__dtor_base` on `*(EBP-0x10)`. |
| `0x005d6499 Unwind@005d6499` | DATA scope-table xref `0x0061eb44`; `CComplexThing__dtor_base` on `*(EBP+0x4)`. |
| `0x005d64d0 Unwind@005d64d0` | DATA scope-table xref `0x0061eb94`; `OID__FreeObject_Callback` on `*(EBP-0x10)`. |
| `0x005d65c0 Unwind@005d65c0` | DATA scope-table xref `0x0061ebfc`; `CDXMemBuffer__dtor_base` on stack-local `EBP-0x140`. |
| `0x005d65cb Unwind@005d65cb` | DATA scope-table xref `0x0061ec04`; `CSPtrSet__Clear` on `(*(EBP-0x18c))+0x40`. |

Read-back evidence:

- `ApplyUnwindContinuationWave777.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave777.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave777.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 925 instruction rows, 25 decompile rows, and 6 helper metadata rows.
- Queue after Wave777: 6098 total, 5287 commented, 811 commentless, 288 exact-undefined signatures, 27 `param_N`, comment-backed proxy `5287/6098 = 86.70%`, strict clean-signature proxy `5229/6098 = 85.75%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d65d9 Unwind@005d65d9`.
- Verified backup: `G:\GhidraBackups\BEA_20260523-210103_post_wave777_unwind_continuation_verified`, 19 files, 170363783 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave777` and `wave777-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
