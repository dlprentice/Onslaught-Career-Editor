# Ghidra DataType Factory/Float Head Wave575 Readiness Note

Date: 2026-05-19
Status: PASS

## Scope

Wave575 hardened twelve saved Ghidra rows in the retail MissionScript datatype factory/float cluster:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x0052ec60` | `void * __cdecl CDataType__CreateFromType(int type_id, void * bytecode_reader)` | Factory called from `CScriptObjectCode__ReadSymbolTable`; switches serialized `type_id` 1..6, allocates a datatype object, installs the observed vtable, and reads initial payload bytes from `bytecode_reader`. Observed mapping is type 1 -> `CIntDataType` vtable `0x005e4af8`, type 2 -> `CFloatDataType` vtable `0x005e4ea4`, type 3 -> `CStringDataType` vtable `0x005e4e4c`, type 4 -> observed `CBoolDataType` region `0x005e4d50`, type 5 -> `CThingPtrDataType` vtable `0x005e4df8`, and type 6 -> `CPositionDataType` vtable `0x005e4da4`. |
| `0x0052ef50` | `void * __thiscall CFloatDataType__Add(void * this, void * rhs)` | Float add vtable slot at data pointer `0x005e4ea8`; reads rhs through datatype vtable slot `+0x34`, allocates an 8-byte `CFloatDataType`, installs vtable `0x005e4ea4`, and stores the sum. |
| `0x0052efc0` | `void * __thiscall CFloatDataType__Subtract(void * this, void * rhs)` | Float subtract vtable slot at data pointer `0x005e4eac`; reads rhs through slot `+0x34`, allocates an 8-byte `CFloatDataType`, and stores `this+0x04 - rhs`. |
| `0x0052f030` | `void * __thiscall CFloatDataType__Multiply(void * this, void * rhs)` | Float multiply vtable slot at data pointer `0x005e4eb0`; reads rhs through slot `+0x34`, allocates an 8-byte `CFloatDataType`, and stores the product. |
| `0x0052f0a0` | `void * __thiscall CFloatDataType__Divide(void * this, void * rhs)` | Float divide vtable slot at data pointer `0x005e4eb4`; reads rhs through slot `+0x34`, allocates an 8-byte `CFloatDataType`, and stores `this+0x04 / rhs`. |
| `0x0052f110` | `bool __thiscall CFloatDataType__Equals(void * this, void * rhs)` | Float equality slot at data pointer `0x005e4ebc`; reads rhs through slot `+0x34` and compares against the float at `this+0x04`. |
| `0x0052f140` | `bool __thiscall CFloatDataType__NotEquals(void * this, void * rhs)` | Float inequality slot at data pointer `0x005e4ec0`; reads rhs through slot `+0x34` and compares against `this+0x04`. |
| `0x0052f170` | `void __thiscall CFloatDataType__Assign(void * this, void * rhs)` | Float assignment slot at data pointer `0x005e4eb8`; reads rhs through slot `+0x34` and stores the returned float at `this+0x04`. |
| `0x0052f190` | `bool __thiscall CFloatDataType__LessThan(void * this, void * rhs)` | Float less-than slot at data pointer `0x005e4ec4`; returns whether `this+0x04 < rhs`. |
| `0x0052f1c0` | `bool __thiscall CFloatDataType__GreaterThan(void * this, void * rhs)` | Float greater-than slot at data pointer `0x005e4ec8`; returns whether `this+0x04 > rhs`. |
| `0x0052f1f0` | `bool __thiscall CFloatDataType__LessOrEqual(void * this, void * rhs)` | Float less-or-equal slot at data pointer `0x005e4ecc`; returns whether `this+0x04 <= rhs`. |
| `0x0052f220` | `bool __thiscall CFloatDataType__GreaterOrEqual(void * this, void * rhs)` | Float greater-or-equal slot at data pointer `0x005e4ed0`; returns whether `this+0x04 >= rhs`. |

No `source-parity` tag was applied. This tranche is bounded to saved retail binary evidence; runtime MissionScript behavior, exact datatype layouts beyond observed fields, exact type enum names, source identity, BEA patching, and rebuild parity remain deferred.

## Verification

- Dry pass: `updated=0 skipped=12 renamed=0 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Apply pass: `updated=12 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Final dry: `updated=0 skipped=12 renamed=0 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Post exports: `12` metadata rows, `12` tag rows, `12` xref rows, `2748` target instruction rows, `12` target decompiles, and `384` datatype-vtable rows
- Focused probe: `py -3 tools\ghidra_datatype_factory_float_head_wave575_probe.py --check` PASS
- Npm wrapper: `cmd.exe /c npm run test:ghidra-datatype-factory-float-head-wave575` PASS
- Queue refresh: `6093` total functions, `2904` commented, `3189` commentless, `1443` exact-undefined signatures, `1139` `param_N` signatures
- Post-Wave575 comment-backed proxy: `2904 / 6093 = 47.66%`
- Post-Wave575 strict clean-signature proxy: `2853 / 6093 = 46.82%`
- Next queue head: `0x0052f2c0 CStringDataType__Clone`
- Backup: `G:\GhidraBackups\BEA_20260519-020812_post_wave575_datatype_factory_float_head_verified`
- Backup verification: `19` files, `160369543` bytes, source/destination manifest hash `DF7C8BD3CCAE9DD1C8FBE58FD8D25CE789E793765732D46BC850ABF9D9629079`

## Limits

This is saved static Ghidra evidence only. No runtime MissionScript behavior was claimed. Exact datatype layouts beyond observed fields, exact type enum names, allocator/free ownership, source identity, BEA launch behavior, game patching, and rebuild parity remain unproven. The factory/type-id table is now corrected in docs for the observed retail mapping, but that does not prove original source enum spelling.
