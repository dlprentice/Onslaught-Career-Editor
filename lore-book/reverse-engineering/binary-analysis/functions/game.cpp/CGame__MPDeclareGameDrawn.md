# CGame__MPDeclareGameDrawn

> Address: 0x0046f3e0 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void CGame__MPDeclareGameDrawn(void *this)`)
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:CGame::MPDeclareGameDrawn`)

## Purpose
Multiplayer draw declaration path: sets draw state, disables vibration, sets end-level countdown, then pauses.

## Signature
```c
void CGame::MPDeclareGameDrawn();
```
