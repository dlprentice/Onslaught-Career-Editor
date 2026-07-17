# IScript mission-scripting interface

Status: active static function map

The retail IScript handlers bridge MissionScript commands to cameras, audio,
object references, vectors, objectives, career slot bits, and Goodie state.
Current corrected metadata is owned by the
[reviewed correction plan](../ghidra-reviewed-correction-plan-2026-07-13.json).

`0x0052ff30 ScriptCommandRegistry__InitBuiltins` initializes 144 contiguous
`0x40`-byte descriptor slots. The retained
[command descriptor schema](../missionscript-command-descriptor-schema.v1.json)
records observed assignments without claiming an exact descriptor layout,
arity, runtime dispatch effect, or complete command semantics.

## Functions (44 listed)

| Address | Name | Purpose |
|---------|------|---------|
| 0x005333b0 | IScript__Constructor | Construct the 0x3c-byte mission-script object for `CComplexThing__SetScript` |
| 0x00533430 | IScript__ScalarDeletingDestructor | Scalar deleting destructor wrapper (`flags&1` frees `this`) |
| 0x00533450 | IScript__Destructor | Tear down the script object, listener/state set, and monitor base |
| 0x00533500 | IScript__CallEvent0AndRegisterNestedListeners | Dispatch event id 0 and register nested `CScriptEventNB` listeners |
| 0x005335a0 | IScript__CallEventId6_OrReset | Dispatch event id 6 or reset when the script VM is shutting down |
| 0x005335d0 | IScript__CreateThingRef | Create a reference to a game object |
| 0x00533660 | IScript__CallEventId5_OrReset | Dispatch event id 5 from destruction/cleanup-adjacent paths or reset |
| 0x00533690 | IScript__CreateThingRefWithSquad | Create thing ref with CRelaxedSquad initialization |
| 0x005337e0 | IScript__CallEventId3_OrReset | Dispatch event id 3 from shutdown/deploy-adjacent paths or reset |
| 0x00533840 | IScript__RestoreSavedStateAndGotoInstruction | Restore a saved script state and resume at the saved instruction cursor |
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
| 0x00534fb0 | IScript__SetThingValueViaVFunc198_FromArg | Dispatch a script-provided value to selected thing vtable slot `+0x198` |
| 0x00534fe0 | IScript__SetThingValueViaVFunc19C_FromArg | Dispatch a script-provided value to selected thing vtable slot `+0x19c` |
| 0x00535010 | IScript__SetThingValueViaEngineHelper4FE390_FromArg | Enable a thing-name flag through the engine helper |
| 0x00535040 | IScript__SetThingValueViaEngineHelper4FE3F0_FromArg | Disable a thing-name flag through the engine helper |
| 0x00535530 | IScript__SetThingFloatViaVFunc1C8_FromArg | Dispatch a script-provided float to selected thing vtable slot `+0x1c8` |
| 0x00535560 | IScript__SetThingRefViaCUnitHelper4FD830_FromArg | Dispatch an integer/faction-like state through `CUnit__SetFactionForHierarchy` |
| 0x00535670 | IScript__GetThingName | Get name string of a game object |
| 0x005357b0 | IScript__GetThingTypeName | Get type/class name of a game object |
| 0x005362a0 | IScript__GetTextWidth | Calculate text width for UI rendering |
| 0x005363e0 | IScript__GetPlayerBattleEngine | Get player's battle engine reference |
| 0x00537410 | IScript__PlaySound | Play sound effect with default settings |
| 0x00537500 | IScript__PlaySoundWithCallback | Play sound with completion callback |
| 0x005375f0 | IScript__PlaySoundWithFade | Play sound with fade-in effect |
| 0x005377e0 | IScript__PlaySoundWithPriority | Play sound with priority level |
| 0x005378e0 | IScript__PlaySoundWithFadeAndPriority | Play sound with fade and priority |
| 0x00537c40 | IScript__PrintText | `PrintText(text_id)`: resolve text id through `CText__GetStringById` and print it through `CConsole__Printf("%w", ...)` |
| 0x00537fd0 | IScript__IsFriendly | Return whether the current script context is friendly (`IsFriendly()`) |
| 0x005381a0 | IScript__LevelLost | Declare the current level LOST (`LevelLost()`) |
| 0x005381c0 | IScript__LevelLostString | Declare the current level LOST with a text id (`LevelLostString(message_id)`) |
| 0x005381e0 | IScript__LevelWon | Declare the current level WON (`LevelWon()`) |
| 0x005383c0 | IScript__ScheduleEvent | Schedule a timed event (2000ms delay) |
| 0x0052ff30 | ScriptCommandRegistry__InitBuiltins | Wave864 built-in command descriptor registry initializer; 144 contiguous 0x40-byte records |

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

Wave578 split the IScript object/event helpers from the later interpreter command handlers. The lifecycle and event helpers at `0x005333b0..0x00533840` are normal retail thiscall-style helpers: `ECX=this`; constructor cleanup is `RET 0x8`; scalar-deleting and thing-ref helpers use `RET 0x4`; register-only event/reset helpers have no stack cleanup. CreateThingRef helpers are IScript thiscall helpers with RET 0x4, not the fixed three-stack-argument script-command ABI.

Later IScript command handlers are called by the MissionScript interpreter using a fixed **3-argument stack ABI** (most return with `ret 0x0c`, i.e. callee pops 12 bytes).

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

## Claim boundary

These entries are static instruction, xref, string, and decompile findings.
They do not prove complete mission-corpus coverage, runtime command behavior,
exact VM/datatype layouts, installed-game patch safety, gameplay outcomes, or
rebuild parity. Save offsets and Goodie state remain owned by the save-format
contracts rather than this function map.
