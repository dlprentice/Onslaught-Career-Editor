# Ghidra Unwind Continuation Wave742 Readiness Note

Status: passed
Date: 2026-05-22

Wave742 unwind continuation saved comments/tags/signatures for twenty-five adjacent compiler-generated SEH unwind cleanup callbacks with the `unwind-continuation-wave742` and `wave742-readback-verified` tags. The pass hardened twenty-five `void __cdecl Unwind@...(void)` signatures, made no renames, made no function-boundary changes, and made no executable-byte changes.

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x005d1170 Unwind@005d1170` | `void __cdecl Unwind@005d1170(void)` | Scope-table DATA xref `0x00619fcc`; calls `CSPtrSet__Clear` on object field `EBP-0x10 + 0x2a4`. |
| `0x005d117e Unwind@005d117e` | `void __cdecl Unwind@005d117e(void)` | Scope-table DATA xref `0x00619fd4`; calls `CGenericActiveReader__dtor` on object field `EBP-0x10 + 0x4c8`. |
| `0x005d118c Unwind@005d118c` | `void __cdecl Unwind@005d118c(void)` | Scope-table DATA xref `0x00619fdc`; calls `CGenericActiveReader__dtor` on object field `EBP-0x10 + 0x4cc`. |
| `0x005d119a Unwind@005d119a` | `void __cdecl Unwind@005d119a(void)` | Scope-table DATA xref `0x00619fe4`; calls `CGenericActiveReader__dtor` on object field `EBP-0x10 + 0x4e0`. |
| `0x005d11a8 Unwind@005d11a8` | `void __cdecl Unwind@005d11a8(void)` | Scope-table DATA xref `0x00619fec`; calls `CGenericActiveReader__dtor` on object field `EBP-0x10 + 0x574`. |
| `0x005d11b6 Unwind@005d11b6` | `void __cdecl Unwind@005d11b6(void)` | Scope-table DATA xref `0x00619ff4`; calls `CGenericActiveReader__dtor` on object field `EBP-0x10 + 0x5e8`. |
| `0x005d11c4 Unwind@005d11c4` | `void __cdecl Unwind@005d11c4(void)` | Scope-table DATA xref `0x00619ffc`; calls `CParticleManager__RemoveFromGlobalList_Thunk` on object field `EBP-0x10 + 0x5f8`. |
| `0x005d11d2 Unwind@005d11d2` | `void __cdecl Unwind@005d11d2(void)` | Scope-table DATA xref `0x0061a004`; calls `CSPtrSet__Clear` on object field `EBP-0x10 + 0x620`. |
| `0x005d11f0 Unwind@005d11f0` | `void __cdecl Unwind@005d11f0(void)` | BattleEngine.cpp path `0x006230bc`, line `0x1f5`, memtype `0x15`, and scope-table DATA xref `0x0061a02c`; frees the pointer at `EBP-0x10`. |
| `0x005d1220 Unwind@005d1220` | `void __cdecl Unwind@005d1220(void)` | Scope-table DATA xref `0x0061a054`; calls `CLine__SetBaseVtable_00426360` on stack local `EBP-0x180`. |
| `0x005d1240 Unwind@005d1240` | `void __cdecl Unwind@005d1240(void)` | Scope-table DATA xref `0x0061a07c`; calls `CLine__SetBaseVtable_00426360` on stack local `EBP-0xb0`. |
| `0x005d1260 Unwind@005d1260` | `void __cdecl Unwind@005d1260(void)` | Scope-table DATA xref `0x0061a0a4`; calls `CLine__SetBaseVtable_00426360` on stack local `EBP-0x70`. |
| `0x005d1280 Unwind@005d1280` | `void __cdecl Unwind@005d1280(void)` | Scope-table DATA xref `0x0061a0cc`; calls `CLine__SetBaseVtable_00426360` on stack local `EBP-0x134`. |
| `0x005d128b Unwind@005d128b` | `void __cdecl Unwind@005d128b(void)` | Scope-table DATA xref `0x0061a0d4`; calls `CLine__SetBaseVtable_00426360` on stack local `EBP-0x40`. |
| `0x005d12a0 Unwind@005d12a0` | `void __cdecl Unwind@005d12a0(void)` | Scope-table DATA xref `0x0061a0fc`; calls `CParticleManager__RemoveFromGlobalList_Thunk` on stack local `EBP-0x24`. |
| `0x005d12c0 Unwind@005d12c0` | `void __cdecl Unwind@005d12c0(void)` | Scope-table DATA xref `0x0061a124`; calls `CSPtrSet__Clear` on object field `EBP-0x10 + 0x40`. |
| `0x005d12e0 Unwind@005d12e0` | `void __cdecl Unwind@005d12e0(void)` | Scope-table DATA xref `0x0061a14c`; calls `CSPtrSet__Clear` on the pointer at `EBP-0x10`. |
| `0x005d1300 Unwind@005d1300` | `void __cdecl Unwind@005d1300(void)` | Scope-table DATA xref `0x0061a174`; calls `CSPtrSet__Clear` on the pointer at `EBP-0x10`. |
| `0x005d1320 Unwind@005d1320` | `void __cdecl Unwind@005d1320(void)` | Scope-table DATA xref `0x0061a19c`; calls `CSPtrSet__Clear` on the pointer at `EBP-0x10`. |
| `0x005d1340 Unwind@005d1340` | `void __cdecl Unwind@005d1340(void)` | Scope-table DATA xref `0x0061a1c4`; calls `CSPtrSet__Clear` on the pointer at `EBP-0x10`. |
| `0x005d1360 Unwind@005d1360` | `void __cdecl Unwind@005d1360(void)` | Boat.cpp path `0x00623990`, line `0x1e`, memtype `0x17`, and scope-table DATA xref `0x0061a1ec`; frees the pointer at `EBP+4`. |
| `0x005d1376 Unwind@005d1376` | `void __cdecl Unwind@005d1376(void)` | Boat.cpp path `0x00623990`, line `0x1f`, memtype `0x16`, and scope-table DATA xref `0x0061a1f4`; frees the pointer at `EBP+4`. |
| `0x005d13a0 Unwind@005d13a0` | `void __cdecl Unwind@005d13a0(void)` | Scope-table DATA xref `0x0061a21c`; calls `CMonitor__Shutdown` on `EBP-0x10`. |
| `0x005d13a8 Unwind@005d13a8` | `void __cdecl Unwind@005d13a8(void)` | Scope-table DATA xref `0x0061a224`; calls `CGenericActiveReader__dtor` on object field `EBP-0x10 + 0xc`. |
| `0x005d13b3 Unwind@005d13b3` | `void __cdecl Unwind@005d13b3(void)` | Scope-table DATA xref `0x0061a22c`; calls `CGenericActiveReader__dtor` on object field `EBP-0x10 + 0x24`. |

Validation evidence:

- Dry/apply/final dry reported `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`, then `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`, then final dry `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post exports verified `25` metadata rows, `25` tag rows, `25` xref rows, `575` instruction rows, and `25` decompile rows.
- Queue refresh passed with `6098` total functions, `4411` commented, `1687` commentless, `1164` exact-undefined signatures, `27` `param_N` signatures, comment-backed proxy `4411/6098 = 72.34%`, and strict clean-signature proxy `4353/6098 = 71.39%`.
- Earliest raw commentless row is `0x0042f220 CSPtrSet__Clear`; next commentless high-signal row is `0x005d13d0 Unwind@005d13d0`.
- Verified backup: `G:\GhidraBackups\BEA_20260522-153147_post_wave742_unwind_continuation_verified`, `19` files, `167152519` bytes, `DiffCount=0`.

Scope boundary: this wave proves saved static retail Ghidra metadata only. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave742 unwind continuation`, `unwind-continuation-wave742`, `0x005d1170 Unwind@005d1170`, `0x005d11f0 Unwind@005d11f0`, `0x005d1220 Unwind@005d1220`, `0x005d1360 Unwind@005d1360`, `0x005d13b3 Unwind@005d13b3`, `0x005d13d0 Unwind@005d13d0`, `0x0042f220 CSPtrSet__Clear`, `G:\GhidraBackups\BEA_20260522-153147_post_wave742_unwind_continuation_verified`.
