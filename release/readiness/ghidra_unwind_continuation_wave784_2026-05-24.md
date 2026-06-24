# Ghidra Unwind Continuation Wave784 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `unwind-continuation-wave784`

Wave784 unwind continuation saved Ghidra comments, tags, and `void __cdecl ... (void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d7536 Unwind@005d7536` through `0x005d77a0 Unwind@005d77a0`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d7536 Unwind@005d7536` | DATA scope-table xref `0x0061f944`; `CFlexArray__Free_thunk` on `(*(EBP-0x10))+0x04`. |
| `0x005d755b Unwind@005d755b` | DATA scope-table xref `0x0061f974`; `CSPtrSet__Clear` on `(*(EBP-0x10))+0x48`. |
| `0x005d7578 Unwind@005d7578` | DATA scope-table xref `0x0061f9a4`; `CStringDataType__Destructor` on `*(EBP-0x10)`. |
| `0x005d7590 Unwind@005d7590` | DATA scope-table xref `0x0061f9cc`; `OID__FreeObject_Callback` on `*(EBP-0x10)`. |
| `0x005d75f1 Unwind@005d75f1` | DATA scope-table xref `0x0061fa0c`; `CStringDataType__Destructor` on `*(EBP-0x10)`. |
| `0x005d76f0 Unwind@005d76f0` | DATA scope-table xref `0x0061faec`; `CAtmospheric__Unlink` on `*(EBP-0x14)`. |
| `0x005d77a0 Unwind@005d77a0` | DATA scope-table xref `0x0061fb64`; `CLine__SetBaseVtable_00426360` on `EBP-0x100`. |

Read-back evidence:

- `ApplyUnwindContinuationWave784.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave784.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave784.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 2225 instruction rows, 25 decompile rows, and 6 helper metadata rows.
- Queue after Wave784: 6098 total, 5462 commented, 636 commentless, 113 exact-undefined signatures, 27 `param_N`, comment-backed proxy `5462/6098 = 89.57%`, strict clean-signature proxy `5404/6098 = 88.62%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d77c0 Unwind@005d77c0`.
- Verified backup: `G:\GhidraBackups\BEA_20260524-001439_post_wave784_unwind_continuation_verified`, 19 files, 170953607 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl ... (void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave784` and `wave784-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
