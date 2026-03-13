# BattleEngineConfigurations.cpp Functions

> Source File: BattleEngineConfigurations.cpp | Binary: BEA.exe
> Debug Path: 0x006235a8 (`C:\dev\ONSLAUGHT2\BattleEngineConfigurations.cpp`)

## Overview

This source file handles **battle engine configuration string management** - loading and skipping configuration name strings from serialized data. The configurations appear to be string identifiers stored in an array at `0x00660200` with a count at `0x00660250` (max 20 entries based on array span).

The "BattleEngineConfigurations" are likely named configuration presets for battle engine behavior (difficulty settings, gameplay modifiers, etc.).

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x0040f180 | BattleEngineConfigurations__Load | Load config strings from stream | ~210 bytes |
| 0x0040f260 | BattleEngineConfigurations__Skip | Skip/discard config strings from stream | ~138 bytes |

## Function Details

### BattleEngineConfigurations__Load (0x0040f180)

**Purpose:** Loads battle engine configuration names from a serialized stream into a global array.

**Signature:** `void BattleEngineConfigurations__Load(void)`

**Behavior:**
1. Clears existing configuration array at `0x00660200` (frees any allocated strings)
2. Resets count at `0x00660250` to 0
3. Calls logging function with "Loading battle engine configurations" message
4. Reads 4-byte count from stream via `DXMemBuffer__ReadBytes` (`0x00548570`)
5. For each configuration:
   - Reads 1-byte string length
   - Allocates memory for string (length + 1) via `OID__AllocObject` (memory allocator)
   - Reads string bytes into allocated buffer
   - Null-terminates the string
   - Stores pointer in array at `0x00660200 + (index * 4)`
6. Calls logging completion function

**Key Data Addresses:**
- `0x00660200` - Array of configuration string pointers (20 slots, 0x50 bytes)
- `0x00660250` - Configuration count (int)
- `0x006235dc` - "Loading battle engine configurations" string
- `0x009c3df0` - Memory manager instance (ECX for thiscall)

**Memory Allocation:**
- Allocator ID: `0x15` (21 decimal)
- Source file param: `0x2c` (44 decimal) - line number in source

### BattleEngineConfigurations__Skip (0x0040f260)

**Purpose:** Reads and discards battle engine configuration data from a stream (used when loading older save formats or skipping unwanted data).

**Signature:** `void BattleEngineConfigurations__Skip(void)`

**Behavior:**
1. Reads 4-byte count from stream
2. For each configuration:
   - Reads 1-byte string length
   - Allocates temporary buffer via `OID__AllocObject`
   - Reads string bytes into buffer
   - Null-terminates
   - **Immediately frees** the buffer via `OID__FreeObject`
3. Returns (configuration data is discarded)

**Key Difference from Load:**
- Does NOT store pointers in the global array
- Does NOT update the global count
- Uses allocator source line `0x44` (68 decimal) vs Load's `0x2c` (44)

## Callers

Both functions are called from `FUN_0050d4c0`:
- `0x0050d4ff` - Calls `BattleEngineConfigurations__Skip`
- `0x0050d506` - Calls `BattleEngineConfigurations__Load`

This suggests conditional loading based on some flag or version check in the caller.

## Key Observations

1. **Serialization Pattern:** Uses length-prefixed strings (1-byte length, N bytes data)
2. **Global Storage:** Fixed-size array of 20 configuration slots at `0x00660200`
3. **Memory Manager:** Uses the game's custom memory allocator (`0x009c3df0`) with allocation type `0x15`
4. **Load/Skip Pattern:** Common in serialization - Skip variant for forward compatibility when data format changes
5. **Logging Integration:** Load function logs progress via functions at `0x0042b500` (start) and `0x0042b800` (complete)

## Related Functions

| Address | Name | Purpose |
|---------|------|---------|
| 0x00548570 | DXMemBuffer__ReadBytes | Read bytes from stream |
| 0x005490e0 | OID__AllocObject | Allocate memory (wrapper around CMemoryManager) |
| 0x00549220 | OID__FreeObject | Free memory (wrapper around CMemoryManager) |
| 0x0042b500 | CConsole__Status | Begin logging section |
| 0x0042b800 | CConsole__StatusDone | End logging section |

## Global Variables

| Address | Type | Name | Notes |
|---------|------|------|-------|
| 0x00660200 | char*[20] | g_BattleEngineConfigNames | Array of config name strings |
| 0x00660250 | int | g_BattleEngineConfigCount | Number of loaded configs |
| 0x009c3df0 | CMemoryManager* | g_MemoryManager | Global memory manager instance |

---

*Discovered via Phase 1 xref analysis (Dec 2025)*
