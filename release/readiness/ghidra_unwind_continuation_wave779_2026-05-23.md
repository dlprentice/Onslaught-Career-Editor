# Ghidra Unwind Continuation Wave779 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave779`

Wave779 unwind continuation saved Ghidra comments, tags, and `void __cdecl ... (void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d6870 Unwind@005d6870` through `0x005d6af0 Unwind@005d6af0`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d6870 Unwind@005d6870` | DATA scope-table xref `0x0061ee74`; `OID__FreeObject_Callback` on `*(EBP+0x4)`. |
| `0x005d68a0 Unwind@005d68a0` | DATA scope-table xref `0x0061ee9c`; `CDXMemBuffer__dtor_base` on `EBP-0x208`. |
| `0x005d68c0 Unwind@005d68c0` | DATA scope-table xref `0x0061eec4`; `OID__FreeObject_Callback` on `*(EBP-0x20)`. |
| `0x005d6920 Unwind@005d6920` | DATA scope-table xref `0x0061ef14`; `OID__FreeObject_Callback` on `*(EBP-0x58)`. |
| `0x005d69c0 Unwind@005d69c0` | DATA scope-table xref `0x0061efdc`; `OID__FreeObject_Callback` on `*(EBP+0x4)`. |
| `0x005d69d6 Unwind@005d69d6` | DATA scope-table xref `0x0061efe4`; `CDataType__Destructor` on `*(EBP+0x4)`. |
| `0x005d6a56 Unwind@005d6a56` | DATA scope-table xref `0x0061f02c`; `CGenericActiveReader__dtor` on `(*(EBP+0x4))+0x4`. |
| `0x005d6af0 Unwind@005d6af0` | DATA scope-table xref `0x0061f0b4`; `OID__FreeObject_Callback` on `*(EBP-0x10)`. |

Read-back evidence:

- `ApplyUnwindContinuationWave779.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave779.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave779.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 925 instruction rows, 25 decompile rows, and 4 helper metadata rows.
- Queue after Wave779: 6098 total, 5337 commented, 761 commentless, 238 exact-undefined signatures, 27 `param_N`, comment-backed proxy `5337/6098 = 87.52%`, strict clean-signature proxy `5279/6098 = 86.57%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d6b20 Unwind@005d6b20`.
- Verified backup: `G:\GhidraBackups\BEA_20260523-215114_post_wave779_unwind_continuation_verified`, 19 files, 170593159 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl ... (void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave779` and `wave779-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
