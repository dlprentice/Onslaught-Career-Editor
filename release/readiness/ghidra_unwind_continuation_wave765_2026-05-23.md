# Ghidra Unwind Continuation Wave765 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave765`

Wave765 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d4948 Unwind@005d4948` through `0x005d4bd0 Unwind@005d4bd0`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d4948 Unwind@005d4948` | DATA scope-table xref `0x0061d1b4`; jumps to `CParticleManager__RemoveFromGlobalList_Thunk` on the stack/local list node at `(*(EBP-0x10))+0xe0`. |
| `0x005d4956 Unwind@005d4956` | DATA scope-table xref `0x0061d1bc`; jumps to `CGenericActiveReader__dtor` on the active-reader subobject at `(*(EBP-0x10))+0xe8`. |
| `0x005d4970 Unwind@005d4970` | DATA scope-table xref `0x0061d1e4`; calls `OID__FreeObject_Callback(*(EBP-0x8c))` with Round.cpp debug path `0x00631d38`, line token `0x62`, and allocation/type value `0x0d`. |
| `0x005d49a2 Unwind@005d49a2` | DATA scope-table xref `0x0061d1f4`; jumps to `CCollisionSeekingRound__Destructor(*(EBP-0x8c))`. |
| `0x005d4a30 Unwind@005d4a30` | DATA scope-table xref `0x0061d2a4`; jumps to `CRenderThing__dtor(*(EBP-0x10))`. |
| `0x005d4a50 Unwind@005d4a50` | DATA scope-table xref `0x0061d2cc`; calls `OID__FreeObject_Callback(*(EBP-0x214))` with meshpose.h debug path `0x00631ed8`, line token `0x21`, and allocation/type value `0x7d`. |
| `0x005d4ae0 Unwind@005d4ae0` | DATA scope-table xref `0x0061d36c`; jumps to `CMonitor__Shutdown` on the monitor subobject at `(*(EBP-0x42c))+0x04`. |
| `0x005d4b50 Unwind@005d4b50` | DATA scope-table xref `0x0061d3c4`; calls `OID__FreeObject_Callback(*(EBP+0x04))` with Sentinel.cpp debug path `0x0063221c`, line token `0x20`, and allocation/type value `0x1b`. |
| `0x005d4bb3 Unwind@005d4bb3` | DATA scope-table xref `0x0061d40c`; jumps to `CGenericActiveReader__dtor` on the active-reader subobject at `(*(EBP-0x10))+0x24`. |
| `0x005d4bd0 Unwind@005d4bd0` | DATA scope-table xref `0x0061d434`; jumps to `CDXLandscape__DestroyResourceDescriptorArray_Thunk` on the stack-local descriptor array at `EBP-0x434`. |

Read-back evidence:

- `ApplyUnwindContinuationWave765.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave765.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave765.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 2025 instruction rows, 25 decompile rows, and 9 helper metadata rows.
- Queue after Wave765: 6098 total, 4987 commented, 1111 commentless, 588 exact-undefined signatures, 27 `param_N`, comment-backed proxy `4987/6098 = 81.78%`, strict clean-signature proxy `4929/6098 = 80.83%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d4bf0 Unwind@005d4bf0`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-155528_post_wave765_unwind_continuation_verified`, 19 files, 169315207 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave765` and `wave765-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, debug-string dumps, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
