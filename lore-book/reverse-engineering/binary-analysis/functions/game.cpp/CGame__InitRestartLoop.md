# CGame__InitRestartLoop

> Address: `0x0046c430` | Source: `references/Onslaught/game.cpp:292`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`int CGame__InitRestartLoop(void *this)`)
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:CGame::InitRestartLoop`)

## Purpose
Initializes per-level/restart runtime state:
- resets cameras/controllers/objective state
- initializes EventManager, particles, interface, render queue
- allocates runtime UI/helper objects (message box/log/pause/help/briefing/random stream)
- registers gameplay console commands/CVars

## Notes
- Contains `CONSOLE.RegisterCommand(...)` and `CONSOLE.RegisterVariable(...)` blocks for `Map/Win/Lose/RemoteCamera/NavMap` and split-screen/frame-length CVars.
- Calls `CEventManager__Init` and seeds pre-run state/event.
- This is distinct from `CGame__Init` (`0x0046c360`), which performs broader startup subsystem initialization.
