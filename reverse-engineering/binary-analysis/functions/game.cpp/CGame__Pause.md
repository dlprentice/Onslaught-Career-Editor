# CGame__Pause

> Address: 0x0046fb00 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void CGame__Pause(void *this, int toggle_pause_menu, void *from_controller)`)
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:CGame::Pause`)

## Purpose
Pause entrypoint: sets pause flag, disables vibration on active controllers, and optionally activates pause menu + controller handoff.

## Signature
```c
void CGame::Pause(BOOL toggle_pause_menu, CController *from_controller);
```
