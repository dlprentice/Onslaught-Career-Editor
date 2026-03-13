# IScript.cpp - Mission Scripting Interface

> Source: `C:\dev\ONSLAUGHT2\MissionScript\IScript.cpp`
> Debug string address: `0x0064fa40`
> Last updated: 2026-02-15

## Overview

IScript.cpp implements the mission scripting interface for Battle Engine Aquila. This file contains script instruction handlers that provide high-level game functionality to the MSL (Mission Script Language) system.

The functions in this file are called by the script interpreter to execute commands like creating cameras, playing sounds, getting object references, and manipulating vectors.

## Functions (28 total)

| Address | Name | Purpose |
|---------|------|---------|
| 0x005335d0 | IScript__CreateThingRef | Create a reference to a game object |
| 0x00533690 | IScript__CreateThingRefWithSquad | Create thing ref with CRelaxedSquad initialization |
| 0x005338a0 | IScript__SetPlayerLives | Set per-player lives counters (`SetPlayerLives(player_index,lives)`) |
| 0x005338d0 | IScript__SetSlot | Set a slot bit in the runtime script bitset only (`SetSlot(slot,val)`) |
| 0x00533900 | IScript__SetSlotSave | Set a slot bit and persist it into career save data (`SetSlotSave(slot,val)`) |
| 0x005339a0 | IScript__GetSlotBitValue | Get career slot bit value (tech unlocks) |
| 0x00533a70 | IScript__SetGoodieState | Set `g_Career_mGoodies[index-1]` state (1-based index in scripts) |
| 0x00533aa0 | IScript__GetGoodieState | Get `g_Career_mGoodies[index-1]` state (cutscene/kill goodies) |
| 0x00533b70 | IScript__Create3PointPanCamera | Create camera pan with 3 control points |
| 0x00533eb0 | IScript__Create4PointPanCamera | Create camera pan with 4 control points |
| 0x005345d0 | IScript__GetVectorLength | Calculate vector magnitude (sqrt) |
| 0x005347b0 | IScript__CheckValueInRange | Check if value is within min/max bounds |
| 0x00534b80 | IScript__GetVectorX | Extract X component from vector |
| 0x00534c10 | IScript__GetVectorY | Extract Y component from vector |
| 0x00534ca0 | IScript__GetVectorZ | Extract Z component from vector |
| 0x00535670 | IScript__GetThingName | Get name string of a game object |
| 0x005357b0 | IScript__GetThingTypeName | Get type/class name of a game object |
| 0x005362a0 | IScript__GetTextWidth | Calculate text width for UI rendering |
| 0x005363e0 | IScript__GetPlayerBattleEngine | Get player's battle engine reference |
| 0x00537410 | IScript__PlaySound | Play sound effect with default settings |
| 0x00537500 | IScript__PlaySoundWithCallback | Play sound with completion callback |
| 0x005375f0 | IScript__PlaySoundWithFade | Play sound with fade-in effect |
| 0x005377e0 | IScript__PlaySoundWithPriority | Play sound with priority level |
| 0x005378e0 | IScript__PlaySoundWithFadeAndPriority | Play sound with fade and priority |
| 0x005381a0 | IScript__LevelLost | Declare the current level LOST (`LevelLost()`) |
| 0x005381c0 | IScript__LevelLostString | Declare the current level LOST with a text id (`LevelLostString(message_id)`) |
| 0x005381e0 | IScript__LevelWon | Declare the current level WON (`LevelWon()`) |
| 0x005383c0 | IScript__ScheduleEvent | Schedule a timed event (2000ms delay) |

## Key Patterns

### Object Allocation Pattern
All functions use `OID__AllocObject` to create script result objects:
```c
puVar = OID__AllocObject(8, 0x18, "IScript.cpp", lineNumber);
if (puVar != NULL) {
    *puVar = vtable;        // Set vtable pointer
    puVar[1] = returnValue; // Set return value
}
```

### Camera Creation (3/4-Point Pan)
The camera functions create CBSpline objects for smooth camera movement:
- Transform world-space coordinates using thing's local matrix
- Create CSPtrSet lists of control points
- Allocate CBSpline with 3 points and initialize camera path

### Vector Operations
Simple extraction of X/Y/Z components from 12-byte vector structure:
- X at offset 0
- Y at offset 4
- Z at offset 8
- Length uses SQRT(x*x + y*y + z*z)

