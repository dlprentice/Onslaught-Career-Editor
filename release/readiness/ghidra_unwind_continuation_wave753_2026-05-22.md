# Ghidra Unwind Continuation Wave753 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-22
Scope: `unwind-continuation-wave753`

Wave753 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d2c48 Unwind@005d2c48` through `0x005d2e78 Unwind@005d2e78`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d2c48 Unwind@005d2c48` | DATA scope-table xref `0x0061ba14`; calls `CDXLandscape__FreeObjectCallback` on `(*(EBP+0x4))+0x10` in the post-GroundVehicle scope-table run. |
| `0x005d2c53 Unwind@005d2c53` | DATA scope-table xref `0x0061ba1c`; calls `CUnitAI__FreeOwnedObjects_10_18` on `(*(EBP-0x10))+0x24`. |
| `0x005d2c90 Unwind@005d2c90` | DATA scope-table xref `0x0061ba6c`; calls `CMonitor__Shutdown_Thunk` on the monitor object at `*(EBP-0x14)`. |
| `0x005d2cb0 Unwind@005d2cb0` | DATA scope-table xref `0x0061ba9c`; calls `OID__FreeObject_Callback` for HiveBoss.cpp debug path `0x0062cc98`, line `0x55`, allocation/type value `0x21`, pointer `*(EBP+0x4)`. |
| `0x005d2d00 Unwind@005d2d00` | DATA scope-table xref `0x0061bad4`; calls `OID__FreeObject_Callback` for Hud.cpp debug path `0x0062ce78`, line `0x38`, allocation/type value `0x5d`, pointer `*(EBP-0x10)`. |
| `0x005d2d80 Unwind@005d2d80` | DATA scope-table xref `0x0061bb34`; calls `CSPtrSet__Clear` on the stack-local set at `EBP-0x4c`. |
| `0x005d2db0 Unwind@005d2db0` | DATA scope-table xref `0x0061bb74`; loads `ECX` from `*(EBP-0x10)` and jumps to `DeviceObject__ctor_like_00512d50`; exact helper semantics remain unproven. |
| `0x005d2df0 Unwind@005d2df0` | DATA scope-table xref `0x0061bbc4`; calls `OID__FreeObject_Callback` for imposter.cpp debug path `0x0062d3f0`, line `0x39`, allocation/type value `0x29`, pointer `*(EBP+0x1c)`. |
| `0x005d2e10 Unwind@005d2e10` | DATA scope-table xref `0x0061bbec`; calls `OID__FreeObject_Callback` for Infantry.cpp debug path `0x0062d4a8`, line `0x0b`, allocation/type value `0x1c`, pointer `*(EBP+0x4)`. |
| `0x005d2e26 Unwind@005d2e26` | DATA scope-table xref `0x0061bbf4`; calls `CCollisionSeekingRound__Destructor` on the object pointer at `*(EBP+0x4)`. |
| `0x005d2e70 Unwind@005d2e70` | DATA scope-table xref `0x0061bc2c`; calls `CMonitor__Shutdown` on the monitor object at `*(EBP-0x10)`. |
| `0x005d2e78 Unwind@005d2e78` | DATA scope-table xref `0x0061bc34`; calls `CGenericActiveReader__dtor` on the active-reader subobject at `(*(EBP-0x10))+0x0c`. |

Read-back evidence:

- `ApplyUnwindContinuationWave753.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave753.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave753.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 925 instruction rows, and 25 decompile rows.
- Queue after Wave753: 6098 total, 4687 commented, 1411 commentless, 888 exact-undefined signatures, 27 `param_N`, comment-backed proxy `4687/6098 = 76.86%`, strict clean-signature proxy `4629/6098 = 75.91%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d2e83 Unwind@005d2e83`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-221626_post_wave753_unwind_continuation_verified`, 19 files, 168168327 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave753` and `wave753-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, debug-string dumps, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
