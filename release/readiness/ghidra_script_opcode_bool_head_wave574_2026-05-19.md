# Ghidra Script Opcode/Bool Head Wave574 Readiness Note

Date: 2026-05-19
Status: PASS

## Scope

Wave574 hardened fifteen saved Ghidra rows in the retail MissionScript opcode/bool head cluster:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x0052e0f0` | `void __thiscall CAsmInstruction__ExecutePop(void * this, void * script_state, void * data_stack, void * object_code)` | POP executor at dispatch-table slot `0x005e4bd0`; decrements `script_state+0x224`, pops a datatype object, reads scalar data through vtable slot `+0x30`, writes `script_state+0x214`, releases the object, and pushes a one-valued `CIntDataType` status object when allocation succeeds. |
| `0x0052e2c0` | `void __thiscall CInstructionOP_PUSH__VFunc_00_0052e2c0(void * this, void * script_state, void * data_stack, void * object_code)` | OP_PUSH executor at dispatch-table slot `0x005e4cf0`; uses `this+0x04` as the instruction attribute index, resolves the value through `CAsmInstruction__GetAttributeValue`, and pushes the datatype object onto the data stack. |
| `0x0052e380` | `void __thiscall CAsmInstruction__ExecuteCompareEqual(void * this, void * script_state, void * data_stack, void * object_code)` | Equality comparison executor; pops two datatype operands, calls vtable slot `+0x18`, allocates an 8-byte boolean result object, pushes it, and releases both operands. |
| `0x0052e420` | `bool __thiscall CBoolDataType__Equals(void * this, void * rhs)` | Semantic rename from the bool vtable region; data pointer `0x005e4d68`, `RET 0x4`, reads `rhs` through vtable slot `+0x3c`, and compares against the byte at `this+0x04`. |
| `0x0052e440` | `bool __thiscall CBoolDataType__NotEquals(void * this, void * rhs)` | Semantic rename from the bool vtable region; data pointer `0x005e4d6c`, `RET 0x4`, reads `rhs` through vtable slot `+0x3c`, and compares against the byte at `this+0x04`. |
| `0x0052e460` | `void __thiscall CBoolDataType__Assign(void * this, void * rhs)` | Semantic rename from the bool vtable region; data pointer `0x005e4d64`, `RET 0x4`, reads `rhs` through vtable slot `+0x3c`, and stores the returned byte at `this+0x04`. |
| `0x0052e4d0` | `void __thiscall CAsmInstruction__ExecuteOr(void * this, void * script_state, void * data_stack, void * object_code)` | OR executor; pops two datatype operands, reads bool values through vtable slot `+0x3c`, allocates an 8-byte boolean result object, pushes logical OR, and releases both operands. |
| `0x0052e580` | `void __thiscall CAsmInstruction__ExecuteAnd(void * this, void * script_state, void * data_stack, void * object_code)` | AND executor; pops two datatype operands, reads bool values through vtable slot `+0x3c`, allocates an 8-byte boolean result object, pushes logical AND, and releases both operands. |
| `0x0052e630` | `void __thiscall CAsmInstruction__ExecuteGreaterThan(void * this, void * script_state, void * data_stack, void * object_code)` | Greater-than executor; pops two datatype operands, calls comparison slot `+0x24`, allocates/pushes an 8-byte boolean result object, and releases both operands. |
| `0x0052e6d0` | `void __thiscall CAsmInstruction__ExecuteLessThan(void * this, void * script_state, void * data_stack, void * object_code)` | Less-than executor; pops two datatype operands, calls comparison slot `+0x20`, allocates/pushes an 8-byte boolean result object, and releases both operands. |
| `0x0052e770` | `void __thiscall CAsmInstruction__ExecuteGreaterOrEqual(void * this, void * script_state, void * data_stack, void * object_code)` | Greater-or-equal executor; pops two datatype operands, calls comparison slot `+0x2c`, allocates/pushes an 8-byte boolean result object, and releases both operands. |
| `0x0052e810` | `void __thiscall CAsmInstruction__ExecuteLessOrEqual(void * this, void * script_state, void * data_stack, void * object_code)` | Less-or-equal executor; pops two datatype operands, calls comparison slot `+0x28`, allocates/pushes an 8-byte boolean result object, and releases both operands. |
| `0x0052e8b0` | `void __thiscall CAsmInstruction__ExecuteCompareNotEqual(void * this, void * script_state, void * data_stack, void * object_code)` | Inequality comparison executor; pops two datatype operands, calls vtable slot `+0x1c`, allocates an 8-byte boolean result object, pushes it, and releases both operands. |
| `0x0052e950` | `void __thiscall CInstructionOP_JMPFALSE__VFunc_00_0052e950(void * this, void * script_state, void * data_stack, void * object_code)` | JMPFALSE executor at dispatch-table slot `0x005e4c10`; pops a datatype object, reads bool through vtable slot `+0x3c`, writes `this+0x04` to `script_state+0x214` when false, and releases the object. |
| `0x0052ea40` | `void __thiscall CAsmInstruction__ExecuteCall(void * this, void * script_state, void * data_stack, void * object_code)` | CALL executor at dispatch-table slot `0x005e4bc0`; uses `this+0x05` argument count and `this+0x04` function metadata, stages arguments in the global scratch array near `0x0089c300`, dispatches through descriptor table `0x0064ce50`, handles missing/unexpected return values, pushes the result datatype, and releases temporary arguments. |

No `source-parity` tag was applied. This tranche is bounded to saved retail binary evidence; runtime MissionScript behavior, exact VM/data-stack/instruction/datatype layouts, exact opcode enum, exact source identity, BEA patching, and rebuild parity remain deferred.

## Verification

- Dry pass: `updated=0 skipped=15 renamed=0 would_rename=3 missing=0 bad=0`, `REPORT: Save succeeded`
- Apply pass: `updated=15 skipped=0 renamed=3 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Final dry: `updated=0 skipped=15 renamed=0 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Post exports: `15` metadata rows, `15` tag rows, `15` xref rows, `2715` target instruction rows, `15` target decompiles, `112` dispatch-table rows, and `48` datatype-vtable peek rows
- Focused probe: `py -3 tools\ghidra_script_opcode_bool_head_wave574_probe.py --check` PASS
- Npm wrapper: `cmd.exe /c npm run test:ghidra-script-opcode-bool-head-wave574` PASS
- Queue refresh: `6093` total functions, `2892` commented, `3201` commentless, `1455` exact-undefined signatures, `1139` `param_N` signatures
- Post-Wave574 comment-backed proxy: `2892 / 6093 = 47.46%`
- Post-Wave574 strict clean-signature proxy: `2841 / 6093 = 46.63%`
- Next queue head: `0x0052ec60 CDataType__CreateFromType`
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-013338_post_wave574_script_opcode_bool_head_verified`
- Backup verification: `19` files, `160271239` bytes, source/destination manifest hash `C97E50FF3F349872C77D638658E3D0ECFA01B40D94660D35C5EE1086816EBB07`

## Limits

This is saved static Ghidra evidence only. No runtime MissionScript behavior was claimed. Exact VM state layout, data-stack semantics, instruction/datatype layouts, opcode enum, source identity, BEA launch, game patching, and rebuild parity remain unproven. The read-only factory peek suggests the older bool/float type-label table is under active correction: type `2` installs vtable `0x005e4ea4` currently carrying `CFloatDataType` names, while type `4` installs the region with the Wave574 `CBoolDataType` assign/equality slots. Full factory/type-id cleanup is deferred to the next wave.
