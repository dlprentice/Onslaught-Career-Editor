# Ghidra Unwind Continuation Wave758 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave758`

Wave758 unwind continuation saved Ghidra comments, tags, and `void __cdecl ...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d38bc Unwind@005d38bc` through `0x005d3bb0 Unwind@005d3bb0`. The pass preserved the existing `0x005d3980 CMeshCollisionVolume__SetPartBounds_Unwind` name and made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d38bc Unwind@005d38bc` | DATA scope-table xref `0x0061c55c`; calls `OID__FreeObject_Callback` on `*(EBP-0x34c)` with mesh.cpp debug path `0x0062f8e8`, line token `0x80`, allocation/type value `0x9cc`. |
| `0x005d3940 Unwind@005d3940` | DATA scope-table xref `0x0061c59c`; jumps to `CLine__SetBaseVtable_00426360` for the stack-local object at `EBP-0x28`. |
| `0x005d3980 CMeshCollisionVolume__SetPartBounds_Unwind` | DATA scope-table xref `0x0061c5ec`; calls `OID__FreeObject_Callback` on `*(EBP+0x4)` with MeshCollisionVolume.cpp debug path `0x0062fe40` and raw pushed immediate tokens `0x229` and `0x6c`; exact allocator callback argument semantics remain unproven. |
| `0x005d39b0 Unwind@005d39b0` | DATA scope-table xref `0x0061c614`; calls `OID__FreeObject_Callback` on `*(EBP-0x10)` with MeshPart.cpp debug path `0x0062fe70`, line token `0x46`, allocation/type value `0xe9`. |
| `0x005d3a10 Unwind@005d3a10` | DATA scope-table xref `0x0061c664`; calls `OID__FreeObject_Callback` on `*(EBP-0x154)` with MeshPart.cpp debug path `0x0062fe70`, line token `0x74`, allocation/type value `0x717`. |
| `0x005d3ac0 Unwind@005d3ac0` | DATA scope-table xref `0x0061c6ec`; calls `OID__FreeObject_Callback` on `*(EBP+0x14)` with MeshRenderer.cpp debug path `0x00630178`, line token `0x10`, allocation/type value `0x207`. |
| `0x005d3af0 Unwind@005d3af0` | DATA scope-table xref `0x0061c714`; loads `ECX` from `*(EBP-0x10)`, subtracts `0x20`, and jumps to `CWaitingThread__ctor_like_00528bf0`; exact helper semantics remain unproven. |
| `0x005d3b30 Unwind@005d3b30` | DATA scope-table xref `0x0061c764`; jumps to `CMonitor__Shutdown_Thunk` on `*(EBP-0x14)`. |
| `0x005d3b38 Unwind@005d3b38` | DATA scope-table xref `0x0061c76c`; jumps to `CGenericActiveReader__dtor` on the active-reader subobject at `(*(EBP-0x14))+0x30`. |
| `0x005d3b78 Unwind@005d3b78` | DATA scope-table xref `0x0061c7c4`; jumps to `CSPtrSet__Clear` on the embedded set at `(*(EBP-0x18))+0x0c`. |
| `0x005d3bb0 Unwind@005d3bb0` | DATA scope-table xref `0x0061c81c`; jumps to `CSPtrSet__Clear` on the stack-local set at `EBP-0x1c`. |

Read-back evidence:

- `ApplyUnwindContinuationWave758.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave758.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave758.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 2025 instruction rows, 25 decompile rows, and 8 helper metadata rows.
- Queue after Wave758: 6098 total, 4812 commented, 1286 commentless, 763 exact-undefined signatures, 27 `param_N`, comment-backed proxy `4812/6098 = 78.91%`, strict clean-signature proxy `4754/6098 = 77.96%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d3bd0 Unwind@005d3bd0`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-123821_post_wave758_unwind_continuation_verified`, 19 files, 168659847 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl ...(void)` with no parameters, including the preserved `CMeshCollisionVolume__SetPartBounds_Unwind` row.
- The saved comments and tags include `unwind-continuation-wave758` and `wave758-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, debug-string dumps, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
