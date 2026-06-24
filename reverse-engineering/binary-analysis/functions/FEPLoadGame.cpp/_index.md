# FEPLoadGame.cpp - Function Index

> Source File: FEPLoadGame.cpp | Category: Frontend/Load Game Menu

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Frontend load game menu implementation. Handles save file selection and loading from the menu system.

Wave802 static read-back (`frontend-save-multiplayer-wave802`, `wave802-readback-verified`) ties FEPLoadGame message prompts to shared `0x0044d390 FEMessBox__Create`, not a save-game-owned helper. The saved signature is `int __thiscall FEMessBox__Create(...)`; `RET 0x2c` proves eleven explicit stack arguments after `ECX=this`, and `CFEPLoadGame__DoLoad` has direct xrefs to the same message-box create body. Verified backup: `G:\GhidraBackups\BEA_20260524-081932_post_wave802_frontend_save_multiplayer_verified`. Exact FEMessBox layout, runtime load dialog behavior, BEA patching, and rebuild parity remain deferred.

Wave954 (`save-load-directory-review-wave954`) re-reviewed the frontend save/load/directory handoff around `0x00461c40 CFEPLoadGame__Init`, `0x00464620 CFEPSaveGame__Init`, and `0x0051ad30 CFEPDirectory__RefreshSaveFileList`. Fresh evidence ties load context through `CFEPLoadGame__DoLoad`, `CFEPOptions__WriteDefaultOptionsFile`, directory refresh/listing, and live `0x00514ec0 PCPlatform__DeleteSaveFile`; debug strings include `C:\dev\ONSLAUGHT2\FEPSaveGame.cpp` and `C:\dev\ONSLAUGHT2\FEPDirectory.cpp`. no mutation was needed. Wave911 focused re-audit progress after Wave954 is `283/1408 = 20.10%`; static closure remains `6151/6151 = 100.00%`; verified backup: `G:\GhidraBackups\BEA_20260528-100717_post_wave954_save_load_directory_review_verified`.

## Functions

| Address | Function | Status | Description |
|---------|----------|--------|-------------|
| 0x00461c40 | [CFEPLoadGame__Init](./CFEPLoadGame__Init.md) | Named | Initialize load-game selection state |
| 0x00461c60 | [CFEPLoadGame__ButtonPressed](./CFEPLoadGame__ButtonPressed.md) | Named | Handle frontend load-game menu input |
| 0x00461d60 | [CFEPLoadGame__Process](./CFEPLoadGame__Process.md) | Named | Process load-game menu state and dispatch load |
| 0x00461d90 | [CFEPLoadGame__Render](./CFEPLoadGame__Render.md) | Named | Render load-game menu title, borders, overlay, and help prompt |
| 0x00461e20 | [CFEPLoadGame__DoLoad](./CFEPLoadGame__DoLoad.md) | Named | Execute save file load from menu selection |
| 0x00464b10 | [FEPSaveLoad__TransitionNotification](../FEPSaveGame.cpp/FEPSaveLoad__TransitionNotification.md) | Named | Shared save/load transition timer hook |

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
