# ScriptObjectCode.cpp Function Analysis

Wave1189 current-risk update: Wave1189 (`wave1189-missionscript-bytecode-iscript-current-risk-review`) re-read and normalized comments/tags for `CMissionScriptObjectCode__ClearFields_Thunk` plus adjacent bytecode/IScript context as part of `7 MissionScript bytecode/IScript current-risk rows`. `CAsmInstruction__SpawnFromOpcode already accounted by Wave1120` and was not counted again. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt; Wave1108 current focused accounting is `808/1179 = 68.53%`; current focused candidates: 1169; live regenerated current focused candidates: 1169; remaining active focused work: 371; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; `updated=7 skipped=0`; `comment_only_updated=7`; `tags_added=63`; final dry updated=0 skipped=7; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consults used; no Cursor/Composer. `CMissionScriptObjectCode__ClearFields_Thunk` is called by `CHud__ShutDown` and jumps to `CMissionScriptObjectCode__ClearFields`, keeping this row as a HUD script-field-block teardown bridge; adjacent active anchors include `CInstructionOP_PLUS__VFunc_00_0052e180`, `CInstructionOP_MINUS__VFunc_00_0052e1d0`, `CInstructionOP_MULTIPLY__VFunc_00_0052e220`, `CInstructionOP_DIVIDE__VFunc_00_0052e270`, `CInstructionOP_CMP__VFunc_00_0052e330`, `IScript__Constructor`, `CScriptObjectCode__GetTop`, `CComplexThing__SetScript`, datatype vtable slot +0x04, datatype vtable slot +0x08, datatype vtable slot +0x0c, datatype vtable slot +0x10, datatype vtable slot +0x18, `script_state+0x218`, `script_object_code+0x68`, and vtable 0x005e4f08. Fresh exports verified `7 xref rows`, `208 instruction rows`, and `7 decompile rows`. Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-164704_post_wave1189_missionscript_bytecode_iscript_current_risk_review_verified`; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction. Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference; exact field-block/object-code concrete layout, exact source-body identity, runtime MissionScript behavior, runtime HUD/script teardown behavior, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof. Probe token anchor: Wave1189; wave1189-missionscript-bytecode-iscript-current-risk-review; 808/1179 = 68.53%; 7 MissionScript bytecode/IScript current-risk rows; current focused candidates: 1169; live regenerated current focused candidates: 1169; remaining active focused work: 371; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=7 skipped=0; comment_only_updated=7; tags_added=63; final dry updated=0 skipped=7; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consults used; no Cursor/Composer; CAsmInstruction__SpawnFromOpcode already accounted by Wave1120; CInstructionOP_PLUS__VFunc_00_0052e180; CInstructionOP_MINUS__VFunc_00_0052e1d0; CInstructionOP_MULTIPLY__VFunc_00_0052e220; CInstructionOP_DIVIDE__VFunc_00_0052e270; CInstructionOP_CMP__VFunc_00_0052e330; IScript__Constructor; CMissionScriptObjectCode__ClearFields_Thunk; CScriptObjectCode__GetTop; CComplexThing__SetScript; CHud__ShutDown; datatype vtable slot +0x04; datatype vtable slot +0x08; datatype vtable slot +0x0c; datatype vtable slot +0x10; datatype vtable slot +0x18; script_state+0x218; script_object_code+0x68; vtable 0x005e4f08; 0 / 0 / 0; 6411/6411 = 100.00%; 7 xref rows; 208 instruction rows; 7 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260606-164704_post_wave1189_missionscript_bytecode_iscript_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.

2026-06-08 VM/datatype/opcode schema proof: `missionscript-vm-datatype-opcode-schema-proof.md` and `missionscript-vm-datatype-opcode-schema.v1.json` now preserve the static VM handoff around `0x00539b00 CScriptObjectCode__Run`, including opcode dispatch through instruction vtable slot 0, opcode read through vtable slot `+0x08`, stop candidate opcode `0x17`, the `10000` instruction limit, stack bound `0x80`, stack count role at `stack+0x200`, state anchors including `script_state+0x218` and `script_object_code+0x68`, and the `CAsmInstruction__ExecuteCall` bridge to descriptor table `0x0064ce50`. This is not runtime VM execution proof and does not prove exact VM/object-code layouts.

2026-06-08 event/object-code lifecycle schema proof: `missionscript-event-object-code-lifecycle-proof.md` and `missionscript-event-object-code-lifecycle.v1.json` now preserve the static event-call side of this owner file. The schema ties `CScriptObjectCode__CallEvent`, `CScriptObjectCode__CallEventDirect`, and `CScriptObjectCode__Run` to `CEventFunction__Execute`, `CScriptEventNB__PostEvent`, `IScript__ScheduleEvent`, `CMissionScriptObjectCode__StartLoadAsync`, `CMissionScriptObjectCode__LoadAsync`, and `CMissionScriptObjectCode__ClearFields`; it also preserves `script_object_code+0x68`, descriptor dependency `0x0064ce50`, and `795` loose event-name counts as corpus context. This is static lifecycle accounting only, not runtime event dispatch/outcome, live loose-MSL loading, exact object-code/event layout, patch, Godot, rebuild, or no-noticeable-difference proof.

2026-06-08 packed-vs-loose script-selection proof plan: `missionscript-packed-vs-loose-script-selection-proof-plan.md` and `missionscript-packed-vs-loose-script-selection.v1.json` now preserve the static planning boundary around this owner file's async load anchors. The plan keeps `0x00539dc0 CMissionScriptObjectCode__StartLoadAsync`, `0x00539ca0 CMissionScriptObjectCode__LoadAsync`, `this+0x20`, `this+0x124`, and `CDXMemBuffer__InitFromFile` as path-buffer/object-code load evidence, then separates that from `733` loose `.msl` corpus files, `95` level rows, `795` event-name counts, `301` packed AYA archives scanned, `0` inflate errors, and `0` literal Goodie API/token hits. This is static source-selection planning only, not runtime MissionScript execution, live loose-MSL loading, packed-resource script-selection proof, exact async-cache layout, patch, Godot, rebuild, or no-noticeable-difference proof.

**Source File:** `[maintainer-local-source-export-root]\MissionScript\ScriptObjectCode.cpp`
**Analysis Date:** December 2025
**Binary:** BEA.exe (Steam release)

## Overview

This file implements the **script virtual machine (VM)** for mission scripting in Battle Engine Aquila. It contains two main classes:

1. **CScriptObjectCode** - Base class implementing the stack-based bytecode interpreter
2. **CMissionScriptObjectCode** - Derived class for mission-specific script loading

The VM is a **stack-based interpreter** with:
- 128-entry stack (0x80 slots)
- 10,000 instruction limit per execution (infinite loop protection)
- Support for cloning/copying script state
- Event-driven execution model

## Classes Identified

### CScriptObjectCode

Base class for script execution. Contains:
- Bytecode instruction array (via CFlexArray)
- Symbol table for variables
- Event function list
- Stack for operand manipulation
- Runtime state (instruction pointer, flags)

**RTTI String:** Not directly found (base class)

**VTable evidence:** Wave587 treats only slot `0x005e4f54[0]` as proven for `CScriptObjectCode__scalar_deleting_dtor`. The surrounding bytes quickly enter unrelated/RTTI/float-looking data, so `0x005e4f54` is not a proven full vtable boundary.

### CMissionScriptObjectCode

Derived class for mission scripts. Adds:
- Async loading support via CChunker
- File path storage (0x100 bytes at offset 0x20)
- Buffer size management
- A separate retail cleanup helper at `0x004f7440` frees the two pointer slots of an object-code record owned by `CMissionScriptObjectCode__ClearFields`

**RTTI String:** `.?AVCMissionScriptObjectCode@@` at `0x00650020`

**VTable Address:** `0x005e4f5c`; Wave588 treats only slot `0x005e4f5c[0]` as proven for `CMissionScriptObjectCode__LoadAsync`. Adjacent slot read-back crosses into `CDXBattleLine` evidence, so the full vtable boundary remains unproven.

### CVM Static Cleanup Wrapper

Wave583 identified two adjacent CVM stack cleanup rows near the script object-code range. The exact CVM source class identity/layout remains unproven; the saved names are based on retail decompile, xref, vtable-slot, and instruction read-back.

| Address | Name | Purpose |
|---------|------|---------|
| `0x00535330` | `CVM__ScalarDeletingDestructor` | Vtable-slot scalar deleting destructor wrapper at `0x005e4f20`; calls `CVM__Destructor`, tests `flags&1`, optionally frees `this`, and returns `this` |
| `0x00535350` | `CVM__Destructor` | Destructor body; clears the embedded script stack via `CScriptObjectCode__ClearStack(this+0x0c)` and calls `CMonitor__Shutdown(this)` |

## Functions

### CScriptObjectCode Class (22 functions)

| Address | Name | Purpose |
|---------|------|---------|
| `0x00538ec0` | `CScriptObjectCode__CScriptObjectCode` | Constructor - reads bytecode from buffer, creates instruction array, symbol table, event functions |
| `0x00538ea0` | `CScriptObjectCode__scalar_deleting_dtor` | Scalar deleting destructor (calls Destructor then frees memory) |
| `0x005391a0` | `CScriptObjectCode__Destructor` | Destructor - frees instructions, event functions, symbol table |
| `0x00539040` | `CScriptObjectCode__Clone` | Creates a deep copy of the script object with cloned instructions and state |
| `0x005392a0` | `CScriptObjectCode__CollectSpawnThings` | Scans instructions for "SpawnThing" opcodes and adds to world mesh list |
| `0x00539350` | `CScriptObjectCode__RestoreStack` | Restores stack state from a saved state buffer |
| `0x005393e0` | `CScriptObjectCode__ClearStack` | Clears entire stack, calling destructors on all elements |
| `0x00539420` | `CScriptObjectCode__Push` | Pushes value onto stack (max 128 entries) |
| `0x00539470` | `CScriptObjectCode__Pop` | Pops and returns top value from stack |
| `0x005394a0` | `CScriptObjectCode__RemoveTop` | Pops and destroys top value (calls destructor) |
| `0x005394e0` | `CScriptObjectCode__GetTop` | Returns stack value at offset from top |
| `0x00539510` | `CScriptObjectCode__ClearSymbolTable` | Frees all entries in symbol table |
| `0x005395b0` | `CScriptObjectCode__CloneSymbolTable` | Creates copy of symbol table for cloned scripts |
| `0x00539760` | `CScriptObjectCode__GetInstruction` | Returns instruction at given index |
| `0x00539770` | `CScriptObjectCode__ReadSymbolTable` | Reads symbol table from buffer (name, type, flags) |
| `0x005398d0` | `CScriptObjectCode__InitRuntime` | Initializes runtime state fields to zero |
| `0x00539910` | `CScriptObjectCode__CopyState` | Copies execution state from another instance |
| `0x00539980` | `CScriptObjectCode__Reset` | Resets VM state (wrapper for ClearStack) |
| `0x00539990` | `CScriptObjectCode__CallEvent` | Calls event handler by index with parameters |
| `0x00539a60` | `CScriptObjectCode__CallEventDirect` | Calls event at specific instruction address |
| `0x00539ae0` | `CScriptObjectCode__GotoInstruction` | Sets instruction pointer and runs |
| `0x00539b00` | `CScriptObjectCode__Run` | **Main VM execution loop** - fetches and executes instructions |

### CMissionScriptObjectCode Class (6 functions plus cleanup helper)

| Address | Name | Purpose |
|---------|------|---------|
| `0x00539c80` | `CMissionScriptObjectCode__CMissionScriptObjectCode` | Constructor - initializes fields |
| `0x00539ca0` | `CMissionScriptObjectCode__LoadAsync` | Async load completion handler |
| `0x00539dc0` | `CMissionScriptObjectCode__StartLoadAsync` | Starts async script file loading |
| `0x00539f00` | `CMissionScriptObjectCode__InitFields` | Zero-initializes all instance fields |
| `0x00539f30` | `CMissionScriptObjectCode__ClearFields_Thunk` | One-instruction jump thunk into `CMissionScriptObjectCode__ClearFields` |
| `0x00539f40` | `CMissionScriptObjectCode__ClearFields` | Frees all dynamically allocated fields |
| `0x004f7440` | `CMissionScriptObjectCode__FreeObjectIfPresent` | Wave546 static cleanup helper: frees object-code record pointer slots `+0x00` and `+0x04` through global memory manager `0x009c3df0`; called by `ClearFields` before freeing the enclosing allocation |

### Wave588 Static Read-Back

Wave588 saved the CMissionScriptObjectCode async/field-block tranche from `0x00539c80` through `0x00539f40`: constructor, async load slot, async start helper, HUD script-field-block init, ClearFields jump thunk, and ClearFields body.

Saved signatures:

| Address | Saved signature |
| --- | --- |
| `0x00539c80` | `void * __fastcall CMissionScriptObjectCode__CMissionScriptObjectCode(void * this)` |
| `0x00539ca0` | `void __thiscall CMissionScriptObjectCode__LoadAsync(void * this)` |
| `0x00539dc0` | `void __thiscall CMissionScriptObjectCode__StartLoadAsync(void * this, char * filename, int buffer_size)` |
| `0x00539f00` | `void __fastcall CMissionScriptObjectCode__InitFields(void * field_block)` |
| `0x00539f30` | `void __fastcall CMissionScriptObjectCode__ClearFields_Thunk(void * field_block)` |
| `0x00539f40` | `void __fastcall CMissionScriptObjectCode__ClearFields(void * field_block)` |

Read-back evidence: `ApplyMissionScriptObjectCodeWave588.java` dry/apply/final dry reported `updated=0 skipped=6 renamed=0 would_rename=1 missing=0 bad=0`, then `updated=6 skipped=0 renamed=1 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=6 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. Post exports verified `6` metadata rows, `6` tag rows, `7` xref rows, `534` instruction rows, `6` decompile rows, and `64` vtable rows.

