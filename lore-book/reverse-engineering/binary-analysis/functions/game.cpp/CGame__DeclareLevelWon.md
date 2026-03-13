# CGame__DeclareLevelWon

> Address: 0x0046f2f0 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void CGame__DeclareLevelWon(void *this)`)
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:CGame::DeclareLevelWon`)

## Purpose
Transitions the game to level-won state, stops controller vibration, sets end-level timer (with special-case levels), and pauses.

## Signature
```c
void CGame::DeclareLevelWon();
```
