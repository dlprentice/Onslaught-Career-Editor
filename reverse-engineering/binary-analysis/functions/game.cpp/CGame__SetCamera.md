# CGame__SetCamera

> Address: 0x0046f2d0 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void CGame__SetCamera(void *this, int number, void *cam)`)
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:CGame::SetCamera`)

## Purpose
Thin wrapper that assigns a player camera via `CGame__SetCurrentCamera(number, cam, false)`.

## Signature
```c
void CGame::SetCamera(int number, CCamera *cam);
```
