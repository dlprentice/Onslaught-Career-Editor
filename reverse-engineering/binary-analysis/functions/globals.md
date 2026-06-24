# Global Variables

> Global variable mappings for BEA.exe (Steam version)
> Migrated from ghidra-analysis.md - December 2025

## Overview

Global variables discovered during reverse engineering. Many are in BSS (uninitialized data) and cannot be file-patched.

---

## Cheat System Globals

| Address | Name | Type | Section | Notes |
|---------|------|------|---------|-------|
| 0x00662df4 | g_bDevModeEnabled | BOOL | BSS | If non-zero, all cheats active |
| 0x00679ec1 | g_bAllCheatsEnabled | BOOL | BSS | If non-zero, all cheats active |
| 0x00662ab4 | g_bGodModeEnabled | BOOL | BSS | Current god mode state |
| 0x00662f3e | DAT_00662f3e | BOOL | BSS | Guard flag for -forcewindowed |

**Note:** BSS variables are zero-initialized at runtime and cannot be modified via file patching.

---

## Cheat Code Data

| Address | Name | Size | Notes |
|---------|------|------|-------|
| 0x00629464 | g_CheatCodes[0] | 256 | MALLOY (XOR encrypted) |
| 0x00629564 | g_CheatCodes[1] | 256 | TURKEY (XOR encrypted) |
| 0x00629664 | g_CheatCodes[2] | 256 | V3R5IOF (XOR encrypted; decoded from BEA.exe) |
| 0x00629764 | g_CheatCodes[3] | 256 | Maladim (XOR encrypted) |
| 0x00629864 | g_CheatCodes[4] | 256 | Aurore (XOR encrypted) |
| 0x00629964 | g_CheatCodes[5] | 256 | lat\xEAte (XOR encrypted; decoded from BEA.exe) |
| 0x00629a64 | g_XORKey | 9 | "HELP ME!!" |

---

## Version/Config Data

| Address | Name | Type | Notes |
|---------|------|------|-------|
| 0x00623e24 | DAT_00623e24 | int | Version component (0x11), used in stamp calc |

**Version Stamp Formula:** `0x11 + 0x4BC0 = 0x4BD1`

---

## Code Locations (Not Variables)

These are code addresses, not data, but useful for patching:

| Address | Purpose | Patch Notes |
|---------|---------|-------------|
| 0x004654a0 | IsCheatActive return-path branch | Legacy: change 75→EB (does not force TRUE for all cases) |
| 0x00465490 | IsCheatActive prologue | Force TRUE (archived; breaks goodies unless `lat\xEAte` is mitigated) |
| 0x0045D819 | Goodies UI (`CFEPGoodies::Process`) | Dev-mode fix: force `g_Cheat_LATETE = 0` (see `patches/patch_devmode_goodies_logic_fix.py`) |
| 0x004ce328 | PauseMenu god mode toggle | Cheat-gated UI; uses `g_bGodModeEnabled` as the toggle state |

---

## Console Variables (CVars)

Console variables registered via CConsole__RegisterVariable:

### Gamut/Visibility System (gcgamut.cpp)

| Address | Name | Type | Default | Notes |
|---------|------|------|---------|-------|
| 0x0067a070 | cg_gamutlocked | bool | 0 | Freezes gamut calculation |
| 0x0067a071 | cg_showgamut | bool | 0 | Displays gamut visualization |
| 0x0062c8c4 | cg_renderimposters | bool | ? | Controls imposter rendering |

---

## Inquisition Agent Discoveries (December 2025)

The following globals were discovered via automated Inquisition agents during deep binary analysis.

### Singleton Pointers

| Address | Name | Type | Notes |
|---------|------|------|-------|
| 0x0066e99c | g_pPhysicsScript | CPhysicsScript* | Physics script singleton |
| 0x008a1374 | g_pSaveGame | CFEPSaveGame* | Save game instance |

### Game State Flags

| Address | Name | Type | Notes |
|---------|------|------|-------|
| 0x00662b20 | g_bNewGoodieFlag | BOOL | New goodie unlock flag |
| 0x00662b24 | g_bNewTechFlag | BOOL | New tech unlock flag |
| 0x00662dd0 | g_FrontendState | BOOL | Frontend active flag |

### Constants

| Address | Name | Value | Notes |
|---------|------|-------|-------|
| 0x00624184 | NUM_LEVELS | 43 | Mission count constant |

### Cheat/Easter Egg Timing

| Address | Name | Type | Notes |
|---------|------|------|-------|
| 0x00679ec8 | g_DevModeTimer | int | Easter egg timing counter |
| 0x00679f9c | g_CheatCheckCounter | int | Frame counter for cheat detection |
| 0x00679fa0 | g_CheatCheckState | int | Directory/state tracking |

---

## Discovery Methods

1. **Xref from functions** - Follow references from IsCheatActive
2. **String search** - Find error messages, trace to globals
3. **Ghidra data references** - Analyze data section access patterns
4. **Inquisition agents** - Automated deep analysis (December 2025)

---

## Related

- [FEPSaveGame.cpp/_index.md](FEPSaveGame.cpp/_index.md) - Cheat system details
- [PauseMenu.cpp/_index.md](PauseMenu.cpp/_index.md) - God mode toggle
- [CLIParams.cpp/_index.md](CLIParams.cpp/_index.md) - CLI flags
