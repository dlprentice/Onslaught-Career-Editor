# Ghidra Unwind Continuation Wave760 Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x004df520` → `CActor__dtor_base_Thunk` (was `CActor__dtor_base`). The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave760`

Wave760 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d3d94 Unwind@005d3d94` through `0x005d3f35 Unwind@005d3f35`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d3d94 Unwind@005d3d94` | DATA scope-table xref `0x0061c9ec`; calls `OID__FreeObject_Callback(*(EBP+0x4))` with oids.cpp debug path `0x00630c20`, line token `0x05`, and allocation/type value `0x2e`. |
| `0x005d3dd6 Unwind@005d3dd6` | DATA scope-table xref `0x0061ca04`; loads `ECX` from `*(EBP+0x4)` and jumps to `CActor__dtor_base`. |
| `0x005d3e20 Unwind@005d3e20` | DATA scope-table xref `0x0061ca24`; loads `ECX` from `*(EBP+0x4)` and jumps to `CComplexThing__dtor_base`. |
| `0x005d3e28 Unwind@005d3e28` | DATA scope-table xref `0x0061ca2c`; jumps to `CGenericActiveReader__dtor` on object field `(*(EBP+0x4))+0x7c`. |
| `0x005d3e7d Unwind@005d3e7d` | DATA scope-table xref `0x0061ca54`; jumps to `CGenericActiveReader__dtor` on object field `(*(EBP+0x4))+0x854`. |
| `0x005d3eeb Unwind@005d3eeb` | DATA scope-table xref `0x0061ca84`; jumps to `CParticleManager__RemoveFromGlobalList_Thunk` on object field `(*(EBP+0x4))+0x7c`. |
| `0x005d3f22 Unwind@005d3f22` | DATA scope-table xref `0x0061ca9c`; loads `ECX` from `*(EBP+0x4)` and jumps to `CComplexThing__dtor_base`. |
| `0x005d3f35 Unwind@005d3f35` | DATA scope-table xref `0x0061caac`; calls `OID__FreeObject_Callback(*(EBP+0x4))` with oids.cpp debug path `0x00630c20`, line token `0x05`, and allocation/type value `0x47`. |

Read-back evidence:

- `ApplyUnwindContinuationWave760.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave760.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave760.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 2625 instruction rows, 25 decompile rows, and 7 helper metadata rows.
- Queue after Wave760: 6098 total, 4862 commented, 1236 commentless, 713 exact-undefined signatures, 27 `param_N`, comment-backed proxy `4862/6098 = 79.73%`, strict clean-signature proxy `4804/6098 = 78.78%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d3f4b Unwind@005d3f4b`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-133538_post_wave760_unwind_continuation_verified`, 19 files, 168889223 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave760` and `wave760-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, debug-string dumps, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
