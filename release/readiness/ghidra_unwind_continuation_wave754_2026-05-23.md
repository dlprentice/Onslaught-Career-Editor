# Ghidra Unwind Continuation Wave754 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave754`

Wave754 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d2e83 Unwind@005d2e83` through `0x005d308a Unwind@005d308a`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d2e83 Unwind@005d2e83` | DATA scope-table xref `0x0061bc3c`; calls `CGenericActiveReader__dtor` on the active-reader subobject at `(*(EBP-0x10))+0x24`. |
| `0x005d2ea0 Unwind@005d2ea0` | DATA scope-table xref `0x0061bc64`; calls `CCollisionSeekingRound__Destructor` on `*(EBP-0x10)`. |
| `0x005d2ec0 Unwind@005d2ec0` | DATA scope-table xref `0x0061bc8c`; calls `CMonitor__Shutdown_Thunk` on `*(EBP-0x10)`. |
| `0x005d2ec8 Unwind@005d2ec8` | DATA scope-table xref `0x0061bc94`; calls `CDXLandscape__FreeObjectCallback` on `(*(EBP+0x4))+0x10`. |
| `0x005d2ed3 Unwind@005d2ed3` | DATA scope-table xref `0x0061bc9c`; calls `CUnitAI__FreeOwnedObjects_10_18` on `(*(EBP-0x10))+0x24`. |
| `0x005d2f30 Unwind@005d2f30` | DATA scope-table xref `0x0061bd1c`; calls `OID__FreeObject_Callback` for InfluenceMap.cpp debug path `0x0062d61c`, line `0x20`, allocation/type value `0x74`, pointer `*(EBP-0x3d0)`. |
| `0x005d2f54 Unwind@005d2f54` | DATA scope-table xref `0x0061bd2c`; calls `CSPtrSet__Clear` on `(*(EBP-0x3d0))+0x7c`. |
| `0x005d2fa0 Unwind@005d2fa0` | DATA scope-table xref `0x0061bd54`; calls `OID__FreeObject_Callback` for InfluenceMap.cpp debug path `0x0062d61c`, line `0x20`, allocation/type value `0x1a6`, pointer `*(EBP-0x10)`. |
| `0x005d2ff0 Unwind@005d2ff0` | DATA scope-table xref `0x0061bda4`; calls `OID__FreeObject_Callback` for InitThing.cpp debug path `0x0062d7b0`, line `0x09`, allocation/type value `0x0f`, pointer `*(EBP+0x4)`. |
| `0x005d3032 Unwind@005d3032` | DATA scope-table xref `0x0061bdbc`; calls `OID__FreeObject_Callback` for InitThing.cpp debug path `0x0062d7b0`, line `0x09`, allocation/type value `0x1b`, pointer `*(EBP+0x4)`. |
| `0x005d308a Unwind@005d308a` | DATA scope-table xref `0x0061bddc`; calls `OID__FreeObject_Callback` for InitThing.cpp debug path `0x0062d7b0`, line `0x09`, allocation/type value `0x2b`, pointer `*(EBP+0x4)`. |

Read-back evidence:

- `ApplyUnwindContinuationWave754.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave754.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave754.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 925 instruction rows, 25 decompile rows, and 10 helper metadata rows.
- Queue after Wave754: 6098 total, 4712 commented, 1386 commentless, 863 exact-undefined signatures, 27 `param_N`, comment-backed proxy `4712/6098 = 77.27%`, strict clean-signature proxy `4654/6098 = 76.32%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d30a0 Unwind@005d30a0`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-102949_post_wave754_unwind_continuation_verified`, 19 files, 168299399 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave754` and `wave754-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, debug-string dumps, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
