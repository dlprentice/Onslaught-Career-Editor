# Ghidra Unwind Continuation Wave774 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave774`

Wave774 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d5d96 Unwind@005d5d96` through `0x005d5f96 Unwind@005d5f96`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d5d96 Unwind@005d5d96` | DATA scope-table xref `0x0061e52c`; `OID__FreeObject_Callback` on `*(EBP+0x4)`. |
| `0x005d5e04 Unwind@005d5e04` | DATA scope-table xref `0x0061e554`; `OID__FreeObject_Callback` on `*(EBP+0x4)`. |
| `0x005d5e88 Unwind@005d5e88` | DATA scope-table xref `0x0061e584`; `OID__FreeObject_Callback` on `*(EBP+0x4)`. |
| `0x005d5f22 Unwind@005d5f22` | DATA scope-table xref `0x0061e5bc`; `OID__FreeObject_Callback` on `*(EBP+0x4)`. |
| `0x005d5f50 Unwind@005d5f50` | DATA scope-table xref `0x0061e5e4`; `CUnit__dtor_base` on `*(EBP-0x10)`. |
| `0x005d5f66 Unwind@005d5f66` | DATA scope-table xref `0x0061e5f4`; `CSPtrSet__Clear` on `(*(EBP-0x10))+0x25c`. |
| `0x005d5f96 Unwind@005d5f96` | DATA scope-table xref `0x0061e62c`; `CSPtrSet__Clear` on `(*(EBP-0x10))+0x25c`. |

Read-back evidence:

- `ApplyUnwindContinuationWave774.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave774.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave774.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 3025 instruction rows, 25 decompile rows, and 4 helper metadata rows.
- Queue after Wave774: 6098 total, 5212 commented, 886 commentless, 363 exact-undefined signatures, 27 `param_N`, comment-backed proxy `5212/6098 = 85.47%`, strict clean-signature proxy `5154/6098 = 84.52%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d5fb0 Unwind@005d5fb0`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-194938_post_wave774_unwind_continuation_verified`, 19 files, 170167175 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave774` and `wave774-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
