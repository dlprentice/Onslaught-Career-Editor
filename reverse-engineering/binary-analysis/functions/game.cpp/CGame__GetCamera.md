# CGame__GetCamera

> Address: 0x0046f2c0 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void * CGame__GetCamera(void *this, int number)`)
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:CGame::GetCamera`)

## Purpose
Returns the active camera pointer for a player slot (`mCurrentCamera[number]`).

## Signature
```c
void* CGame::GetCamera(int number);
```
