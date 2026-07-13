# Ghidra Unwind Continuation Wave764 Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x004df520` → `CActor__dtor_base_Thunk` (was `CActor__dtor_base`). The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave764`

Wave764 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d46c8 Unwind@005d46c8` through `0x005d4940 Unwind@005d4940`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d46c8 Unwind@005d46c8` | DATA scope-table xref `0x0061cf4c`; jumps to `CGenericActiveReader__dtor` on the active-reader subobject at `(*(EBP-0x10))+0x0c`. |
| `0x005d46f0 Unwind@005d46f0` | DATA scope-table xref `0x0061cf7c`; jumps to `CMonitor__Shutdown_Thunk(*(EBP-0x10))`. |
| `0x005d4730 Unwind@005d4730` | DATA scope-table xref `0x0061cfd4`; calls `OID__FreeObject_Callback(*(EBP-0x14))` with Player.cpp debug path `0x00631690`, line token `0x3a`, and allocation/type value `0x26`. |
| `0x005d4746 Unwind@005d4746` | DATA scope-table xref `0x0061cfdc`; jumps to `CGenericCamera__dtor(*(EBP-0x14))`. |
| `0x005d4756 Unwind@005d4756` | DATA scope-table xref `0x0061cfec`; calls `OID__FreeObject_Callback(*(EBP-0x10))` with monitor.h debug path `0x0062551c`, line token `0x18`, and allocation/type value `0x5e`. |
| `0x005d47a0 Unwind@005d47a0` | DATA scope-table xref `0x0061d03c`; calls `OID__FreeObject_Callback(*(EBP-0x40))` with Player.cpp debug path `0x00631690`, line token `0xa0`, and allocation/type value `0x28`. |
| `0x005d4800 Unwind@005d4800` | DATA scope-table xref `0x0061d074`; calls `OID__FreeObject_Callback(EBP-0xec)` with PolyBucket.cpp debug path `0x006316bc`, line token `0x14c`, and allocation/type value `0x46`. |
| `0x005d481c Unwind@005d481c` | DATA scope-table xref `0x0061d07c`; calls `OID__FreeObject_Callback(EBP-0xe4)` with array.h debug path `0x0062d590`, line token `0x12`, and allocation/type value `0x54`. |
| `0x005d4888 Unwind@005d4888` | DATA scope-table xref `0x0061d0dc`; jumps to `CSPtrSet__Clear` on the embedded pointer set at `(*(EBP-0x10))+0x1c`. |
| `0x005d48a0 Unwind@005d48a0` | DATA scope-table xref `0x0061d104`; calls `OID__FreeObject_Callback(*(EBP-0x44))` with RadarWarningReceiver.cpp debug path `0x00631784`, line token `0x41`, and allocation/type value `0x49`. |
| `0x005d48d0 Unwind@005d48d0` | DATA scope-table xref `0x0061d134`; calls `OID__FreeObject_Callback(EBP-0x5cc)` with ResourceAccumulator.cpp debug path `0x00631b7c`, line token `0x330`, and allocation/type value `0x80`. |
| `0x005d4900 Unwind@005d4900` | DATA scope-table xref `0x0061d15c`; jumps to `CDXLandscape__DestroyResourceDescriptorArray_Thunk` on the stack-local descriptor array at `EBP-0x434`. |
| `0x005d4920 Unwind@005d4920` | DATA scope-table xref `0x0061d184`; jumps to `CActor__dtor_base(*(EBP-0x10))`. |
| `0x005d4940 Unwind@005d4940` | DATA scope-table xref `0x0061d1ac`; jumps to `CActor__dtor_base(*(EBP-0x10))`. |

Read-back evidence:

- `ApplyUnwindContinuationWave764.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave764.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave764.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 2625 instruction rows, 25 decompile rows, and 7 helper metadata rows.
- Queue after Wave764: 6098 total, 4962 commented, 1136 commentless, 613 exact-undefined signatures, 27 `param_N`, comment-backed proxy `4962/6098 = 81.37%`, strict clean-signature proxy `4904/6098 = 80.42%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d4948 Unwind@005d4948`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-152957_post_wave764_unwind_continuation_verified`, 19 files, 169216903 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave764` and `wave764-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, debug-string dumps, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
