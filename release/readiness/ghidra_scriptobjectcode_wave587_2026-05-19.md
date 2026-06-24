# Ghidra CScriptObjectCode Wave587 Readiness Note

Date: 2026-05-19
Status: static saved-Ghidra evidence only

Wave587 hardened 22 adjacent `CScriptObjectCode` core VM rows from `0x00538ea0` through `0x00539b00`.

Saved rows:

| Address | Function |
| --- | --- |
| `0x00538ea0` | `CScriptObjectCode__scalar_deleting_dtor` |
| `0x00538ec0` | `CScriptObjectCode__CScriptObjectCode` |
| `0x00539040` | `CScriptObjectCode__Clone` |
| `0x005391a0` | `CScriptObjectCode__Destructor` |
| `0x005392a0` | `CScriptObjectCode__CollectSpawnThings` |
| `0x00539350` | `CScriptObjectCode__RestoreStack` |
| `0x005393e0` | `CScriptObjectCode__ClearStack` |
| `0x00539420` | `CScriptObjectCode__Push` |
| `0x00539470` | `CScriptObjectCode__Pop` |
| `0x005394a0` | `CScriptObjectCode__RemoveTop` |
| `0x005394e0` | `CScriptObjectCode__GetTop` |
| `0x00539510` | `CScriptObjectCode__ClearSymbolTable` |
| `0x005395b0` | `CScriptObjectCode__CloneSymbolTable` |
| `0x00539760` | `CScriptObjectCode__GetInstruction` |
| `0x00539770` | `CScriptObjectCode__ReadSymbolTable` |
| `0x005398d0` | `CScriptObjectCode__InitRuntime` |
| `0x00539910` | `CScriptObjectCode__CopyState` |
| `0x00539980` | `CScriptObjectCode__Reset` |
| `0x00539990` | `CScriptObjectCode__CallEvent` |
| `0x00539a60` | `CScriptObjectCode__CallEventDirect` |
| `0x00539ae0` | `CScriptObjectCode__GotoInstruction` |
| `0x00539b00` | `CScriptObjectCode__Run` |

What is proven:

- Ghidra now records clean signatures, comments, and `scriptobjectcode-wave587` tags for all 22 rows.
- The saved signatures distinguish scalar deleting destructor, constructor, clone/destructor helpers, stack helpers, symbol-table helpers, runtime-state helpers, event-call helpers, and the VM run loop.
- `CScriptObjectCode__CScriptObjectCode` is reached from `CWorld__LoadScriptEvents` and reads instruction, symbol-table, and event-function data from the bytecode reader.
- `CScriptObjectCode__CallEvent` and `CScriptObjectCode__CallEventDirect` are saved as `__thiscall` helpers with four explicit stack arguments; instruction read-back confirms `RET 0x10`.
- `CScriptObjectCode__GotoInstruction`, `GetTop`, `GetInstruction`, `Push`, `RestoreStack`, the constructor, and the scalar deleting destructor retain `RET 0x4` evidence.
- Vtable evidence is bounded: only slot `0x005e4f54[0]` is treated as proven for `CScriptObjectCode__scalar_deleting_dtor`; a full vtable boundary remains unproven because adjacent data quickly crosses into unrelated/RTTI/float-looking rows.
- Post-save read-back verified 22 metadata rows, 22 tag rows, 105 xref rows, 2662 instruction rows, 22 decompile rows, and 64 vtable-slot rows.
- The queue refresh reports `6093` total functions, `3000` commented, `3093` commentless, `1365` exact-undefined signatures, and `1116` `param_N` signatures.
- The next high-signal queue head is `0x00539c80 CMissionScriptObjectCode__CMissionScriptObjectCode`.
- The live Ghidra project backup verified at `G:\GhidraBackups\BEA_20260519-104019_post_wave587_scriptobjectcode_verified` with 19 files, 160861063 bytes, `DiffCount=0`, and manifest hash `d49c8bc11303903eec25964607ee6435e2b3b1fd5ef723ca69cc480bbfe08149`.

What is not proven:

- runtime mission-script behavior remains unproven.
- Script corpus coverage remains separate evidence.
- Exact `CScriptObjectCode`, runtime-state, symbol-table, instruction-array, stack-value, event-table, and bytecode layouts remain unproven.
- Exact source identity remains unproven because no matching tracked Stuart source implementation body was found for this wave.
- The full vtable boundary remains unproven beyond the observed destructor slot.
- BEA patching, gameplay behavior, and rebuild parity remain unproven.
