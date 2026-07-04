# Ghidra DataType String/Thing/Position Tail Wave576 Readiness Note

Date: 2026-05-19
Status: PASS

## Scope

Wave576 hardened thirteen saved Ghidra rows in the retail MissionScript datatype string, thing-pointer, base-destructor, and position tail cluster:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x0052f2c0` | `void * __thiscall CStringDataType__Clone(void * this)` | CString clone slot at data pointer `0x005e4e94`; allocates an 8-byte string datatype, installs vtable `0x005e4e4c`, allocates a buffer sized from `this+0x04`, copies the string, and null-terminates the clone buffer. |
| `0x0052f360` | `bool __thiscall CStringDataType__Equals(void * this, void * rhs)` | String equality slot at data pointer `0x005e4e64`; `RET 0x4`, rhs read through datatype vtable slot `+0x38`, then bytewise comparison with the string pointer at `this+0x04`. |
| `0x0052f430` | `void __thiscall CStringDataType__Print(void * this, void * rhs)` | Print/reader bridge observed at data pointer `0x005e4e0c`; `RET 0x4`, rhs reader cell returned through slot `+0x40`, then passed to `CGenericActiveReader__SetReader` for the string field at `this+0x04`. |
| `0x0052f470` | `void * __thiscall CThingPtrDataType__Clone(void * this)` | Thing-pointer clone slot at data pointer `0x005e4e40`; allocates an 8-byte thing-pointer datatype, copies `this+0x04`, creates/registers a `CSPtrSet` entry when needed, and installs vtable `0x005e4df8`. |
| `0x0052f550` | `void * __thiscall CThingPtrDataType__ScalarDeletingDestructor(void * this, byte flags)` | `CThingPtrDataType` scalar-deleting destructor at vtable `0x005e4df8`; calls `CThingPtrDataType__Destructor` and frees `this` when `flags&1` is set. |
| `0x0052f570` | `void __thiscall CThingPtrDataType__Destructor(void * this)` | Thing-pointer destructor; removes `this+0x04` from the pointed object's `CSPtrSet` when present and restores base vtable pointer `0x005e4b4c`. |
| `0x0052f670` | `void * __thiscall CDataType__ScalarDeletingDestructor(void * this, byte flags)` | Shared scalar-deleting destructor wrapper reused by CInt, CFloat, CBool, and CPosition vtable heads; calls `CDataType__Destructor` and frees `this` when `flags&1` is set. |
| `0x0052f690` | `void * __thiscall CStringDataType__InitFromString(void * this, char * source_text)` | CString constructor/init helper called from MissionScript string-return sites; installs vtable `0x005e4e4c`, allocates/copies `source_text`, null-terminates it, and returns `this`. |
| `0x0052f720` | `void * __thiscall CStringDataType__ScalarDeletingDestructor(void * this, byte flags)` | CString scalar-deleting destructor at vtable `0x005e4e4c`; calls `CStringDataType__Destructor` and frees `this` when `flags&1` is set. |
| `0x0052f740` | `void __thiscall CStringDataType__Destructor(void * this)` | CString destructor; frees the string buffer at `this+0x04` and restores base vtable pointer `0x005e4b4c`. |
| `0x0052f790` | `void * __thiscall CStringDataType__ReadFromBuffer(void * this, void * bytecode_reader)` | CString buffer-read helper called from `CWorld__LoadScriptEvents` and `CScriptObjectCode__ReadSymbolTable`; reads a 4-byte length, allocates `length+1`, reads bytes, and appends a null terminator. |
| `0x0052f8a0` | `void * __thiscall CPositionDataType__SubtractPosition(void * this, void * rhs)` | Position subtract slot at data pointer `0x005e4dac`; rhs read through slot `+0x44`, allocates a 0x14-byte CPosition object, installs vtable `0x005e4da4`, and stores observed x/y/z differences. |
| `0x0052f920` | `void * __thiscall CPositionDataType__ScaleByFloat(void * this, void * rhs)` | Position scale slot at data pointer `0x005e4db0`; rhs float read through slot `+0x34`, allocates a 0x14-byte CPosition object, installs vtable `0x005e4da4`, and stores observed x/y/z scaled values. |

No `source-parity` tag was applied. This tranche is bounded to saved retail binary evidence; runtime MissionScript behavior, exact datatype layouts beyond observed fields, trailing CPosition dword semantics, exact source identity, BEA patching, and rebuild parity remain deferred.

## Verification

- Dry pass: `updated=0 skipped=13 renamed=0 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Apply pass: `updated=13 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Final dry: `updated=0 skipped=13 renamed=0 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Post exports: `13` metadata rows, `13` tag rows, `26` xref rows, `2977` target instruction rows, `13` target decompiles, and `384` datatype-vtable rows
- Focused probe: `py -3 tools\ghidra_datatype_string_thing_position_tail_wave576_probe.py --check` PASS
- Npm wrapper: `cmd.exe /c npm run test:ghidra-datatype-string-thing-position-tail-wave576` PASS
- Queue refresh: `6093` total functions, `2917` commented, `3176` commentless, `1430` exact-undefined signatures, `1139` `param_N` signatures
- Post-Wave576 comment-backed proxy: `2917 / 6093 = 47.87%`
- Post-Wave576 strict clean-signature proxy: `2866 / 6093 = 47.04%`
- Next queue head: `0x0052f9a0 CEventFunction__Destructor`
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-023729_post_wave576_datatype_string_thing_position_tail_verified`
- Backup verification: `19` files, `160402311` bytes, source/destination manifest hash `9A6A9EEF1378754A0E241C8EDF1871EB9F4AC3D6A9A33928CB5922E10C3BE0BC`

## Limits

This is saved static Ghidra evidence only. No runtime MissionScript behavior was claimed. Exact datatype layouts beyond observed fields, trailing position-vector dword semantics, exact source identity, BEA launch behavior, game patching, and rebuild parity remain unproven.
