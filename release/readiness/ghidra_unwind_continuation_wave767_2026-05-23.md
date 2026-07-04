# Ghidra Unwind Continuation Wave767 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave767`

Wave767 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d4e00 Unwind@005d4e00` through `0x005d5030 Unwind@005d5030`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d4e00 Unwind@005d4e00` | DATA scope-table xref `0x0061d6a4`; calls `OID__FreeObject_Callback` on `*(EBP-0x10)` with SquadNormal.cpp debug path `0x0063283c`, line token `0x437`, allocation/type value `0x08`. |
| `0x005d4e60 Unwind@005d4e60` | DATA scope-table xref `0x0061d6f4`; calls `OID__FreeObject_Callback` on `*(EBP-0x10)` with SquadRelaxed.cpp debug path `0x00632918`, line token `0xa0`, allocation/type value `0x08`. |
| `0x005d4e90 Unwind@005d4e90` | DATA scope-table xref `0x0061d71c`; jumps to `CComplexThing__dtor_base` for the object pointer at `*(EBP-0x10)`. |
| `0x005d4ed0 Unwind@005d4ed0` | DATA scope-table xref `0x0061d77c`; jumps to `CParticleManager__RemoveFromGlobalList_Thunk` for the stack-local node at `EBP-0x14`. |
| `0x005d4ef0 Unwind@005d4ef0` | DATA scope-table xref `0x0061d7a4`; calls `OID__FreeObject_Callback` with StaticShadows.cpp debug path `0x006329f8`, line token `0x18a`, allocation/type value `0x70`. |
| `0x005d4f28 Unwind@005d4f28` | DATA scope-table xref `0x0061d7b4`; first of eight adjacent `CLine__SetBaseVtable_00426360` stack-local line cleanup callbacks. |
| `0x005d4f90 Unwind@005d4f90` | DATA scope-table xref `0x0061d814`; calls `OID__FreeObject_Callback` with StaticShadows.cpp debug path `0x006329f8`, line token `0x43d`, allocation/type value `0x70`. |
| `0x005d4fc0 Unwind@005d4fc0` | DATA scope-table xref `0x0061d83c`; calls `OID__FreeObject_Callback` with Submarine.cpp debug path `0x00632abc`, line token `0x1d`, allocation/type value `0x16`. |
| `0x005d5000 Unwind@005d5000` | DATA scope-table xref `0x0061d86c`; jumps to `CMonitor__Shutdown` on the monitor pointer at `*(EBP-0x10)`. |
| `0x005d5008 Unwind@005d5008` | DATA scope-table xref `0x0061d874`; jumps to `CGenericActiveReader__dtor` on the embedded active-reader subobject at `(*(EBP-0x10))+0x0c`. |
| `0x005d5013 Unwind@005d5013` | DATA scope-table xref `0x0061d87c`; jumps to `CGenericActiveReader__dtor` on the embedded active-reader subobject at `(*(EBP-0x10))+0x24`. |
| `0x005d5030 Unwind@005d5030` | DATA scope-table xref `0x0061d8a4`; jumps to `CController__dtor_Thunk` on the stack-local controller at `EBP-0x184`. |

Read-back evidence:

- `ApplyUnwindContinuationWave767.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave767.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave767.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 925 instruction rows, 25 decompile rows, and 7 helper metadata rows.
- Queue after Wave767: 6098 total, 5037 commented, 1061 commentless, 538 exact-undefined signatures, 27 `param_N`, comment-backed proxy `5037/6098 = 82.60%`, strict clean-signature proxy `4979/6098 = 81.65%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d5050 Unwind@005d5050`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-164622_post_wave767_unwind_continuation_verified`, 19 files, 169511815 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave767` and `wave767-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, debug-string dumps, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