### Sound System Integration
Sound functions integrate with the sound manager:
- Use `FUN_004f2580` to convert sound enum to resource
- Support priority levels (0-10)
- Support fade effects with 0x3d4ccccd (0.05f) fade rate
- Event ID 0x7d1 (2001) for sound fade event

## Related Global Variables

| Address | Purpose |
|---------|---------|
| 0x0089c7f0 | Script system disabled flag |
| 0x008a9ac0 | Game state (4 = exiting) |
| 0x0089c528 | Last created script object |
| 0x008a9d84 | Sound manager initialized flag |
| 0x008a9d3c | Player array base |
| 0x0089c590 | Sound manager instance |

## VTables Referenced

| Address | Class |
|---------|-------|
| 0x005e4af8 | Script integer/thing ref result |
| 0x005e4b4c | Script thing ref with squad |
| 0x005e4d50 | Script boolean result |
| 0x005e4df8 | Script thing ref (final) |
| 0x005e4ea4 | Script float result |
| 0x005e4f1c | Sound fade state |
| 0x005e4f34 | Scheduled event |

## Error Strings

| Address | String | Function |
|---------|--------|----------|
| 0x0064fa9c | "FATAL ERROR: null thing passed to 'Create3PointPanCamera'" | IScript__Create3PointPanCamera |
| 0x0064fad8 | "FATAL ERROR: null thing passed to 'Create4PointPanCamera'" | IScript__Create4PointPanCamera |
| 0x0064fc3c | "Fatal error: Player %d has no battle engine!!!" | IScript__GetPlayerBattleEngine |
| 0x0064fc6c | "Warning: sorry no player %d returning 1" | IScript__GetPlayerBattleEngine |
| 0x0064fd30 | "_unknown_" | IScript__PlaySound (default sound name) |
| 0x0064fd3c | "SHIT this should never happen" | IScript__PlaySoundWithFade (error case) |

## Calling Convention

IScript command handlers are called by the MissionScript interpreter using a fixed **3-argument stack ABI** (most return with `ret 0x0c`, i.e. callee pops 12 bytes).

Observed (Steam `BEA.exe`):
- `arg0`: pointers to script argument objects (handlers call virtual getters on these objects)
- `arg1`: often unused (sometimes a state/flags value)
- `arg2`: out-result pointer for commands that return a value (e.g. `IScript__GetSlotBitValue` writes `*out`)

Virtual getters on argument objects (common offsets):
- vtable+`0x30`: integer getter (e.g. `LevelLostString(message_id)`)
- vtable+`0x34`: float getter
- vtable+`0x3c`: byte/bool-like getter (seen in `IScript__SetSlot`)
- vtable+`0x44`: vector getter

Note: many handlers ignore `arg1/arg2` (e.g. `IScript__LevelLost`), so Ghidra may infer fewer parameters even though the call ABI is fixed.

## Integration with CGame Slot Bits

Slot-bit persistence is script-driven:
- `GetSlot(...)` returns `CGame__GetSlot(slot)` (`0x0046d410`) from the runtime slot-bitset at `CGame + 0x308`.
- `SetSlot(slot,val)` calls `CGame__SetSlot(slot,val)` (`0x0046d3a0`) on the runtime slot-bitset (persists into CCareer on LevelWon via END_LEVEL_DATA copy).
- `SetSlotSave(slot,val)` calls `CGame__SetSlot(slot,val)` (`0x0046d3a0`) and also persists the same flag into the career save bitmap via `CCareer__SetSlot(&CAREER, slot, val)` (`0x004214e0`).

Goodie state manipulation is also script-driven:
- `GetGoodieState(index)` returns `g_Career_mGoodies[index-1]` as a scalar result.
- `SetGoodieState(index, state)` updates `g_Career_mGoodies[index-1]` in-place (scripts use 1-based indices).
- Retail state values are `0..3` (`GOODIE_UNKNOWN/INSTRUCTIONS/NEW/OLD`); see [`reverse-engineering/save-file/goodies-system.md`](../../save-file/goodies-system.md).
- Save-file mapping: goodie array starts at file offset `0x1F46`, so script index `N` maps to `0x1F46 + (N-1)*4`.

## Notes

1. **Exception Handling**: All functions set up SEH (Structured Exception Handling) frames with Unwind handlers
2. **Memory Safety**: Functions check for NULL allocations before dereferencing
3. **Squad System**: Some thing refs automatically initialize CRelaxedSquad for AI control
4. **Matrix Operations**: Camera functions perform full 3x3 matrix multiplication for coordinate transformation
