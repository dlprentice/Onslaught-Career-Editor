# Ghidra Unwind Continuation Wave757 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave757`

Wave757 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d3614 Unwind@005d3614` through `0x005d38a0 Unwind@005d38a0`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d3614 Unwind@005d3614` | DATA scope-table xref `0x0061c354`; jumps to `CGenericActiveReader__dtor` for the active-reader subobject at `(*(EBP-0x10))+0x34`. |
| `0x005d3630 Unwind@005d3630` | DATA scope-table xref `0x0061c37c`; jumps to `CMenuItem__RestoreCompactVTable(*(EBP-0x14))`. |
| `0x005d3640 Unwind@005d3640` | DATA scope-table xref `0x0061c38c`; calls `OID__FreeObject_Callback` for Monitor.h debug path `0x00622b80`, line `0x5e`, allocation/type value `0x18`, pointer `*(EBP+0x8)`. |
| `0x005d3698 Unwind@005d3698` | DATA scope-table xref `0x0061c3f4`; jumps to `CGenericActiveReader__dtor` for the active-reader subobject at `(*(EBP-0x10))+0x34`. |
| `0x005d36b0 Unwind@005d36b0` | DATA scope-table xref `0x0061c41c`; jumps to `CSPtrSet__Clear((*(EBP-0x10))+0x08)`. |
| `0x005d36f0 Unwind@005d36f0` | DATA scope-table xref `0x0061c46c`; calls `OID__FreeObject_Callback` for mesh.cpp debug path `0x0062f8e8`, line `0x24`, allocation/type value `0x91`, pointer `*(EBP-0x10)`. |
| `0x005d3720 Unwind@005d3720` | DATA scope-table xref `0x0061c494`; jumps to `CDXMemBuffer__dtor_base` for the stack-local buffer at `EBP-0x340`. |
| `0x005d3740 Unwind@005d3740` | DATA scope-table xref `0x0061c4dc`; calls `OID__FreeObject_Callback` for mesh.cpp debug path `0x0062f8e8`, line `0x24`, allocation/type value `0x349`, pointer `*(EBP-0x82c)`. |
| `0x005d37b0 Unwind@005d37b0` | DATA scope-table xref `0x0061c4fc`; calls `OID__FreeObject_Callback` for mesh.cpp debug path `0x0062f8e8`, line `0x01`, allocation/type value `0x584`, pointer `*(EBP-0x794)`. |
| `0x005d3820 Unwind@005d3820` | DATA scope-table xref `0x0061c4cc`; calls `OID__FreeObject_Callback` for mesh.cpp debug path `0x0062f8e8`, line `0x01`, allocation/type value `0x28d`, pointer `*(EBP-0x810)`. |
| `0x005d3870 Unwind@005d3870` | DATA scope-table xref `0x0061c52c`; calls `OID__FreeObject_Callback` for mesh.cpp debug path `0x0062f8e8`, line `0x01`, allocation/type value `0x755`, pointer `*(EBP+0x4)`. |
| `0x005d38a0 Unwind@005d38a0` | DATA scope-table xref `0x0061c554`; calls `OID__FreeObject_Callback` for mesh.cpp debug path `0x0062f8e8`, line `0x01`, allocation/type value `0x982`, pointer `*(EBP-0x34c)`. |

Read-back evidence:

- `ApplyUnwindContinuationWave757.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave757.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave757.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 925 instruction rows, 25 decompile rows, and 6 helper metadata rows.
- Queue after Wave757: 6098 total, 4787 commented, 1311 commentless, 788 exact-undefined signatures, 27 `param_N`, comment-backed proxy `4787/6098 = 78.50%`, strict clean-signature proxy `4729/6098 = 77.55%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d38bc Unwind@005d38bc`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-120201_post_wave757_unwind_continuation_verified`, 19 files, 168594311 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave757` and `wave757-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, debug-string dumps, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
