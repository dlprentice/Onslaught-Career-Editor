# ScriptObjectCode.cpp Function Analysis

**Source File:** `C:\dev\ONSLAUGHT2\MissionScript\ScriptObjectCode.cpp`
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

**VTable Address:** `0x005e4f54`

### CMissionScriptObjectCode

Derived class for mission scripts. Adds:
- Async loading support via CChunker
- File path storage (0x100 bytes at offset 0x20)
- Buffer size management

**RTTI String:** `.?AVCMissionScriptObjectCode@@` at `0x00650020`

**VTable Address:** `0x005e4f5c`

## Functions

### CScriptObjectCode Class (17 functions)

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

### CMissionScriptObjectCode Class (5 functions)

| Address | Name | Purpose |
|---------|------|---------|
| `0x00539c80` | `CMissionScriptObjectCode__CMissionScriptObjectCode` | Constructor - initializes fields |
| `0x00539ca0` | `CMissionScriptObjectCode__LoadAsync` | Async load completion handler |
| `0x00539dc0` | `CMissionScriptObjectCode__StartLoadAsync` | Starts async script file loading |
| `0x00539f00` | `CMissionScriptObjectCode__InitFields` | Zero-initializes all instance fields |
| `0x00539f40` | `CMissionScriptObjectCode__ClearFields` | Frees all dynamically allocated fields |

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
