# CGame__ToggleDebugSquadForward

> Address: 0x0046fe20 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Partial (mapped via `CGame__ReceiveButtonAction` button=3)

## Purpose
Advances the currently selected debug squad forward (used by debug render paths that draw squad debug info).

Source reference: `references/Onslaught/game.cpp:CGame::ToggleDebugSquadForward()`.

## Signature
```c
// __thiscall, no stack args
void CGame::ToggleDebugSquadForward(void);
```

## Notes
- Invoked by `BUTTON_TOGGLE_DEBUG_SQUAD_FORWARD` (Controller.h = 3).
- Emits warnings when an expected squad cannot be resolved (see `"Warning: can't find squad %d to debug"` in `game.cpp`).

