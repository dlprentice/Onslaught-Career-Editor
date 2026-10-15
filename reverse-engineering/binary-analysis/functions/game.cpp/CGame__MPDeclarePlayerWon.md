# CGame__MPDeclarePlayerWon

> Address: 0x0046f360 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void CGame__MPDeclarePlayerWon(void *this, int number)`)
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:CGame::MPDeclarePlayerWon`)

## Purpose
Multiplayer winner declaration for player 1/2: sets winner game-state, disables vibration, sets end-level countdown, and pauses.

## Signature
```c
void CGame::MPDeclarePlayerWon(int number);
```
