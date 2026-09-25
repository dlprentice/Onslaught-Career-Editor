# Global Variables

Status: mixed — inherited mappings with scoped instruction-backed corrections
Last updated: 2026-09-19
Summary: legacy global map; distinguish CLI developer selection from autoconfig and its cheat-query bypass.
Source File: multiple pinned reference files; see the CLI contract | Binary: pristine BEA.exe.original.backup, SHA-256 74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750

> Global variable mappings for BEA.exe (Steam version)
> Migrated from ghidra-analysis.md - December 2025

## Overview

Global variables discovered during reverse engineering. Many are in BSS (uninitialized data) and cannot be file-patched.
The inherited rows are not all revalidated by the September 19 correction.

---

## Cheat System Globals

| Address | Name | Type | Section | Notes |
|---------|------|------|---------|-------|
| 0x00662df4 | CLIParams `+3c` autoconfig-test flag | 32-bit value | BSS | Set by `-autoconfigtest`; nonzero also makes retail `IsCheatActive` return true before name/code checks. Legacy alias `g_bDevModeEnabled` conflated it with the separate `+18` selector. |
| 0x00679ec1 | g_bAllCheatsEnabled | byte | BSS | Nonzero takes the same early true-return branch in `IsCheatActive`; `CGame__Update` sets this byte at `0046ea34`. |
| 0x00662ab4 | g_bGodModeEnabled | BOOL | BSS | Current god mode state |
| 0x00662f3e | DAT_00662f3e | byte | BSS | Global guard for `-forcewindowed`; initializer clears it, `-testeur` sets it on the normal CLI receiver. |

**Note:** BSS variables are zero-initialized at runtime and cannot be modified via file patching.

The [cheat-query correction](FEPSaveGame.cpp/IsCheatActive.md#autoconfig-identity-correction--september-19)
preserves the proven bypass behavior while correcting its field identity.

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
| 0x0045D819 | Goodies UI (`CFEPGoodies::Process`) | Historical dev-mode mitigation candidate: force `g_Cheat_LATETE = 0`; no active product row |
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
| 0x00662dd0 | CLIParams `+18` developer selector | 32-bit value | Initializer clears it; ten absolute reads span actor, water-death, scheduler, frontend, game and logger code. Some test exactly `1`, others nonzero. The old `g_FrontendState` / "Frontend active flag" label was wrong. |

The [CLI consumer audit](CLIParams.cpp/CLIParams__ParseCommandLine.md#developer-selector-and-trace-consumers--september-19)
binds the exact instructions, source counterparts and private evidence. The
frontend is one consumer of this selector. No later deliberate writer was
identified; this is not proof against computed-pointer writes or external changes.

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

- [Save-game cheat check](FEPSaveGame.cpp/IsCheatActive.md)
- [Pause-menu rendering](PauseMenu.cpp/CPauseMenu__Render.md)
- [CLI parameter parsing](CLIParams.cpp/CLIParams__ParseCommandLine.md)
