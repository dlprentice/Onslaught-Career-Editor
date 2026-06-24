# Ghidra Unwind Continuation Wave772 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave772`

Wave772 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 compiler-generated SEH unwind cleanup callbacks from `0x005d59f3 Unwind@005d59f3` through `0x005d5b37 Unwind@005d5b37`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d59f3 Unwind@005d59f3` | DATA scope-table xref `0x0061e25c`; calls `CSPtrSet__Clear` on subobject `(*(EBP-0x10))+0x90`. |
| `0x005d5a01 Unwind@005d5a01` | DATA scope-table xref `0x0061e264`; calls `CSPtrSet__Clear` on subobject `(*(EBP-0x10))+0xa0`. |
| `0x005d5a0f Unwind@005d5a0f` | DATA scope-table xref `0x0061e26c`; calls `CSPtrSet__Clear` on subobject `(*(EBP-0x10))+0xb0`. |
| `0x005d5a63 Unwind@005d5a63` | DATA scope-table xref `0x0061e29c`; calls `CSPtrSet__Clear` on subobject `(*(EBP-0x10))+0x110`. |
| `0x005d5a80 Unwind@005d5a80` | DATA scope-table xref `0x0061e2c4`; calls `CSPtrSet__Clear` on `*(EBP-0x10)`. |
| `0x005d5aca Unwind@005d5aca` | DATA scope-table xref `0x0061e2fc`; calls `CSPtrSet__Clear` on subobject `(*(EBP-0x10))+0x70`. |
| `0x005d5b37 Unwind@005d5b37` | DATA scope-table xref `0x0061e33c`; calls `CSPtrSet__Clear` on subobject `(*(EBP-0x10))+0xf0`. |

Read-back evidence:

- `ApplyUnwindContinuationWave772.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave772.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave772.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 2325 instruction rows, 25 decompile rows, and 1 helper metadata row.
- Queue after Wave772: 6098 total, 5162 commented, 936 commentless, 413 exact-undefined signatures, 27 `param_N`, comment-backed proxy `5162/6098 = 84.65%`, strict clean-signature proxy `5104/6098 = 83.70%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d5b45 Unwind@005d5b45`.
- Verified backup: `G:\GhidraBackups\BEA_20260523-185858_post_wave772_unwind_continuation_verified`, 19 files, 170003335 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave772` and `wave772-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, helper metadata, instruction exports, and decompile exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