Important boundaries:

- `CMissionScriptObjectCode__CMissionScriptObjectCode` is reached from `CFEPMultiplayerStart__ctor`, calls `CWaitingThread__ctor_base`, installs pointer `0x005e4f5c`, and clears the path byte at `this+0x20`.
- Only slot `0x005e4f5c[0]` is proven for `CMissionScriptObjectCode__LoadAsync`; adjacent slot read-back crosses into `CDXBattleLine__scalar_deleting_dtor`, so the full vtable boundary remains unproven.
- `CMissionScriptObjectCode__LoadAsync` closes prior buffer state, allocates a `CDXMemBuffer`, initializes it from the stored path, and clears the first path byte before returning.
- `CMissionScriptObjectCode__StartLoadAsync` has `RET 0x8` evidence for `filename` and `buffer_size`, waits for the current thread, copies the filename, stores buffer size, and starts the async worker.
- `CMissionScriptObjectCode__InitFields`, `CMissionScriptObjectCode__ClearFields_Thunk`, and `CMissionScriptObjectCode__ClearFields` are documented as HUD script-field-block helpers because their observed xrefs are `CHud__Init` and `CHud__ShutDown`; this does not prove a full `CMissionScriptObjectCode` instance layout.

Post-Wave588 queue telemetry: `6093` total functions, `3006` commented, `3087` commentless, `1359` exact-undefined signatures, `1116` `param_N` signatures, comment-backed proxy `3006/6093 = 49.34%`, strict clean-signature proxy `2960/6093 = 48.58%`, and next head `0x0053a050 CDXBattleLine__Constructor`.

