# Ghidra Unwind Continuation Wave783 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave783`

Wave783 unwind continuation saved Ghidra comments, tags, and `void __cdecl ... (void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d7280 Unwind@005d7280` through `0x005d7520 Unwind@005d7520`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d7280 Unwind@005d7280` | DATA scope-table xref `0x0061f6d4`; `CGenericActiveReader__dtor` on `*(EBP-0x40)`. |
| `0x005d72a0 Unwind@005d72a0` | DATA scope-table xref `0x0061f704`; `OID__FreeObject_Callback` on `*(EBP-0x41c)`. |
| `0x005d72ae Unwind@005d72ae` | DATA scope-table xref `0x0061f70c`; `CActor__dtor_base` on `*(EBP-0x41c)`. |
| `0x005d73d9 Unwind@005d73d9` | DATA scope-table xref `0x0061f804`; `CMonitor__Shutdown` on `*(EBP-0x10)`. |
| `0x005d7410 Unwind@005d7410` | DATA scope-table xref `0x0061f854`; `CSPtrSet__Clear` on `(*(EBP-0x10))+0x04`. |
| `0x005d7487 Unwind@005d7487` | DATA scope-table xref `0x0061f8bc`; `CGenericActiveReader__dtor` on `*(EBP-0x14)`. |
| `0x005d74d0 Unwind@005d74d0` | DATA scope-table xref `0x0061f8fc`; `CFlexArray__Free_thunk` on `(*(EBP-0x10))+0x04`. |
| `0x005d7520 Unwind@005d7520` | DATA scope-table xref `0x0061f93c`; `OID__FreeObject_Callback` on `*(EBP-0x10)`. |

Read-back evidence:

- `ApplyUnwindContinuationWave783.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave783.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave783.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 1225 instruction rows, 25 decompile rows, and 6 helper metadata rows.
- Queue after Wave783: 6098 total, 5437 commented, 661 commentless, 138 exact-undefined signatures, 27 `param_N`, comment-backed proxy `5437/6098 = 89.16%`, strict clean-signature proxy `5379/6098 = 88.21%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d7536 Unwind@005d7536`.
- Verified backup: `G:\GhidraBackups\BEA_20260523-231334_post_wave783_unwind_continuation_verified`, 19 files, 170920839 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl ... (void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave783` and `wave783-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
