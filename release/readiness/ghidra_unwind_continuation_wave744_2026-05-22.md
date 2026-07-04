# Ghidra Unwind Continuation Wave744 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-22
Scope: `unwind-continuation-wave744`

Wave744 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 26 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d1610 Unwind@005d1610` through `0x005d1828 Unwind@005d1828`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d1610 Unwind@005d1610` | DATA scope-table xref `0x0061a47c`; calls `CGenericCamera__dtor` on `EBP-0x10`. |
| `0x005d164b Unwind@005d164b` | DATA scope-table xref `0x0061a4c4`; calls `OID__FreeObject_Callback` on `EBP+4` with Monitor.h debug path `0x00622b80`, line `0x18`, memtype `0x5e`. |
| `0x005d1760 Unwind@005d1760` | DATA scope-table xref `0x0061a5dc`; calls `OID__FreeObject_Callback` on `EBP+4` with Cannon.cpp debug path `0x00623dd4`, line `0x22`, memtype `0x17`. |
| `0x005d17b0 Unwind@005d17b0` | DATA scope-table xref `0x0061a61c`; calls `CSPtrSet__Clear` on stack local `EBP-0x1c`. |
| `0x005d1828 Unwind@005d1828` | DATA scope-table xref `0x0061a684`; calls `CSPtrSet__Clear` on stack local `EBP-0x1c`, closing the local set-clear pair before the next Carrier.cpp allocation-cleanup cluster. |

Read-back evidence:

- `ApplyUnwindContinuationWave744.java dry`: `updated=0 skipped=26 renamed=0 would_rename=0 signature_updated=26 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave744.java apply`: `updated=26 skipped=0 renamed=0 would_rename=0 signature_updated=26 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave744.java final dry`: `updated=0 skipped=26 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 26 metadata rows, 26 tag rows, 26 xref rows, 598 instruction rows, and 26 decompile rows.
- Queue after Wave744: 6098 total, 4462 commented, 1636 commentless, 1113 exact-undefined signatures, 27 `param_N`, comment-backed proxy `4462/6098 = 73.17%`, strict clean-signature proxy `4404/6098 = 72.22%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d1840 Unwind@005d1840`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-163423_post_wave744_unwind_continuation_verified`, 19 files, 167381895 bytes, `DiffCount=0`.

What this proves:

- The 26 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave744` and `wave744-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
