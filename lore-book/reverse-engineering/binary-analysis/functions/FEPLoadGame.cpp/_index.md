# FEPLoadGame.cpp - Function Index

> Source File: FEPLoadGame.cpp | Category: Frontend/Load Game Menu

## Overview

Frontend load game menu implementation. Handles save file selection and loading from the menu system.

## Functions

| Address | Function | Status | Description |
|---------|----------|--------|-------------|
| 0x00461e20 | [CFEPLoadGame__DoLoad](./CFEPLoadGame__DoLoad.md) | Named | Execute save file load from menu selection |

## Save File Loading Flow

1. User navigates to Load Game menu
2. Menu displays available save files from the savegames folder
3. User selects a save file
4. `CFEPLoadGame::DoLoad` is called
5. Career data is loaded via `CCareer::Load(&g_Career, buffer, 1)`
6. **Steam build nuance:** `CCareer::Load(..., flag=1)` preserves existing Sound/Music volume floats (see `CCareer__Load` at `0x00421200`)
7. Save name is extracted for cheat code checking
8. Game state is restored
9. The game may also write `defaultoptions.bea` from the loaded buffer (see `CFEPLoadGame__DoLoad` calling `CFEPOptions__WriteDefaultOptionsFile`)

## Related Systems

- **Cheat Checking:** After loading, the save name is used by `IsCheatActive()` to determine which cheats are enabled
- **Career System:** Loaded data populates `CCareer` struct with nodes, links, goodies, kills
- **Level Select UI:** [`FEPLevelSelect.cpp`](../FEPLevelSelect.cpp/_index.md) consumes unlocked-world state for world wheel selection/highlighting
- **Save Discovery:** Steam build uses `<game dir>/savegames/` (e.g. `C:\\Program Files (x86)\\Steam\\steamapps\\common\\Battle Engine Aquila\\savegames\\`)
- **Global Options:** Boot loads `defaultoptions.bea` (see `CLTShell__WinMain` at `0x00512130`)

## Cross-References

- Related: [FEPSaveGame.cpp](../FEPSaveGame.cpp/_index.md) - save game menu and cheat system
- Related: [Career.cpp](../Career.cpp/_index.md) - career data structures and loading

## Migration Notes

- Migrated from ghidra-analysis.md (Dec 2025)
