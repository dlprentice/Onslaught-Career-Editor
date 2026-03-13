# FEPOptions.cpp - Function Index

> Source File: FEPOptions.cpp | Category: Frontend/Options Menu

## Overview

Frontend options menu implementation. Saves configuration to `defaultoptions.bea` (Steam build). Contains UI state management and save file enumeration.

Important nuance discovered via Ghidra:
- The functions previously labeled as "GetVolumes/SetVolumes" do **not** operate on the sound/music float volumes.
- They call `CCareer__GetKillCounterTopByte_23F4/23F8` and `CCareer__SetKillCounterTopByte_23F4/23F8` (top-byte metadata inside the first two kill counters). Their exact UI meaning is still TBD.
- The actual Sound/Music floats live in the global `CCareer` instance at `g_Career+0x248C` and `g_Career+0x2490` (`0x00662AAC` / `0x00662AB0`).

## Debug Path String

| Address | String |
|---------|--------|
| 0x0063fc88 | `"C:\\dev\\ONSLAUGHT2\\FEPOptions.cpp"` |

## Functions

| Address | Function | Status | Description |
|---------|----------|--------|-------------|
| 0x0051f370 | CFEPOptions__GetState | Named | Returns current menu state from `this+5` |
| 0x0051f470 | CFEPOptions__GetKillCounterTopBytes_23F4_23F8 | Named | Gets **kill-counter top-byte metadata** for 0x23F4/0x23F8 (not float volumes) |
| 0x0051f490 | CFEPOptions__SetKillCounterTopBytes_23F4_23F8 | Named | Sets **kill-counter top-byte metadata** for 0x23F4/0x23F8 (not float volumes) |
| 0x0051f500 | CFEPOptions__SaveDefaultOptions | Named | Saves career settings to `defaultoptions.bea` |
| 0x0051f600 | CFEPOptions__ProcessInput | Named | State machine for menu input processing |
| 0x0051f680 | [CFEPOptions__WriteDefaultOptionsFile](./CFEPOptions__WriteDefaultOptionsFile.md) | Named | Low-level writer for `defaultoptions.bea` (called from load/save flows) |
| 0x0051f700 | CFEPOptions__Update | Named | Updates UI, handles selection highlight |
| 0x0051f7e0 | CFEPOptions__EnsureOptionsContext | Named | Vtable helper: snapshots CCareer option globals into page state; lazily allocates `g_pOptionsContext` |
| 0x0051f8e0 | CFEPOptions__Cleanup | Named | Destroys resources, clears global pointer |
| 0x0051fff0 | CFEPOptions__EnumerateSaveFiles | Named | Populates save file list for UI |

**Total: 10 functions identified**

## Key Data References

| Address | Type | Purpose |
|---------|------|---------|
| 0x0063fc74 | String | `"defaultoptions.bea"` - config filename |
| 0x0063fc54 | String | `"Couldn't write defaultoptions"` - error message |
| 0x00660620 | Data | Global CCareer instance |
| 0x0089bc30 | Pointer | Options context pointer (`g_pOptionsContext`, was `DAT_0089bc30`) |

## Function Details

### CFEPOptions__SaveDefaultOptions (0x0051f500)
Saves the current career settings to `defaultoptions.bea`. Uses memory allocation with debug info from line 0xFA (250). Calls `CCareer__GetSaveSize()` and `CCareer__Save()` to serialize career data. Handles UI transition states.

Key operations:
1. Checks global state flags (DAT_008a1388, DAT_008a9584)
2. Allocates buffer using CCareer__GetSaveSize
3. Serializes career via CCareer__Save
4. Opens file for writing via `fopen` (0x0055e490, was `FUN_0055e490`)
5. Writes data and closes file
6. Frees allocated buffer

### CFEPOptions__WriteDefaultOptionsFile (0x0051f680)
Helper function that handles the low-level file I/O for writing default options. Opens `defaultoptions.bea`, writes the provided buffer, and closes the file. Shows error message on failure.

Signature (Steam build, verified):
- `void CFEPOptions__WriteDefaultOptionsFile(void * data, int size)`

Verified call chains:
- `CFEPLoadGame__DoLoad` (`0x00461e20`) on successful load when `DAT_0082b5b0 == 0`
- `Platform__AsyncSaveCareer` (`0x004d2580`) when prior `DAT_0082b5b0 == 2`
- `FUN_004d06e0` (PauseMenu path)
- `CFEPMain__Process` (`0x00462640`) at callsite `0x004628df` (paired with `CCareer__Save` at `0x00462893`)

