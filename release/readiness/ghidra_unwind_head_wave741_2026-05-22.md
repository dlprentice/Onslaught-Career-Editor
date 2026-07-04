# Ghidra Unwind Head Wave741 Readiness Note

Status: passed
Date: 2026-05-22

Wave741 unwind head saved comments/tags/signatures for twenty-five adjacent compiler-generated SEH unwind cleanup callbacks with the `unwind-head-wave741` and `wave741-readback-verified` tags. The pass hardened twenty-five `void __cdecl Unwind@...(void)` signatures, made no renames, made no function-boundary changes, and made no executable-byte changes.

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x005d0f10 Unwind@005d0f10` | `void __cdecl Unwind@005d0f10(void)` | Scope-table DATA xref `0x00619e04`; decompile/instruction evidence calls `OID__FreeObject_Callback` on `EBP-0x10` with Monitor.h path `0x00622b80`, line `0x18`, and memtype `0x5e`. |
| `0x005d0f30 Unwind@005d0f30` | `void __cdecl Unwind@005d0f30(void)` | Scope-table DATA xref `0x00619e2c`; forwards `EBP-0x10` to `CMonitor__Shutdown_Thunk`. |
| `0x005d0f38 Unwind@005d0f38` | `void __cdecl Unwind@005d0f38(void)` | Scope-table DATA xref `0x00619e34`; calls `CGenericActiveReader__dtor` on the embedded reader at `EBP-0x10 + 0x2c`. |
| `0x005d0f50 Unwind@005d0f50` | `void __cdecl Unwind@005d0f50(void)` | Scope-table DATA xref `0x00619e5c`; forwards `EBP-0x10` to `CMonitor__Shutdown_Thunk`. |
| `0x005d0f70 Unwind@005d0f70` | `void __cdecl Unwind@005d0f70(void)` | AirUnit.cpp path `0x00622cf4`, line `0x2a`, memtype `0x10`, and scope-table DATA xref `0x00619e84`; frees the pointer at `EBP-0x80`. |
| `0x005d0f86 Unwind@005d0f86` | `void __cdecl Unwind@005d0f86(void)` | AirUnit.cpp path `0x00622cf4`, line `0x36`, memtype `0x10`, and scope-table DATA xref `0x00619e8c`; frees the pointer at `EBP-0x80`. |
| `0x005d0fb0 Unwind@005d0fb0` | `void __cdecl Unwind@005d0fb0(void)` | Scope-table DATA xref `0x00619eb4`; calls `CDXLandscape__DestroyResourceDescriptorArray_Thunk` on stack-local descriptor array `EBP-0x434`. |
| `0x005d0fd0 Unwind@005d0fd0` | `void __cdecl Unwind@005d0fd0(void)` | Scope-table DATA xref `0x00619edc`; calls `CMonitor__Shutdown` on `EBP-0x10`. |
| `0x005d0ff0 Unwind@005d0ff0` | `void __cdecl Unwind@005d0ff0(void)` | Atmospherics.cpp path `0x00622ec4`, line `0x70`, memtype `0x65`, and scope-table DATA xref `0x00619f04`; frees the pointer at `EBP-0x10`. |
| `0x005d1006 Unwind@005d1006` | `void __cdecl Unwind@005d1006(void)` | Atmospherics.cpp path `0x00622ec4`, line `0x73`, memtype `0x65`, and scope-table DATA xref `0x00619f0c`; frees the pointer at `EBP-0x10`. |
| `0x005d1030 Unwind@005d1030` | `void __cdecl Unwind@005d1030(void)` | BattleEngine.cpp path `0x006230bc`, line `0x63`, memtype `0x15`, and scope-table DATA xref `0x00619f34`; frees the pointer at `EBP-0x490`. |
| `0x005d1049 Unwind@005d1049` | `void __cdecl Unwind@005d1049(void)` | BattleEngine.cpp path `0x006230bc`, line `0x64`, memtype `0x15`, and scope-table DATA xref `0x00619f3c`; frees the pointer at `EBP-0x490`. |
| `0x005d1062 Unwind@005d1062` | `void __cdecl Unwind@005d1062(void)` | Scope-table DATA xref `0x00619f44`; calls `CDXLandscape__DestroyResourceDescriptorArray_Thunk` on stack-local descriptor array `EBP-0x434`. |
| `0x005d106d Unwind@005d106d` | `void __cdecl Unwind@005d106d(void)` | BattleEngine.cpp path `0x006230bc`, line `0xb1`, memtype `0x10`, and scope-table DATA xref `0x00619f4c`; frees the pointer at `EBP-0x490`. |
| `0x005d1089 Unwind@005d1089` | `void __cdecl Unwind@005d1089(void)` | BattleEngine.cpp path `0x006230bc`, line `0xbd`, memtype `0x10`, and scope-table DATA xref `0x00619f54`; frees the pointer at `EBP-0x490`. |
| `0x005d10a5 Unwind@005d10a5` | `void __cdecl Unwind@005d10a5(void)` | BattleEngine.cpp path `0x006230bc`, line `0xc8`, memtype `0x15`, and scope-table DATA xref `0x00619f5c`; frees the pointer at `EBP-0x490`. |
| `0x005d10c1 Unwind@005d10c1` | `void __cdecl Unwind@005d10c1(void)` | BattleEngine.cpp path `0x006230bc`, line `0x1f5`, memtype `0x15`, and scope-table DATA xref `0x00619f64`; frees the pointer at `EBP-0x47c`. |
| `0x005d10dd Unwind@005d10dd` | `void __cdecl Unwind@005d10dd(void)` | BattleEngine.cpp path `0x006230bc`, line `0x108`, memtype `0x15`, and scope-table DATA xref `0x00619f6c`; frees the pointer at `EBP-0x47c`. |
| `0x005d10f9 Unwind@005d10f9` | `void __cdecl Unwind@005d10f9(void)` | BattleEngine.cpp path `0x006230bc`, line `0x124`, memtype `0x15`, and scope-table DATA xref `0x00619f74`; frees the pointer at `EBP-0x47c`. |
| `0x005d1115 Unwind@005d1115` | `void __cdecl Unwind@005d1115(void)` | BattleEngine.cpp path `0x006230bc`, scope-table DATA xref `0x00619f7c`; forwards `EBP-0x47c` to `CMonitor__Shutdown_Thunk`. |
| `0x005d1130 Unwind@005d1130` | `void __cdecl Unwind@005d1130(void)` | Scope-table DATA xref `0x00619fa4`; calls `CUnit__dtor_base` on `EBP-0x10`. |
| `0x005d1138 Unwind@005d1138` | `void __cdecl Unwind@005d1138(void)` | Scope-table DATA xref `0x00619fac`; calls `CSPtrSet__Clear` on object field `EBP-0x10 + 0x250`. |
| `0x005d1146 Unwind@005d1146` | `void __cdecl Unwind@005d1146(void)` | Scope-table DATA xref `0x00619fb4`; calls `CGenericActiveReader__dtor` on object field `EBP-0x10 + 0x264`. |
| `0x005d1154 Unwind@005d1154` | `void __cdecl Unwind@005d1154(void)` | Scope-table DATA xref `0x00619fbc`; calls `CSPtrSet__Clear` on object field `EBP-0x10 + 0x284`. |
| `0x005d1162 Unwind@005d1162` | `void __cdecl Unwind@005d1162(void)` | Scope-table DATA xref `0x00619fc4`; calls `CSPtrSet__Clear` on object field `EBP-0x10 + 0x294`. |

Validation evidence:

- Dry/apply/final dry reported `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`, then `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`, then final dry `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post exports verified `25` metadata rows, `25` tag rows, `25` xref rows, `525` instruction rows, and `25` decompile rows.
- Queue refresh passed with `6098` total functions, `4386` commented, `1712` commentless, `1189` exact-undefined signatures, `27` `param_N` signatures, comment-backed proxy `4386/6098 = 71.93%`, and strict clean-signature proxy `4328/6098 = 70.97%`.
- Earliest raw commentless row is `0x0042f220 CSPtrSet__Clear`; next commentless high-signal row is `0x005d1170 Unwind@005d1170`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-150238_post_wave741_unwind_head_verified`, `19` files, `167086983` bytes, `DiffCount=0`.

Scope boundary: this wave proves saved static retail Ghidra metadata only. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave741 unwind head`, `unwind-head-wave741`, `0x005d0f10 Unwind@005d0f10`, `0x005d0f70 Unwind@005d0f70`, `0x005d0ff0 Unwind@005d0ff0`, `0x005d1030 Unwind@005d1030`, `0x005d1162 Unwind@005d1162`, `0x005d1170 Unwind@005d1170`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-150238_post_wave741_unwind_head_verified`.
