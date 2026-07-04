# Ghidra Unwind Continuation Wave775 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave775`

Wave775 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d5fb0 Unwind@005d5fb0` through `0x005d6136 Unwind@005d6136`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d5fb0 Unwind@005d5fb0` | DATA scope-table xref `0x0061e654`; `CUnit__dtor_base` on `*(EBP-0x10)`. |
| `0x005d5fb8 Unwind@005d5fb8` | DATA scope-table xref `0x0061e65c`; `CParticleManager__RemoveFromGlobalList_Thunk` on `(*(EBP-0x10))+0x250`. |
| `0x005d5fc6 Unwind@005d5fc6` | DATA scope-table xref `0x0061e664`; `CSPtrSet__Clear` on `(*(EBP-0x10))+0x25c`. |
| `0x005d6070 Unwind@005d6070` | DATA scope-table xref `0x0061e734`; `CUnit__dtor_base_Thunk_004bfe00` on `*(EBP-0x10)`. |
| `0x005d6090 Unwind@005d6090` | DATA scope-table xref `0x0061e75c`; `CUnit__dtor_base` on `*(EBP-0x10)`. |
| `0x005d60a6 Unwind@005d60a6` | DATA scope-table xref `0x0061e76c`; `CSPtrSet__Clear` on `(*(EBP-0x10))+0x25c`. |
| `0x005d6120 Unwind@005d6120` | DATA scope-table xref `0x0061e804`; `CUnit__dtor_base` on `*(EBP-0x10)`. |
| `0x005d6136 Unwind@005d6136` | DATA scope-table xref `0x0061e814`; `CSPtrSet__Clear` on `(*(EBP-0x10))+0x25c`. |

Read-back evidence:

- `ApplyUnwindContinuationWave775.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave775.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave775.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 3025 instruction rows, 25 decompile rows, and 4 helper metadata rows.
- Queue after Wave775: 6098 total, 5237 commented, 861 commentless, 338 exact-undefined signatures, 27 `param_N`, comment-backed proxy `5237/6098 = 85.88%`, strict clean-signature proxy `5179/6098 = 84.93%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d6150 Unwind@005d6150`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-201144_post_wave775_unwind_continuation_verified`, 19 files, 170199943 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave775` and `wave775-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