This is static retail Ghidra evidence only; exact `CMissionScriptObjectCode`, HUD field-block, async-cache, object-code-record, and file path ownership layouts, source identity, runtime mission-script/Goodie/HUD behavior, full vtable boundary, BEA patching, and rebuild parity remain deferred.

### Wave587 Static Read-Back

Wave587 saved the CScriptObjectCode core VM tranche from `0x00538ea0` through `0x00539b00`: constructor, clone/destructor, SpawnThing scan, stack helpers, symbol-table helpers, runtime-state helpers, event-call helpers, and the VM run loop.

Saved signatures:

| Address | Saved signature |
| --- | --- |
| `0x00538ea0` | `void * __thiscall CScriptObjectCode__scalar_deleting_dtor(void * this, byte delete_flags)` |
| `0x00538ec0` | `void * __thiscall CScriptObjectCode__CScriptObjectCode(void * this, void * bytecode_reader)` |
| `0x00539040` | `void * __fastcall CScriptObjectCode__Clone(void * script_object_code)` |
| `0x005391a0` | `void __fastcall CScriptObjectCode__Destructor(void * script_object_code)` |
| `0x005392a0` | `void __fastcall CScriptObjectCode__CollectSpawnThings(void * script_object_code)` |
| `0x00539350` | `void * __thiscall CScriptObjectCode__RestoreStack(void * this, void * saved_stack)` |
| `0x005393e0` | `void __fastcall CScriptObjectCode__ClearStack(void * stack)` |
| `0x00539420` | `void __thiscall CScriptObjectCode__Push(void * this, void * value)` |
| `0x00539470` | `void * __fastcall CScriptObjectCode__Pop(void * stack)` |
| `0x005394a0` | `void __fastcall CScriptObjectCode__RemoveTop(void * stack)` |
| `0x005394e0` | `void * __thiscall CScriptObjectCode__GetTop(void * this, int offset_from_top)` |
| `0x00539510` | `void __fastcall CScriptObjectCode__ClearSymbolTable(void * symbol_table)` |
| `0x005395b0` | `void * __fastcall CScriptObjectCode__CloneSymbolTable(void * symbol_table)` |
| `0x00539760` | `void * __thiscall CScriptObjectCode__GetInstruction(void * this, int instruction_index)` |
| `0x00539770` | `void * __thiscall CScriptObjectCode__ReadSymbolTable(void * this, void * bytecode_reader)` |
| `0x005398d0` | `void __fastcall CScriptObjectCode__InitRuntime(void * runtime_state)` |
| `0x00539910` | `void * __thiscall CScriptObjectCode__CopyState(void * this, void * source_state)` |
| `0x00539980` | `void __fastcall CScriptObjectCode__Reset(void * stack)` |
| `0x00539990` | `void __thiscall CScriptObjectCode__CallEvent(void * this, void * script_object_code, int event_index, void * * params, int param_count)` |
| `0x00539a60` | `void __thiscall CScriptObjectCode__CallEventDirect(void * this, void * script_object_code, int instruction_index, void * * params, int param_count)` |
| `0x00539ae0` | `void __thiscall CScriptObjectCode__GotoInstruction(void * this, int instruction_index)` |
| `0x00539b00` | `void __fastcall CScriptObjectCode__Run(void * runtime_state)` |

