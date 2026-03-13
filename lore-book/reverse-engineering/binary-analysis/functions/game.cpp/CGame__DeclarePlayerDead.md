# CGame__DeclarePlayerDead

> Address: 0x0046f550 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void CGame__DeclarePlayerDead(void *this, int number)`)
- **Verified vs Source:** Mostly (`references/Onslaught/game.cpp:CGame::DeclarePlayerDead`; retail path includes build-specific branching)

## Purpose
Death-handling path for a player slot: exits free camera when needed, switches to death/pan camera, then routes to single-player loss or multiplayer respawn scheduling.

## Signature
```c
void CGame::DeclarePlayerDead(int number);
```