### CFEPOptions__Update (0x0051f700)
Updates the options menu UI. Handles:
- Sound/music volume selection highlighting
- Float-based selection interpolation (0.75 to 1.0 range)
- Volume level visualization

Parameters:
- `param_1` (float): Current selection value
- `param_2` (int): Menu item index (0x12 and 0x13 are special cases)

### CFEPOptions__ProcessInput (0x0051f600)
State machine for processing menu input. Uses switch statement on `this+4` state field:
- Cases 0, 2, 3, 5: Increment state
- Case 4: Check for FEP transitions
- Default: Handle save confirmation

Calls CFEPOptions__SaveDefaultOptions when confirming settings.

### CFEPOptions__EnsureOptionsContext (0x0051f7e0)

SEH-protected vtable helper that snapshots current CCareer option globals into the options-page state and lazily allocates the options context pointer (`g_pOptionsContext` @ `0x0089bc30`) if needed.

Signature (Steam build, verified):
- `void CFEPOptions__EnsureOptionsContext(void * this, int msg)`

Behavior notes:
- When `msg == 0` or `msg == 0x16`, clears `this+0x04` and snapshots:
  - `CAREER_mSoundVolume`, `CAREER_mMusicVolume`
  - `CAREER_mVibration_P1/P2`, `CAREER_mControllerConfig_P1/P2`
  - kill-counter top-byte metadata via `CCareer__GetKillCounterTopByte_23F4/23F8`
- Updates a UI timer (`this+0x08 = PLATFORM__GetSysTimeFloat() + 2.0`) and lazily allocates `g_pOptionsContext` if NULL.

### CFEPOptions__EnumerateSaveFiles (0x0051fff0)
Populates the save file list for the options menu. Iterates through save directory:
1. Adds default entry from DAT_0063fd34
2. Enumerates save files using EnumerateSaveFiles_1/2
3. Checks for duplicates via FUN_0055f2e8
4. Limits list to 0x1f (31) entries maximum
5. Sets completion flag at `this+0x48`

### CFEPOptions__GetKillCounterTopBytes_23F4_23F8 (0x0051f470)
Getter that retrieves current **kill-counter top-byte metadata** from the global `CCareer` instance:

- `CCareer__GetKillCounterTopByte_23F4` (`0x004218f0`)
- `CCareer__GetKillCounterTopByte_23F8` (`0x00421900`)

These return `((killCounter >> 24) - 0x80)` (signed bias). Their use in the options UI needs further investigation.

### CFEPOptions__SetKillCounterTopBytes_23F4_23F8 (0x0051f490)
Setter that writes **kill-counter top-byte metadata** back into the global `CCareer` instance:

- `CCareer__SetKillCounterTopByte_23F4` (`0x00421910`)
- `CCareer__SetKillCounterTopByte_23F8` (`0x00421940`)

This sets the top byte while preserving the lower 24 bits: `((top+0x80)<<24) | (value & 0x00FFFFFF)`.

### Mapping Correction (0x0051fd50)
`0x0051fd50` was previously labeled `CFEPOptions__Init`, but live vtable/RTTI checks show it belongs to `CFEPScreenPos` slot 6:

- `CFEPScreenPos__TransitionNotification(void * this, int from_page)`

See [`FEPScreenPos.cpp/_index.md`](../FEPScreenPos.cpp/_index.md) for the class-local mapping.

### CFEPOptions__Cleanup (0x0051f8e0)
Cleanup handler that destroys resources:
1. Checks if `g_pOptionsContext` is non-null
2. Calls destructor via vtable (offset +4)
3. Sets global pointer to NULL

### CFEPOptions__GetState (0x0051f370)
Minimal getter that returns the state byte at `this+5`.

## Exception Handler

| Address | Function | Notes |
|---------|----------|-------|
| 0x005d6870 | Unwind@005d6870 | SEH exception unwind handler, not a class method |

This is a compiler-generated Structured Exception Handling (SEH) unwind function, not a CFEPOptions method. References the FEPOptions.cpp debug path at line 0x196 (406).

## Related Files

- [FEPSaveGame.cpp](../FEPSaveGame.cpp/_index.md) - Save game name checking, cheat codes
- [FEPLoadGame.cpp](../FEPLoadGame.cpp/_index.md) - Save file loading
- [Career.cpp](../Career.cpp/_index.md) - Career data structure (serialized by SaveDefaultOptions)

## Notes

- FEP = "Front End Page" - the game's menu system terminology
- `defaultoptions.bea` stores game settings separate from career saves
- Volume controls interact with global sound/music systems
- Menu uses a state machine pattern (state field at offset +4)
- Save file enumeration limits to 31 entries (0x1f)
