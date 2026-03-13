# CGame__ShutdownRestartLoop

> Address: `0x0046ca70` | Source: `references/Onslaught/game.cpp:530`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void CGame__ShutdownRestartLoop(void *this)`)
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:CGame::ShutdownRestartLoop`)

## Purpose
Tears down runtime state for the current restart-loop pass:
- stops music/scripts as needed
- frees per-level UI/runtime allocations
- clears map/fx/event/script systems
- shuts down EventManager and related temporary state

## Notes
- Called from both `CGame__RestartLoopRunLevel` and `CGame__RunLevel`.
- Pairs with `CGame__InitRestartLoop` (`0x0046c430`) and is central to restart/retry stability.
