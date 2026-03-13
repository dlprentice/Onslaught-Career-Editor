# PauseMenu.cpp Functions

> Source File: PauseMenu.cpp | Binary: BEA.exe

## Overview

Pause menu UI implementation. Handles the in-game pause menu, including cheat-dependent options like the god mode toggle.

## Functions

| Address | Name | Purpose |
|---------|------|---------|
| 0x004cde60 | [PauseMenu__Init](./PauseMenu__Init.md) | Pause menu constructor - calls IsCheatActive(3) for god mode toggle |
| 0x004d04d0 | CPauseMenu__ReloadSharedBlankTexture | Reloads shared blank texture used by pause-menu panel rendering |
| 0x004d0510 | CPauseMenu__LoadPauseTextures | Loads pause-menu texture resources |
| 0x004d06e0 | [CPauseMenu__ResumeGameAndPersistOptions](./CPauseMenu__ResumeGameAndPersistOptions.md) | Resume/exit helper that also persists options/defaultoptions state |
| 0x004d0810 | CPauseMenu__ButtonPressed | Pause-menu button dispatch handler |
| 0x004d0db0 | CPauseMenu__InitBindingPromptAction | Initializes binding-prompt action node with target menu item and dispatch id |
| 0x004d0de0 | CPauseMenu__GetBindingCapacityError | Control-binding capacity/error helper |
| 0x004d0ff0 | CPauseMenu__InitPauseSession | Initializes pause-session state/resources |

## Key Observations

### God Mode Toggle Discovery

At address 0x004ce328, PauseMenu UI logic uses `IsCheatActive(3)` (Maladim) for gating and uses `g_bGodModeEnabled` as the toggle state. This was a key discovery for separating:
1. Cheat gating (save-name substring check)
2. UI toggle state (persisted)
3. Per-player invincibility (runtime `CPlayer::mIsGod`; **not** a known persisted field in Steam saves)

- The pause menu checks `IsCheatActive(3)` (index 3 = "Maladim" cheat code)
- If active, a god mode toggle option appears in the pause menu
- The toggle reads/writes `g_bGodModeEnabled` (CCareer offset `0x2494`, file offset `0x2496`)

### Important Offsets

| CCareer Offset | File Offset | Field | Purpose |
|----------------|-------------|-------|---------|
| 0x2494 | 0x2496 | g_bGodModeEnabled | Pause-menu toggle state (cheat-gated) |
| 0x2498 | 0x249A | (unused/padding) | Observed 0 in Steam saves/options; preserve |
| 0x249C | 0x249E | Invert Y (Flight/Jet) (P1) | Steam stores `0=Off`, non-zero=On (verified in `FUN_00407540`) |
| 0x24A0 | 0x24A2 | Invert Y (Flight/Jet) (P2) | Steam stores `0=Off`, non-zero=On (verified in `FUN_00407540`) |
| 0x24A4 | 0x24A6 | Invert Y (Walker) (P1) | Steam stores `0=Off`, non-zero=On (verification pending on walker path) |
| 0x24A8 | 0x24AA | Invert Y (Walker) (P2) | Steam stores `0=Off`, non-zero=On (verification pending on walker path) |

**NOTE (Feb 2026):** In the retail build, `CCareer::Load/Save` copies bytes from/to `file + 2` after a 16-bit version word. So file offsets are `file_off = 0x0002 + career_off` (the header often *looks* like a 4-byte `0x00004BD1` if the first CCareer dword is 0).

## Related Files

- Career.cpp - Contains CCareer persisted settings (`g_bGodModeEnabled`, invert-Y arrays, controller config, etc.)
- FEPSaveGame.cpp - Cheat code activation via save name

---
*Migrated from ghidra-analysis.md (Dec 2025)*
