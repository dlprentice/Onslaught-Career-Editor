# CGame__DeclareLevelWon

> Address: 0x0046f2f0 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void CGame__DeclareLevelWon(void *this)`)
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:CGame::DeclareLevelWon`)

## Purpose
Transitions the game to level-won state, stops controller vibration, sets end-level timer (with special-case levels), and pauses.

2026-06-08 MissionScript Objective/Outcome Command-Effect static proof: `missionscript-objective-outcome-command-effect-static-proof.md` and `missionscript-objective-outcome-command-effect.v1.json` use this function as the CGame level-won transition bridge from `0x005381e0 IScript__LevelWon`, alongside `CGame__FillOutEndLevelData`, `CCareer__Update`, and `CEndLevelData__IsAllSecondaryObjectivesComplete`. This is static bridge accounting only; runtime command effects, runtime level outcome behavior, runtime save/career behavior, exact layout, patching, Godot, rebuild parity, and no-noticeable-difference parity remain separate proof.

## Signature
```c
void CGame::DeclareLevelWon();
```
