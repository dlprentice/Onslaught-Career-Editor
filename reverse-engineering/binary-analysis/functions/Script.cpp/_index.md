# Script.cpp Functions

> Source File: Script.cpp | Binary: BEA.exe

## Overview

MSL (Mission Scripting Language) script system integration points for slot-bit manipulation.

Although the mission scripts call `GetSlot` / `SetSlot` / `SetSlotSave`, the underlying runtime bitset lives on the `CGame` singleton (`CGame::mSlots`), and is copied into `END_LEVEL_DATA` and then persisted into `CCareer` on **LevelWon**. `SetSlotSave` additionally persists into `CCareer` immediately.

## Functions

| Address | Name | Purpose |
|---------|------|---------|
| 0x0046d3a0 | [CGame__SetSlot](./CGame__SetSlot.md) | Set/clear a runtime slot bit (`CGame::mSlots`) |
| 0x0046d410 | [CGame__GetSlot](./CGame__GetSlot.md) | Read a runtime slot bit (`CGame::mSlots`) |

## Tech Slots Overview

Tech slots are a 32-integer array (`mSlots[32]`) in the **CCareer** structure that store 1024 individual bits (32 slots x 32 bits). The game uses only 256 slots (0-255) by range check, but the save still reserves the full 32-dword array.

| File Offset | Contents |
|-------------|----------|
| 0x240A | `mSlots[0]` (slots 0-31) |
| 0x240E | `mSlots[1]` (slots 32-63) |
| 0x2412 | `mSlots[2]` (slots 64-95) |
| ... | ... |
| 0x2486 | `mSlots[31]` |

## Bit Manipulation

Tech slots use standard bit operations (NOT shift-16):

```c
// Set bit
mSlots[slot >> 5] |= (1 << (slot & 31));

// Get bit
bool isSet = (mSlots[slot >> 5] & (1 << (slot & 31))) != 0;

// Clear bit
mSlots[slot >> 5] &= ~(1 << (slot & 31));
```

## Related Systems

- MSL scripting language in .aya files
- Career save system (stores mSlots)
- Mission progression logic
- MissionScript interface (`IScript__SetSlot` / `IScript__SetSlotSave` / `IScript__GetSlotBitValue` in [`IScript.cpp.md`](../IScript.cpp.md))

---
*Migrated from ghidra-analysis.md (Dec 2025)*
