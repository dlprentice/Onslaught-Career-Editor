# Wave581 IScript Vector/Range Static Read-Back

Date: 2026-05-19

Scope: static Ghidra metadata hardening for five adjacent IScript vector/range command handlers:

| Address | Handler | Saved signature | Static evidence |
| --- | --- | --- | --- |
| `0x005345d0` | `IScript__GetVectorLength` | `void __stdcall IScript__GetVectorLength(void * script_args, void * unused_state, void * out_result)` | `RET 0xc`; registered by `ScriptCommandRegistry__InitBuiltins`; reads vector through datatype vtable slot `+0x44`; computes `sqrt(x*x+y*y+z*z)`; returns a float result using vtable `0x005e4ea4`. |
| `0x005347b0` | `IScript__CheckValueInRange` | `void __stdcall IScript__CheckValueInRange(void * script_args, void * unused_state, void * out_result)` | `RET 0xc`; reads value/min/max through float getter slot `+0x34`; accepts ascending and descending bound order; returns a boolean byte result. |
| `0x00534b80` | `IScript__GetVectorX` | `void __stdcall IScript__GetVectorX(void * script_args, void * unused_state, void * out_result)` | Reads vector through slot `+0x44`; copies component offset `+0`; returns a float result using vtable `0x005e4ea4`. |
| `0x00534c10` | `IScript__GetVectorY` | `void __stdcall IScript__GetVectorY(void * script_args, void * unused_state, void * out_result)` | Reads vector through slot `+0x44`; copies component offset `+4`; returns a float result using vtable `0x005e4ea4`. |
| `0x00534ca0` | `IScript__GetVectorZ` | `void __stdcall IScript__GetVectorZ(void * script_args, void * unused_state, void * out_result)` | Reads vector through slot `+0x44`; copies component offset `+8`; returns a float result using vtable `0x005e4ea4`. |

Read-back evidence:

- `ApplyIScriptVectorRangeWave581.java` dry/apply/final dry reported `updated=0 skipped=5 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=5 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=5 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post exports verified `5` metadata rows, `5` tag rows, `5` xref rows, `3545` target instruction rows, `5` decompile rows, and `24` vtable rows.
- Queue refresh after Wave581: `6093` total functions, `2944` commented, `3149` commentless, `1413` exact-undefined signatures, `1127` `param_N` signatures, comment-backed proxy `2944/6093 = 48.32%`, and strict clean-signature proxy `2895/6093 = 47.51%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-075959_post_wave581_iscript_vector_range_verified`, `19` files, `160500615` bytes, `DiffCount=0`, manifest hash `66EAC6D25839E7626D5F27E6A496E682085E0169D2D38E22BAD8E61E00E4F687`.

Not proven:

- runtime mission-script behavior remains unproven.
- script corpus coverage remains unproven.
- Exact command descriptor layout, exact vector layout naming beyond observed offsets, BEA patching, and rebuild parity remain unproven.

Next queue head: `0x00534fb0 IScript__SetThingValueViaVFunc198_FromArg`.
