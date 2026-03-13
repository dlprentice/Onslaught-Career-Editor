# FEPSaveGame.cpp - Function Index

> Source File: FEPSaveGame.cpp | Category: Frontend/Save System

## Overview

Frontend save game menu implementation. Contains the XOR-encrypted cheat code system that checks save game names for special codes.

## Functions

| Address | Function | Status | Description |
|---------|----------|--------|-------------|
| 0x00464c50 | [CFEPSaveGame__CreateSave](./CFEPSaveGame__CreateSave.md) | Named | Creates/overwrites save and writes `.bes` via `CCareer__SaveWithFlag` + `PCPlatform__WriteSaveFile` |
| 0x00465490 | [IsCheatActive](./IsCheatActive.md) | Named | XOR decrypts cheat codes, checks save name via strstr() |

## Cheat Code System

The PC port uses XOR-encrypted cheat codes checked against save game names at runtime.

### Memory Locations

| Address | Size | Purpose |
|---------|------|---------|
| 0x00629a64 | 10 bytes | XOR decryption key: `"HELP ME!!"` |
| 0x00629464 | ~1280 bytes | Cheat code table (256 bytes per cheat) |
| 0x00662df4 | 1 byte | `g_bDevModeEnabled` - enables all cheats if set |
| 0x00679ec1 | 1 byte | `g_bAllCheatsEnabled` - enables all cheats if set |

### Known Cheat Codes

| Index | Code | Effect | Status |
|-------|------|--------|--------|
| 0 | `MALLOY` | All goodies | Works (Dec 2025 user testing confirmed) |
| 1 | `TURKEY` | All levels | Works |
| 2 | `V3R5IOF` | Version display | Decoded from BEA.exe; no call sites found (needs in-game confirmation) |
| 3 | `Maladim` | God mode toggle UI | Call site found; no visible effect in user testing (needs investigation) |
| 4 | `Aurore` | Free camera debug toggle | Verified in binary (gates `BUTTON_TOGGLE_FREE_CAMERA`) |
| 5 | `latête` | Goodie UI override | Verified in binary (sets `g_Cheat_LATETE`; forces displayed goodie state to `1`) |

**Note:** Stuart's source/internal build uses `V3R5ION` (index 2) and `B4K42` (index 3). In the Steam retail build, the XOR-decrypted cheat table yields `V3R5IOF` at index 2. See `reverse-engineering/game-mechanics/cheat-codes.md` and `tools/cheat_table_decode.py`.

### How It Works

1. `IsCheatActive(int index)` is called with cheat index
2. First checks `g_bDevModeEnabled` and `g_bAllCheatsEnabled` - returns TRUE if either set
3. XOR-decrypts the cheat code at `0x00629464 + (index * 256)` using key `"HELP ME!!"`
4. Uses `strstr()` to check if the current save name **contains** the decrypted code
5. Returns TRUE if found, FALSE otherwise

### Important Notes

- **B4K42 is NOT in IsCheatActive!** The source code shows B4K42, but Ghidra reveals the binary uses `Maladim` for god mode (index 3)
- Cheat codes use **substring matching** via `strstr()` - code can appear anywhere in save name
- The MALLOY cheat works correctly via save name (Dec 2025 user testing); Ghidra-discovered inverted logic may only affect dev mode

## Cross-References

- Called by: FEPGoodies, PauseMenu, various game systems
- Related: [FEPGoodies.cpp](../FEPGoodies.cpp/_index.md) - uses IsCheatActive for goodie unlocks
- Related: [FEPLoadGame.cpp](../FEPLoadGame.cpp/_index.md) - loads save files that contain names checked by cheats

## Migration Notes

- Migrated from ghidra-analysis.md (Dec 2025)
- Cheat system discovered via Ghidra analysis of IsCheatActive
