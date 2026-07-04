# Ghidra CVM Stack Cleanup Wave583 Readiness

Status: validated static Ghidra read-back
Date: 2026-05-19

Wave583 CVM stack cleanup static read-back hardened two CVM stack cleanup functions: `CVM__ScalarDeletingDestructor` at `0x00535330` and `CVM__Destructor` at `0x00535350`.

Read-back evidence:

| Check | Result |
| --- | --- |
| Dry/apply/final dry | `updated=0 skipped=2 renamed=0 would_rename=2`, then `updated=2 skipped=0 renamed=2`, then `updated=0 skipped=2 renamed=0 would_rename=0`, all with `missing=0 bad=0` and `REPORT: Save succeeded` |
| Post exports | `2` metadata rows, `2` tag rows, `3` xref rows, `242` instruction rows, `2` decompile rows, `32` vtable rows |
| Queue refresh | `6093` functions, `2952` commented, `3141` commentless, `1413` exact-undefined signatures, `1119` `param_N`; next head `0x00535670 IScript__GetThingName` |
| Backup | `[maintainer-local-ghidra-backup-root]\BEA_20260519-085219_post_wave583_cvm_stack_verified`, `19` files, `160598919` bytes, `DiffCount=0`, manifest hash `df7a59131010926f91ea16643abbe7ffe32ab125d1a4423b54e9dfe5e0d27cab` |

Bounded claims:

- `CVM__ScalarDeletingDestructor` is the saved vtable-slot wrapper reached from `0x005e4f20`; it calls `CVM__Destructor(this)`, tests `flags&1`, frees `this` via `CDXMemoryManager__Free(&DAT_009c3df0,this)` when set, returns `this`, and ends with `RET 0x4`.
- `CVM__Destructor` is the saved destructor body called by the wrapper and raw callsite `0x005398c5`; instruction read-back shows `LEA ECX, [ESI + 0xc]` before `CScriptObjectCode__ClearStack`, then `CMonitor__Shutdown(this)`.

Not proven:

- runtime mission-script behavior remains unproven.
- exact CVM source class identity/layout remains unproven.
- Exception-handler semantics, full vtable recovery, BEA patching, and rebuild parity remain deferred.
