# CGame__DeclareLevelLost

> Address: 0x0046f430 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void CGame__DeclareLevelLost(void *this, int message, int player_died)`)
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:CGame::DeclareLevelLost`)

## Purpose
Level-loss transition logic: stores/prints loss reason, sets level-lost state/timers, stops vibration, and triggers pause behavior (immediate or delayed depending on `player_died`).

2026-06-08 MissionScript Objective/Outcome Command-Effect static proof: `missionscript-objective-outcome-command-effect-static-proof.md` and `missionscript-objective-outcome-command-effect.v1.json` use this function as the CGame level-lost transition bridge from `0x005381a0 IScript__LevelLost` and `0x005381c0 IScript__LevelLostString`, alongside `CGame__FillOutEndLevelData`, `CCareer__Update`, and `CEndLevelData__IsAllSecondaryObjectivesComplete`. This is static bridge accounting only; runtime command effects, runtime level outcome behavior, runtime save/career behavior, exact layout, patching, Godot, rebuild parity, and no-noticeable-difference parity remain separate proof.

## Signature
```c
void CGame::DeclareLevelLost(int message, BOOL player_died);
```
