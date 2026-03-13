# CGame__StartPlayingState

> Address: 0x0046fec0 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void CGame__StartPlayingState(void *this)`)
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:CGame::StartPlayingState`)

## Purpose
Transitions from pre-run/panning to active gameplay, posts `"game playing"` script event, and schedules message-box enable event.

## Signature
```c
void CGame::StartPlayingState();
```
