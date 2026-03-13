# CGame__DeclareLevelLost

> Address: 0x0046f430 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void CGame__DeclareLevelLost(void *this, int message, int player_died)`)
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:CGame::DeclareLevelLost`)

## Purpose
Level-loss transition logic: stores/prints loss reason, sets level-lost state/timers, stops vibration, and triggers pause behavior (immediate or delayed depending on `player_died`).

## Signature
```c
void CGame::DeclareLevelLost(int message, BOOL player_died);
```
