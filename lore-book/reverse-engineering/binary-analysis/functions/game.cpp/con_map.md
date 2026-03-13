# con_map

> Address: 0x0046be10 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes (free function)
- **Signature Set:** Yes
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:84`)

## Purpose

Console command: `Map <map number>` to force-load a level by number and quit to the frontend to trigger the change.

## Notes (Binary Evidence)

- Parses `cmd` via `sscanf(cmd, "%*s %s", mapno)` (format string at `0x00624bb8`).
- On parse failure: prints usage string `Syntax : map <map number>\n` at `0x0062bb10`.
- On success:
  - Sets `SYSTEM.mNextLevel` at `0x00896ca4` (via `atoi(mapno)`).
  - Forces quit to frontend by writing `QT_QUIT_TO_FRONTEND` (value 9) into `g_QuitType` at `0x008a9ac0` and `g_QuitPending` at `0x008a9acc`.

## Related

- Registered in `CGame::InitRestartLoop()` (`CGame__InitRestartLoop`, `0x0046c430`) (command name `Map` at `0x0062be5c`).
