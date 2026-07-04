# Ghidra Unwind Continuation Wave743 Readiness Note

Status: passed
Date: 2026-05-22

Wave743 unwind continuation saved comments/tags/signatures for twenty-five adjacent compiler-generated SEH unwind cleanup callbacks with the `unwind-continuation-wave743` and `wave743-readback-verified` tags. The pass hardened twenty-five `void __cdecl Unwind@...(void)` signatures, made no renames, made no function-boundary changes, and made no executable-byte changes.

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x005d13d0 Unwind@005d13d0` | `void __cdecl Unwind@005d13d0(void)` | Scope-table DATA xref `0x0061a254`; calls `CMonitor__Shutdown` on `EBP-0x10`. |
| `0x005d13d8 Unwind@005d13d8` | `void __cdecl Unwind@005d13d8(void)` | Scope-table DATA xref `0x0061a25c`; calls `CGenericActiveReader__dtor` on object field `EBP-0x10 + 0xc`. |
| `0x005d13e3 Unwind@005d13e3` | `void __cdecl Unwind@005d13e3(void)` | Scope-table DATA xref `0x0061a264`; calls `CGenericActiveReader__dtor` on object field `EBP-0x10 + 0x24`. |
| `0x005d1400 Unwind@005d1400` | `void __cdecl Unwind@005d1400(void)` | Bomber.cpp path `0x00623a78`, line `0x11`, memtype `0x17`, and scope-table DATA xref `0x0061a28c`; frees the pointer at `EBP+4`. |
| `0x005d1416 Unwind@005d1416` | `void __cdecl Unwind@005d1416(void)` | Bomber.cpp path `0x00623a78`, line `0x12`, memtype `0x16`, and scope-table DATA xref `0x0061a294`; frees the pointer at `EBP+4`. |
| `0x005d1440 Unwind@005d1440` | `void __cdecl Unwind@005d1440(void)` | Scope-table DATA xref `0x0061a2bc`; calls `CMonitor__Shutdown` on `EBP-0x10`. |
| `0x005d1448 Unwind@005d1448` | `void __cdecl Unwind@005d1448(void)` | Scope-table DATA xref `0x0061a2c4`; calls `CGenericActiveReader__dtor` on object field `EBP-0x10 + 0xc`. |
| `0x005d1453 Unwind@005d1453` | `void __cdecl Unwind@005d1453(void)` | Scope-table DATA xref `0x0061a2cc`; calls `CGenericActiveReader__dtor` on object field `EBP-0x10 + 0x24`. |
| `0x005d1470 Unwind@005d1470` | `void __cdecl Unwind@005d1470(void)` | Scope-table DATA xref `0x0061a2f4`; calls `CMonitor__Shutdown_Thunk` on `EBP-0x10`. |
| `0x005d1490 Unwind@005d1490` | `void __cdecl Unwind@005d1490(void)` | Building.cpp path `0x00623af4`, line `0x32`, memtype `0x80`, and scope-table DATA xref `0x0061a31c`; frees the pointer at `EBP+4`. |
| `0x005d14a9 Unwind@005d14a9` | `void __cdecl Unwind@005d14a9(void)` | Building.cpp path `0x00623af4`, line `0x33`, memtype `0x80`, and scope-table DATA xref `0x0061a324`; frees the pointer at `EBP+4`. |
| `0x005d14d0 Unwind@005d14d0` | `void __cdecl Unwind@005d14d0(void)` | Building.cpp path `0x00623af4`, line `0x64`, memtype `0x16`, and scope-table DATA xref `0x0061a34c`; frees the pointer at `EBP-0x10`. |
| `0x005d14e6 Unwind@005d14e6` | `void __cdecl Unwind@005d14e6(void)` | Building.cpp path `0x00623af4`, line `0x68`, memtype `0x16`, and scope-table DATA xref `0x0061a354`; frees the pointer at `EBP-0x10`. |
| `0x005d1510 Unwind@005d1510` | `void __cdecl Unwind@005d1510(void)` | Scope-table DATA xref `0x0061a37c`; calls `CMonitor__Shutdown` on `EBP-0x10`. |
| `0x005d1518 Unwind@005d1518` | `void __cdecl Unwind@005d1518(void)` | Scope-table DATA xref `0x0061a384`; calls `CGenericActiveReader__dtor` on object field `EBP-0x10 + 0xc`. |
| `0x005d1523 Unwind@005d1523` | `void __cdecl Unwind@005d1523(void)` | Scope-table DATA xref `0x0061a38c`; calls `CGenericActiveReader__dtor` on object field `EBP-0x10 + 0x24`. |
| `0x005d1540 Unwind@005d1540` | `void __cdecl Unwind@005d1540(void)` | Scope-table DATA xref `0x0061a3b4`; calls `CResourceDescriptor__dtor` on stack local `EBP-0x5b8`. |
| `0x005d1560 Unwind@005d1560` | `void __cdecl Unwind@005d1560(void)` | Scope-table DATA xref `0x0061a3dc`; calls `CParticleManager__RemoveFromGlobalList_Thunk` on stack local `EBP-0x404`. |
| `0x005d1580 Unwind@005d1580` | `void __cdecl Unwind@005d1580(void)` | Scope-table DATA xref `0x0061a404`; calls `CDXMemBuffer__dtor_base` on stack local `EBP-0x140`. |
| `0x005d158b Unwind@005d158b` | `void __cdecl Unwind@005d158b(void)` | bytesprite.cpp path `0x00623c18`, line `0x1d`, memtype `0x61`, and scope-table DATA xref `0x0061a40c`; frees the pointer at `EBP-0x164`. |
| `0x005d15b0 Unwind@005d15b0` | `void __cdecl Unwind@005d15b0(void)` | Scope-table DATA xref `0x0061a434`; calls `CGenericCamera__dtor` on the pointer at `EBP-0x14`. |
| `0x005d15b8 Unwind@005d15b8` | `void __cdecl Unwind@005d15b8(void)` | Scope-table DATA xref `0x0061a43c`; calls `CGenericActiveReader__dtor` on the pointer at `EBP-0x10`. |
| `0x005d15c0 Unwind@005d15c0` | `void __cdecl Unwind@005d15c0(void)` | Scope-table DATA xref `0x0061a444`; calls `CGenericActiveReader__dtor` on object field `EBP-0x14 + 0x4`. |
| `0x005d15cb Unwind@005d15cb` | `void __cdecl Unwind@005d15cb(void)` | Camera.cpp path `0x00623c90`, line `0x9e`, memtype `0x28`, and scope-table DATA xref `0x0061a44c`; frees the pointer at `EBP+4`. |
| `0x005d15e4 Unwind@005d15e4` | `void __cdecl Unwind@005d15e4(void)` | Camera.cpp path `0x00623c90`, line `0xa9`, memtype `0x26`, and scope-table DATA xref `0x0061a454`; frees the pointer at `EBP+4`. |

Validation evidence:

- Dry/apply/final dry reported `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`, then `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`, then final dry `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post exports verified `25` metadata rows, `25` tag rows, `25` xref rows, `575` instruction rows, and `25` decompile rows.
- Queue refresh passed with `6098` total functions, `4436` commented, `1662` commentless, `1139` exact-undefined signatures, `27` `param_N` signatures, comment-backed proxy `4436/6098 = 72.75%`, and strict clean-signature proxy `4378/6098 = 71.80%`.
- Earliest raw commentless row is `0x0042f220 CSPtrSet__Clear`; next commentless high-signal row is `0x005d1610 Unwind@005d1610`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-160155_post_wave743_unwind_continuation_verified`, `19` files, `167250823` bytes, `DiffCount=0`.

Scope boundary: this wave proves saved static retail Ghidra metadata only. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave743 unwind continuation`, `unwind-continuation-wave743`, `0x005d13d0 Unwind@005d13d0`, `0x005d1400 Unwind@005d1400`, `0x005d1490 Unwind@005d1490`, `0x005d158b Unwind@005d158b`, `0x005d15e4 Unwind@005d15e4`, `0x005d1610 Unwind@005d1610`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-160155_post_wave743_unwind_continuation_verified`.
