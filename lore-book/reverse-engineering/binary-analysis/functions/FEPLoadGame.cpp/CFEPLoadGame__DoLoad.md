# CFEPLoadGame__DoLoad

> Address: 0x00461e20 | Source: `references/Onslaught/FEPLoadGame.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Partial (binary behavior documented; full source parity not revalidated)

## Purpose

Executes the save file load operation when the user selects a save from the Load Game menu. This function handles reading the .bes file, validating it, and populating the career data structures.

## Signature
```c
void CFEPLoadGame__DoLoad(void * this);
```

## High-Confidence Behavior (Binary Evidence)

- Requires a selected save slot at `this+0x40`; if `-1` it logs a debug error and returns.
- Allocates a temp buffer of `size = CCareer__GetSaveSize()`.
- Reads the save file into the buffer via:
  - `PCPlatform__ReadSaveFile(device=DAT_008a9694, slot=this+0x40, save_name=this+0x44, out_buf, size, &bytesRead)`
  - Return convention: `0` indicates a full read, non-zero indicates failure.
- Loads career state into the global `CAREER` via:
  - `CCareer__Load(&CAREER, out_buf, flag=1)`
  - Return convention: non-zero indicates success.
- On successful load:
  - Transitions the frontend to the next page/state (success path).
  - Sets `DAT_008a9584 = 1` (frontend state flag used by save/load flows).
  - **Steam build nuance:** if `DAT_0082b5b0 == 0`, it writes `defaultoptions.bea` from the loaded buffer via `CFEPOptions__WriteDefaultOptionsFile(out_buf, size)`.
- Frees the temp buffer before returning.

### Steam Build Nuance: Sound/Music Volumes Preserved On Load

In the Steam build, save loading calls:

- `CCareer__Load(&DAT_00660620, source, 1)` (flag=1)

Inside `CCareer__Load` (`0x00421200`), when `flag != 0`, the function restores the pre-load values of:

- `this+0x248C` (Sound volume float)
- `this+0x2490` (Music volume float)

Meaning: patching sound/music volume floats inside a `.bes` save may not affect audio after loading that save. Boot-time audio comes from `defaultoptions.bea` (loaded with flag=0).

### defaultoptions.bea Side Effect

On successful load, `CFEPLoadGame__DoLoad` may call:

- `CFEPOptions__WriteDefaultOptionsFile(source, size)`

This can cause `defaultoptions.bea` to become identical to the last-loaded save buffer (and therefore apply on next boot, since boot loads `defaultoptions.bea` with `flag=0`).

## File Format Reference

| Offset | Size | Content |
|--------|------|---------|
| 0x0000 | 2 | Version word (0x4BD1) |
| 0x0002 | 4 | `new_goodie_count` (CCareer +0x0000) |
| 0x0006 | 6400 | CCareerNode[100] |
| 0x1906 | 1600 | CCareerNodeLink[200] |
| 0x1F46 | 1200 | Goodies[300] |
| 0x23F6 | 20 | Kill counters[5] |
| 0x240A | 128 | Tech slots[32] |
| ... | ... | Settings and metadata |

## Error Handling

Known failure behaviors (partial):
- If the device/card is absent or unformatted, it routes through the frontend error/whinge path and returns.
- If `PCPlatform__ReadSaveFile` fails, it shows an error message and returns to the frontend.
- If `CCareer__Load` fails, it shows an error message and returns to the frontend.

## Post-Load Cheat Checking

After loading, the save game name is available for cheat code checking. Functions like `IsCheatActive()` use `strstr()` to check if the loaded save name contains any cheat codes (MALLOY, TURKEY, V3R5IOF, Maladim, Aurore, latête). (Source/internal strings differ: V3R5ION/B4K42.)

## Cross-References

### Calls
- File I/O functions (fopen, fread, fclose)
- Career data parsing functions

### Called By
- Frontend menu system when user confirms load selection

### Related
- `CCareer::Load` - lower-level career loading function
- `IsCheatActive` - uses save name after load

## Notes

- Migrated from ghidra-analysis.md (Dec 2025)
- The loaded save name determines which cheats are active
- File validation is important - corrupted saves can cause crashes
