# Ghidra Unwind Continuation Wave780 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave780`

Wave780 unwind continuation saved Ghidra comments, tags, and `void __cdecl ... (void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d6b20 Unwind@005d6b20` through `0x005d6d50 Unwind@005d6d50`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d6b20 Unwind@005d6b20` | DATA scope-table xref `0x0061f0dc`; `OID__FreeObject_Callback` on `*(EBP-0x10)`. |
| `0x005d6b50 Unwind@005d6b50` | DATA scope-table xref `0x0061f104`; `OID__FreeObject_Callback` on `*(EBP-0x10)`. |
| `0x005d6b69 Unwind@005d6b69` | DATA scope-table xref `0x0061f10c`; `CDataType__Destructor` on `*(EBP-0x10)`. |
| `0x005d6ba1 Unwind@005d6ba1` | DATA scope-table xref `0x0061f144`; `CGenericActiveReader__dtor` on `*(EBP-0x14)`. |
| `0x005d6c50 Unwind@005d6c50` | DATA scope-table xref `0x0061f214`; `CMonitor__Shutdown` on `*(EBP-0x10)`. |
| `0x005d6c58 Unwind@005d6c58` | DATA scope-table xref `0x0061f21c`; `CSPtrSet__Clear` on `(*(EBP-0x10))+0xc`. |
| `0x005d6d00 Unwind@005d6d00` | DATA scope-table xref `0x0061f2fc`; `OID__FreeObject_Callback` on `*(EBP-0x14)`. |
| `0x005d6d50 Unwind@005d6d50` | DATA scope-table xref `0x0061f33c`; `OID__FreeObject_Callback` on `*(EBP-0x10)`. |

Read-back evidence:

- `ApplyUnwindContinuationWave780.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave780.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave780.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 925 instruction rows, 25 decompile rows, and 5 helper metadata rows.
- Queue after Wave780: 6098 total, 5362 commented, 736 commentless, 213 exact-undefined signatures, 27 `param_N`, comment-backed proxy `5362/6098 = 87.93%`, strict clean-signature proxy `5304/6098 = 86.98%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d6d80 Unwind@005d6d80`.
- Verified backup: `G:\GhidraBackups\BEA_20260523-220956_post_wave780_unwind_continuation_verified`, 19 files, 170625927 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl ... (void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave780` and `wave780-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