Read-back evidence: `ApplyScriptObjectCodeWave587.java` dry/apply/final dry reported `updated=0 skipped=22 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=22 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=22 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. Post exports verified `22` metadata rows, `22` tag rows, `105` xref rows, `2662` instruction rows, `22` decompile rows, and `64` vtable rows.

Important boundaries:

- `CScriptObjectCode__CScriptObjectCode` is reached from `CWorld__LoadScriptEvents`, reads instruction objects through `CAsmInstruction__SpawnFromOpcode`, calls `CScriptObjectCode__ReadSymbolTable`, and creates `CEventFunction` records.
- `CScriptObjectCode__Clone` is reached from `CWorld__CloneScriptObjectCodeByName` and clones instructions, symbol-table entries, event functions, and selected state fields.
- Stack helpers use the observed count at `+0x200`; the saved comments keep exact stack value type and owner layout open.
- `CScriptObjectCode__GetInstruction` is kept as the current saved name, but the body only proves ECX as the instruction-array/flex-array pointer, not a full object instance.
- `CScriptObjectCode__CallEvent` and `CScriptObjectCode__CallEventDirect` both call `CScriptObjectCode__Run`; instruction read-back confirms `RET 0x10` on each helper.
- `CScriptObjectCode__Run` records recursive-run protection, debug trace logging, the 10000-instruction limit, final stack-size check, and cleanup through `CScriptObjectCode__RemoveTop`.
- For vtable evidence, only slot `0x005e4f54[0]` is treated as proven; the full vtable boundary remains unproven.

Post-Wave587 queue telemetry: `6093` total functions, `3000` commented, `3093` commentless, `1365` exact-undefined signatures, `1116` `param_N` signatures, comment-backed proxy `3000/6093 = 49.24%`, strict clean-signature proxy `2954/6093 = 48.48%`, and next head `0x00539c80 CMissionScriptObjectCode__CMissionScriptObjectCode`.

This is static retail Ghidra evidence only; exact `CScriptObjectCode`, runtime-state, stack-value, symbol-table, event-table, bytecode, and instruction-array layouts, source identity, script corpus coverage, runtime mission-script behavior, BEA patching, and rebuild parity remain deferred.

### Wave583 Static Read-Back

Wave583 saved `0x00535330` as `void * __thiscall CVM__ScalarDeletingDestructor(void * this, byte flags)` and `0x00535350` as `void __thiscall CVM__Destructor(void * this)`.

The scalar-deleting wrapper is referenced by vtable slot `0x005e4f20`; decompile read-back calls `CVM__Destructor(this)`, tests `flags&1`, optionally calls `CDXMemoryManager__Free(&DAT_009c3df0,this)`, returns `this`, and instruction read-back confirms `RET 0x4`.

The destructor body is called by the wrapper and raw callsite `0x005398c5`; instruction read-back shows `LEA ECX, [ESI + 0xc]` before `CScriptObjectCode__ClearStack`, then `CMonitor__Shutdown(this)`. This is static retail Ghidra evidence only; exact CVM source class identity/layout, exception-handler semantics, runtime mission-script behavior, BEA patching, and rebuild parity remain deferred.

### Wave546 Static Cleanup Helper

Wave546 saved `0x004f7440` as `void __fastcall CMissionScriptObjectCode__FreeObjectIfPresent(void * object_code)`. The body treats `ECX` as the object-code record, frees `*(object_code+0x00)` and `*(object_code+0x04)` through `CDXMemoryManager__Free(&DAT_009c3df0, ...)`, and returns.

The only observed xref is `CMissionScriptObjectCode__ClearFields`: it checks its object-code pointer for non-null, calls this helper, frees the enclosing object-code allocation, and clears the owner field. This is static retail Ghidra evidence only; exact object-code layout, allocation ownership, source identity, runtime mission-script behavior, and rebuild parity remain open.

## Key Structures

### CScriptObjectCode Runtime Layout (offset from `this`)

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0x000 | 4 | vtable | Virtual function table pointer |
| 0x004 | 4 | mInstructions | CFlexArray of CAsmInstruction* |
| 0x008 | 4 | mCodeObject | Parent CScriptObjectCode* |
| 0x00C | 4 | mInstructionCount | Number of instructions |
| ... | ... | ... | ... |
| 0x058 | 4 | mSymbolTable | Symbol table pointer |
| 0x05C | 4 | mEventFunctionCount | Number of event handlers |
| 0x060 | 4 | mDebugMode | Debug trace enabled flag |
| 0x064 | 4 | mInstructionIndex | Current execution position |
| 0x06C | 4 | mInitialized | Script initialized flag |
| ... | ... | ... | ... |
| 0x000-0x1FC | 512 | mStack[128] | Operand stack (128 x 4 bytes) |
| 0x200 | 4 | mStackPointer | Current stack depth |
| 0x20C | 4 | mStackSize | (Alias for stack pointer) |
| 0x210 | 4 | mIsRunning | VM currently executing flag |
| 0x214 | 4 | mIP | Instruction pointer |
| 0x218 | 4 | mFlags | Execution flags |
| 0x21C | 4 | mSavedStackSize | Stack size at call entry |
| 0x220 | 4 | mAbort | Abort execution flag |
| 0x224 | 4 | mCallDepth | Nested call counter |

### CMissionScriptObjectCode Additional Fields

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0x01C | 4 | mChunker | CChunker* for async loading |
| 0x020 | 256 | mFilePath | Script file path string |
| 0x124 | 4 | mBufferSize | Read buffer size |

## Error Messages

These error strings provide insight into the VM's error handling:

| String | Function | Meaning |
|--------|----------|---------|
| `FATAL ERROR: Stack out of memory` | Push | Stack overflow (>128 entries) |
| `FATAL ERROR: Pop called on empty stack` | Pop | Stack underflow |
| `FATAL ERROR: RemoveTop called on empty stack` | RemoveTop | Stack underflow |
| `FATAL ERROR: Stack item does not exist in call to GetTop - %d` | GetTop | Invalid stack index |
| `FATAL ERROR: stack not empty on call` | CallEvent | Stack corruption check |
| `FATAL ERROR: stack was different size when exiting` | Run | Stack balance check |
| `FATAL ERROR: Infinite loop in sc` | Run | >10000 instructions executed |
| `ERROR: VM tryin to run VM whilst` | Run | Recursive VM entry |

## VM Execution Model

1. **Event-driven**: Scripts respond to events (OnCreate, OnUpdate, OnDamage, etc.)
2. **Stack-based**: Operands pushed/popped for instruction execution
3. **Bytecode**: Instructions are `CAsmInstruction` objects with opcode + operands
4. **Safety limits**:
   - 128 stack entries max
   - 10,000 instructions per event call
   - Re-entry protection

### Instruction Loop (Run)

```
while (opcode != 0x17 /*END*/ || callDepth > 0) && !abort:
    opcode = instruction[IP].GetOpcode()
    IP++
    instruction.Execute()

    if (debugMode):
        print("-> %4d stack size = %d flags = %d", IP, stackSize, flags)

    iterationCount++
    if (iterationCount > 10000):
        error("Infinite loop")
        abort = true
```

## Related Files

- `DataType.cpp` - CDataType base class for typed values
- `EventFunction.cpp` - CEventFunction event handler implementation
- `Script.cpp` - Higher-level script management
- `IScript.cpp` - Script interface definitions

## Notable Discoveries

1. **SpawnThing Collection**: The `CollectSpawnThings` function scans bytecode for spawn instructions (opcode 0x18) to pre-load assets

2. **Debug Mode**: Setting offset 0x60 to 1 enables per-instruction trace logging

3. **Clone Support**: Scripts can be cloned for multiple concurrent instances (important for spawned entities)

4. **Async Loading**: Mission scripts support background loading via the chunker system

## Cross-References

- Called by: `CScript`, `CMission`, various game systems
- Calls: `CAsmInstruction::Execute`, `CDataType` hierarchy, `CEventFunction`
