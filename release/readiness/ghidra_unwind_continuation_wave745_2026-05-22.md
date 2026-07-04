# Ghidra Unwind Continuation Wave745 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-22
Scope: `unwind-continuation-wave745`

Wave745 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d1840 Unwind@005d1840` through `0x005d1a98 Unwind@005d1a98`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d1840 Unwind@005d1840` | DATA scope-table xref `0x0061a6ac`; calls `OID__FreeObject_Callback` on `EBP+4` with Carrier.cpp debug path `0x006243bc`, line `0x1a`, memtype `0x17`. |
| `0x005d18b0 Unwind@005d18b0` | DATA scope-table xref `0x0061a714`; calls `OID__FreeObject_Callback` on `EBP+4` with Carver.cpp debug path `0x00624400`, line `0x16`, memtype `0x17`. |
| `0x005d1940 Unwind@005d1940` | DATA scope-table xref `0x0061a7a4`; calls `OID__FreeObject_Callback` on `EBP-0x10` with chunker.cpp debug path `0x00624464`, line `0x62`, memtype `0x11`. |
| `0x005d196b Unwind@005d196b` | DATA scope-table xref `0x0061a7d4`; calls `CDXLandscape__DestroyResourceDescriptorArray_Thunk` on stack local `EBP-0x434`. |
| `0x005d19e0 Unwind@005d19e0` | DATA scope-table xref `0x0061a874`; calls `OID__FreeObject_Callback` on `EBP-0x10` with Component.cpp debug path `0x006247f8`, line `0x4d`, memtype `0x1b`. |
| `0x005d1a98 Unwind@005d1a98` | DATA scope-table xref `0x0061a90c`; calls `CGenericActiveReader__dtor` on embedded object field `*(EBP-0x10)+0xc`. |

Read-back evidence:

- `ApplyUnwindContinuationWave745.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave745.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave745.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 575 instruction rows, and 25 decompile rows.
- Queue after Wave745: 6098 total, 4487 commented, 1611 commentless, 1088 exact-undefined signatures, 27 `param_N`, comment-backed proxy `4487/6098 = 73.58%`, strict clean-signature proxy `4429/6098 = 72.63%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d1aa3 Unwind@005d1aa3`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-170426_post_wave745_unwind_continuation_verified`, 19 files, 167447431 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave745` and `wave745-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, debug-string dumps, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
