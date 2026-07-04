# Ghidra Script/DataType Head Wave573 Readiness Note

Date: 2026-05-19
Status: PASS

## Scope

Wave573 hardened fourteen saved Ghidra rows in the retail MissionScript/DataType head cluster:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x0052d040` | `void * __stdcall CAsmInstruction__GetAttributeValue(void * instruction)` | `RET 0x4` confirms one stack argument; OP_PUSH uses this helper to read instruction attribute data, clone it through vtable slot `+0x48`, or allocate a zero-valued `CIntDataType` fallback after the no-data-set fatal string. |
| `0x0052d0a0` | `void * __thiscall CIntDataType__Add(void * this, void * rhs)` | CInt vtable arithmetic slot: reads `rhs` through vtable slot `+0x30`, allocates an 8-byte `CIntDataType`, and stores `this+0x04 + rhs`. |
| `0x0052d110` | `void * __thiscall CIntDataType__Subtract(void * this, void * rhs)` | CInt vtable arithmetic slot: reads `rhs` through slot `+0x30`, allocates a new CInt object, and stores `this+0x04 - rhs`. |
| `0x0052d180` | `void * __thiscall CIntDataType__Multiply(void * this, void * rhs)` | CInt vtable arithmetic slot: reads `rhs` through slot `+0x30`, allocates a new CInt object, and stores the product. |
| `0x0052d1f0` | `void * __thiscall CIntDataType__Divide(void * this, void * rhs)` | CInt vtable arithmetic slot: reads `rhs` through slot `+0x30`, allocates a new CInt object, and stores `this+0x04 / rhs`; divide-by-zero behavior remains runtime-unproven. |
| `0x0052d260` | `bool __thiscall CIntDataType__Equals(void * this, void * rhs)` | CInt comparison slot returning whether `this+0x04 == rhs_value`. |
| `0x0052d280` | `bool __thiscall CIntDataType__NotEquals(void * this, void * rhs)` | CInt comparison slot returning whether `this+0x04 != rhs_value`. |
| `0x0052d2a0` | `void __thiscall CIntDataType__Assign(void * this, void * rhs)` | Assignment slot that reads `rhs` through vtable slot `+0x30` and stores the returned integer at `this+0x04`. |
| `0x0052d2c0` | `bool __thiscall CIntDataType__LessThan(void * this, void * rhs)` | CInt comparison slot returning whether `this+0x04 < rhs_value`. |
| `0x0052d2e0` | `bool __thiscall CIntDataType__GreaterThan(void * this, void * rhs)` | CInt comparison slot returning whether `this+0x04 > rhs_value`. |
| `0x0052d300` | `bool __thiscall CIntDataType__LessOrEqual(void * this, void * rhs)` | CInt comparison slot returning whether `this+0x04 <= rhs_value`. |
| `0x0052d320` | `bool __thiscall CIntDataType__GreaterOrEqual(void * this, void * rhs)` | CInt comparison slot returning whether `this+0x04 >= rhs_value`. |
| `0x0052d390` | `void __thiscall CDataType__Destructor(void * this)` | Base destructor reached by the scalar-deleting destructor and unwind cleanups; it restores the base `CDataType` vtable pointer. |
| `0x0052d3d0` | `void * __cdecl CAsmInstruction__SpawnFromOpcode(int opcode, void * bytecode_reader)` | Bytecode opcode factory called by `CScriptObjectCode` construction; it reads an attribute dword from the bytecode reader, allocates 0x0c-byte instruction records, installs opcode-specific vtables, and reports an unknown-instruction fatal string on unsupported opcodes. |

No `source-parity` tag was applied. This tranche is bounded to saved retail binary evidence; runtime MissionScript behavior, exact opcode enum, exact data-type/instruction layouts, exact source identity, BEA patching, and rebuild parity remain deferred.

## Verification

- Dry pass: `updated=0 skipped=14 renamed=0 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Apply pass: `updated=14 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Final dry: `updated=0 skipped=14 renamed=0 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Post exports: `14` metadata rows, `14` tag rows, `34` xref rows, `2254` target instruction rows, and `14` target decompiles
- Focused probe: `py -3 tools\ghidra_script_datatype_head_wave573_probe.py --check` PASS
- Npm wrapper: `cmd.exe /c npm run test:ghidra-script-datatype-head-wave573` PASS
- Queue refresh: `6093` total functions, `2877` commented, `3216` commentless, `1465` exact-undefined signatures, `1144` `param_N` signatures
- Post-Wave573 comment-backed proxy: `2877 / 6093 = 47.22%`
- Post-Wave573 strict clean-signature proxy: `2826 / 6093 = 46.39%`
- Next queue head: `0x0052e0f0 CAsmInstruction__ExecutePop`
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-010737_post_wave573_script_datatype_head_verified`
- Backup verification: `19` files, `160205703` bytes, source/destination manifest hash `38C237CB56E35532CA197F68F894172849F3F0F8B224FEE947E3DEA6A62E3E53`

## Limits

This is saved static Ghidra evidence only. No runtime MissionScript behavior was claimed. Exact instruction object layout, exact CDataType/CIntDataType layout, exact opcode enum, exact source identity, BEA launch, game patching, and rebuild parity remain unproven.
