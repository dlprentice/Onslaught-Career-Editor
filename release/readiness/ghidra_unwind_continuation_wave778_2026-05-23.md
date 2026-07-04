# Ghidra Unwind Continuation Wave778 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave778`

Wave778 unwind continuation saved Ghidra comments, tags, and `void __cdecl ... (void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d65d9 Unwind@005d65d9` through `0x005d6840 CFastVB__Render__Unwind`. The pass preserved existing `CFastVB__Create__Unwind` and `CFastVB__Render__Unwind` names, made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d65d9 Unwind@005d65d9` | DATA scope-table xref `0x0061ec0c`; `OID__FreeObject_Callback` on `*(EBP-0x18c)`. |
| `0x005d65f5 Unwind@005d65f5` | DATA scope-table xref `0x0061ec14`; `CSPtrSet__Clear` on `(*(EBP-0x188))+0x40`. |
| `0x005d6630 Unwind@005d6630` | DATA scope-table xref `0x0061ec44`; `CSPtrSet__Clear` on `(*(EBP-0x10))+0x4c`. |
| `0x005d6690 Unwind@005d6690` | DATA scope-table xref `0x0061ecb4`; `CSPtrSet__Clear` on `(*(EBP-0x10))+0x40`. |
| `0x005d67b0 Unwind@005d67b0` | DATA scope-table xref `0x0061edac`; `CSample__DestructorBody` on `*(EBP-0x10)`. |
| `0x005d6800 Unwind@005d6800` | DATA scope-table xref `0x0061edfc`; `CDXMemBuffer__dtor_base` on `EBP-0x240`. |
| `0x005d6820 CFastVB__Create__Unwind` | DATA scope-table xref `0x0061ee24`; `OID__FreeObject_Callback` on `*(EBP-0x10)`. |
| `0x005d6840 CFastVB__Render__Unwind` | DATA scope-table xref `0x0061ee4c`; `OID__FreeObject_Callback` on `*(EBP-0x10)`. |

Read-back evidence:

- `ApplyUnwindContinuationWave778.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave778.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave778.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 925 instruction rows, 25 decompile rows, and 4 helper metadata rows.
- Queue after Wave778: 6098 total, 5312 commented, 786 commentless, 263 exact-undefined signatures, 27 `param_N`, comment-backed proxy `5312/6098 = 87.11%`, strict clean-signature proxy `5254/6098 = 86.16%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d6870 Unwind@005d6870`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-212139_post_wave778_unwind_continuation_verified`, 19 files, 170429319 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl ... (void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave778` and `wave778-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
