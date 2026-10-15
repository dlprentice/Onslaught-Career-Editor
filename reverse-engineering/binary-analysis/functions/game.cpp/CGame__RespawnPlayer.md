# CGame__RespawnPlayer

> Address: 0x00470120 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void CGame__RespawnPlayer(void *this, int playernumber)`)
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:CGame::RespawnPlayer`)

## Purpose
Respawn flow for multiplayer/co-op: life checks, spawn/start selection, battle-engine reassignment, and retry event scheduling when spawn fails.

## Signature
```c
void CGame::RespawnPlayer(SINT inNumber);
```
