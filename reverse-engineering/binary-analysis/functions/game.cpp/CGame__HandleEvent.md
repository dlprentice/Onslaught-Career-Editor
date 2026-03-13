# CGame__HandleEvent

> Address: 0x0046ff10 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void CGame__HandleEvent(void *this, void *event)`)
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:CGame::HandleEvent`)

## Purpose
Primary game-event dispatcher for run-state transitions and scheduled gameplay events, including respawn events and pause/fade continuation events.

## Signature
```c
void CGame::HandleEvent(CEvent *event);
```
