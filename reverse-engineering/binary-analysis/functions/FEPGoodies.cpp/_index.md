# FEPGoodies.cpp - Function Index

> Source File: FEPGoodies.cpp | Category: Frontend/Goodies Gallery

## Overview

Frontend goodies gallery implementation. Displays unlockable content (artwork, models, videos) based on player progress and cheat codes.

**NOTE:** Ghidra analysis found inverted logic in this file, but user testing (Dec 2025) confirmed MALLOY works without any patch. The inverted logic may only affect the `g_bAllCheatsEnabled` dev mode code path.

## Functions

| Address | Function | Status | Description |
|---------|----------|--------|-------------|
| 0x0045ac30 | [CFEPGoodies__BuildStaticGoodieDataTable](./CFEPGoodies__BuildStaticGoodieDataTable.md) | Verified | Static goodie entry table materializer (bulk `CGoodieData__ctor` writes into global goodies metadata array) |
| 0x0045c770 | [CGoodieData__ctor](./CGoodieData__ctor.md) | Verified | `CGoodieData` field ctor helper (`Method/Method2/Number/Number2/mT1/mT2`) |
| 0x0045c870 | [CFEPGoodies__Deserialise](./CFEPGoodies__Deserialise.md) | Verified | `GDIE` resource chunk deserializer (textures/mesh load into current goody payload) |
| 0x0045c9f0 | [CFEPGoodies__StartLoadingGoody](./CFEPGoodies__StartLoadingGoody.md) | Verified | Computes selected goody id/type and starts async loading path |
| 0x0045cb80 | [get_goodie_number](./get_goodie_number.md) | Verified | Static helper mapping grid `(x,y)` to goodie id |
| 0x0045cc10 | [CFEPGoodies__LoadingGoodyPoll](./CFEPGoodies__LoadingGoodyPoll.md) | Verified | Polls async load and transitions to loaded state |
| 0x0045cd10 | [CFEPGoodies__FreeUpGoodyResources](./CFEPGoodies__FreeUpGoodyResources.md) | Verified | Releases current goody mesh/textures and resets loader state |
| 0x0045d7e0 | [CFEPGoodies__Process](./CFEPGoodies__Process.md) | Named | Main goodies process/update loop; sets cheat flags for gating/UI overrides |

## Cheat Flags and Goodie State Overrides

The binary derives two runtime flags from the save-name cheat system and uses them in multiple goodies UI paths:

| Address | Name | Set By | Effect |
|---------|------|--------|--------|
| 0x006798b0 | `g_Cheat_MALLOY` | `IsCheatActive(0)` | Treats displayed goodie state as `GS_OLD` (3) |
| 0x006798b4 | `g_Cheat_LATETE` | `IsCheatActive(5)` | Treats displayed goodie state as `GS_INSTRUCTIONS` (1) |

Goodie state is read from the global career instance:

- `CCareer` base: `0x00660620`
- `CGoodie[300]` base: `0x00660620 + 0x1F44 = 0x00662564`

UI code patterns:

- Gating/selection logic near `0x0045d048` checks these flags before consulting `CCareer.mGoodies[i]`.
- Color/display logic (examples: `0x0045e4a9`, `0x0045e62c`) uses the flags to override the effective state used for rendering.

**Prior note (deprecated):** earlier docs suggested patching `0x0045D04E` / `0x0045D056` (JNZ/JZ). After deeper tracing, these jumps appear to be part of normal state/cheat gating and should not be patched.

If you want dev mode (`g_bAllCheatsEnabled`) to behave like “MALLOY only” inside the goodies gallery, the safer patch is:
- `0x0045D819` (file `0x5D819`): `F7 D8` (NEG EAX) -> `33 C0` (XOR EAX,EAX), forcing `g_Cheat_LATETE = 0` before it is stored.
- Script: `patches/patch_devmode_goodies_logic_fix.py`

## Goodie Unlock System

Goodies are unlocked based on:
1. Kill count thresholds (aircraft, vehicles, emplacements, infantry, mechs)
2. Mission completion grades (A-rank and S-rank bonuses)
3. Level completion
4. Cheat codes (MALLOY - works without patch)

Cheats relevant to goodies:

- `MALLOY` (index 0) sets `g_Cheat_MALLOY` and overrides displayed state to `GS_OLD` (3).
- `lat\xEAte` (index 5, decoded from BEA.exe) sets `g_Cheat_LATETE` and overrides displayed state to `GS_INSTRUCTIONS` (1).

## Cross-References

- Calls: `IsCheatActive` (0x00465490) - in [FEPSaveGame.cpp](../FEPSaveGame.cpp/_index.md)
- Related: [Career.cpp](../Career.cpp/_index.md) - goodie unlock conditions

## Migration Notes

- Migrated from ghidra-analysis.md (Dec 2025)
- Bug discovered via Ghidra analysis comparing source code logic to compiled binary
