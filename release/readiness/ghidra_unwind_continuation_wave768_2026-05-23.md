# Ghidra Unwind Continuation Wave768 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave768`

Wave768 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d5050 Unwind@005d5050` through `0x005d5320 Unwind@005d5320`. The pass made no renames, no function-boundary changes, and no executable-byte changes. The already-clean `0x005d5120 CTexture__FindTexture_Unwind` row was not part of the mutation set.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d5050 Unwind@005d5050` | DATA scope-table xref `0x0061d8cc`; calls `OID__FreeObject_Callback` on `*(EBP-0x10)` with Tentacle.cpp debug path `0x00632ccc`, line token `0x2f`, allocation/type value `0x1b`. |
| `0x005d5070 Unwind@005d5070` | DATA scope-table xref `0x0061d8f4`; calls `OID__FreeObject_Callback` on `*(EBP-0x10)` with Tentacle.cpp line token `0x35`, allocation/type value `0x17`. |
| `0x005d5090 Unwind@005d5090` | DATA scope-table xref `0x0061d91c`; calls `OID__FreeObject_Callback` on `*(EBP-0x10)` with Tentacle.cpp line token `0x3c`, allocation/type value `0x17`. |
| `0x005d50b0 Unwind@005d50b0` | DATA scope-table xref `0x0061d944`; jumps to `CMonitor__Shutdown` on the monitor pointer at `*(EBP-0x10)`. |
| `0x005d50b8 Unwind@005d50b8` | DATA scope-table xref `0x0061d94c`; jumps to `CGenericActiveReader__dtor` on the embedded active-reader subobject at `(*(EBP-0x10))+0x0c`. |
| `0x005d50e0 Unwind@005d50e0` | DATA scope-table xref `0x0061d97c`; jumps to `CParticleManager__RemoveFromGlobalList_Thunk` on the stack-local node at `EBP-0x44`. |
| `0x005d5100 Unwind@005d5100` | DATA scope-table xref `0x0061d9a4`; jumps to `CDXMemBuffer__dtor_base` on the stack-local buffer at `EBP-0x240`. |
| `0x005d5198 Unwind@005d5198` | DATA scope-table xref `0x0061da4c`; jumps to `CMapWhoEntry__RemoveFromMap` on the entry subobject at `(*(EBP-0x10))+0x0c`. |
| `0x005d51b0 Unwind@005d51b0` | DATA scope-table xref `0x0061da74`; jumps to `CCollisionSeekingRound__Destructor` on the object pointer at `*(EBP-0x10)`. |
| `0x005d5220 Unwind@005d5220` | DATA scope-table xref `0x0061dafc`; calls `OID__FreeObject_Callback` on `*(EBP+0x4)` with thing.cpp debug path `0x006331c0`, line token `0x299`, allocation/type value `0x18`. |
| `0x005d5280 Unwind@005d5280` | DATA scope-table xref `0x0061db4c`; calls `OID__FreeObject_Callback` on `*(EBP-0x10)` with ThunderHead.cpp debug path `0x00633240`, line token `0x20`, allocation/type value `0x1b`. |
| `0x005d52e0 Unwind@005d52e0` | DATA scope-table xref `0x0061dbc4`; jumps to `CDXLandscape__DestroyResourceDescriptorArray_Thunk` on the stack-local descriptor array at `EBP-0x534`. |
| `0x005d5320 Unwind@005d5320` | DATA scope-table xref `0x0061dc14`; calls `OID__FreeObject_Callback` on `*(EBP+0x4)` with tree.cpp debug path `0x00633a84`, line token `0x8f`, allocation/type value `0x5c`. |

Read-back evidence:

- `ApplyUnwindContinuationWave768.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave768.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave768.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 2025 instruction rows, 25 decompile rows, and 10 helper metadata rows.
- Queue after Wave768: 6098 total, 5062 commented, 1036 commentless, 513 exact-undefined signatures, 27 `param_N`, comment-backed proxy `5062/6098 = 83.01%`, strict clean-signature proxy `5004/6098 = 82.06%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d5350 Unwind@005d5350`.
- Verified backup: `G:\GhidraBackups\BEA_20260523-171555_post_wave768_unwind_continuation_verified`, 19 files, 169610119 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave768` and `wave768-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, debug-string dumps, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
