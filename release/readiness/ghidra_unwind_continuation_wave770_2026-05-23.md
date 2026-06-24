# Ghidra Unwind Continuation Wave770 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave770`

Wave770 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d5532 Unwind@005d5532` through `0x005d57ec Unwind@005d57ec`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d5532 Unwind@005d5532` | DATA scope-table xref `0x0061ddc4`; `OID__FreeObject_Callback` on `*(EBP+0x4)` with Unit.cpp debug path `0x00633b6c`, line `0x15b`, allocation/type value `0x10`. |
| `0x005d5590 Unwind@005d5590` | DATA scope-table xref `0x0061ddfc`; jumps to `CLine__SetBaseVtable_00426360` on the stack-local object at `EBP-0x70`. |
| `0x005d55f0 Unwind@005d55f0` | DATA scope-table xref `0x0061de54`; jumps to `CMonitor__Shutdown` on the monitor object at `*(EBP-0x74)`. |
| `0x005d55f8 Unwind@005d55f8` | DATA scope-table xref `0x0061de5c`; jumps to `CGenericActiveReader__dtor` on `(*(EBP-0x74))+0x0c`. |
| `0x005d5630 Unwind@005d5630` | DATA scope-table xref `0x0061de94`; jumps to `DeviceObject__ctor_like_00512d50`; exact helper semantics remain unproven. |
| `0x005d5670 Unwind@005d5670` | DATA scope-table xref `0x0061dee4`; `OID__FreeObject_Callback` with vbuftexture.cpp debug path `0x00633d5c`, line `0xb6`, allocation/type value `0x2c`. |
| `0x005d5710 Unwind@005d5710` | DATA scope-table xref `0x0061df84`; `OID__FreeObject_Callback` with VertexShader.cpp debug path `0x0063cf78`, line `0x2bd`, allocation/type value `0x50`. |
| `0x005d5770 Unwind@005d5770` | DATA scope-table xref `0x0061dfd4`; `OID__FreeObject_Callback` with Warspite.cpp debug path `0x0063d12c`, line `0x0a`, allocation/type value `0x16`. |
| `0x005d5790 Unwind@005d5790` | DATA scope-table xref `0x0061dffc`; jumps to `CMonitor__Shutdown` on the monitor object at `*(EBP-0x10)`. |
| `0x005d57c0 Unwind@005d57c0` | DATA scope-table xref `0x0061e034`; `OID__FreeObject_Callback` with WarspiteDome.cpp debug path `0x0063d170`, line `0x19`, allocation/type value `0x17`. |
| `0x005d57ec Unwind@005d57ec` | DATA scope-table xref `0x0061e044`; `OID__FreeObject_Callback` with WarspiteDome.cpp debug path `0x0063d170`, line `0x1d`, allocation/type value `0x1b`. |

Read-back evidence:

- `ApplyUnwindContinuationWave770.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave770.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave770.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 2225 instruction rows, 25 decompile rows, and 5 helper metadata rows.
- Queue after Wave770: 6098 total, 5112 commented, 986 commentless, 463 exact-undefined signatures, 27 `param_N`, comment-backed proxy `5112/6098 = 83.83%`, strict clean-signature proxy `5054/6098 = 82.88%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d5810 Unwind@005d5810`.
- Verified backup: `G:\GhidraBackups\BEA_20260523-180835_post_wave770_unwind_continuation_verified`, 19 files, 169806727 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave770` and `wave770-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, debug-string dumps, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
