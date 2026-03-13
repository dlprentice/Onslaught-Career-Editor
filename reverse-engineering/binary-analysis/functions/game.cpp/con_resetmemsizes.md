# con_resetmemsizes

> Address: 0x0046be80 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes (free function)
- **Signature Set:** Yes
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:100`)

## Purpose

Console command: `ResetMemSizes` resets the baseline used by the memory counters.

## Notes (Binary Evidence)

- Implements the loop `for (i=0; i<MEMTYPE_LIMIT; i++) GAME.mLastSize[i] = ...` as a single `rep movsd` copy:
  - Copies `0x81` dwords from `0x009c405c` to `0x008a9e58`.

## Related

- Registered in `CGame::InitRestartLoop()` (`CGame__InitRestartLoop`, `0x0046c430`):
  - Name `ResetMemSizes` at `0x0062bd98`
  - Description `Resets the baseline for the memory counters` at `0x0062bda8`
