# con_remotecameraoff

> Address: 0x0046c0b0 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes (free function)
- **Signature Set:** Yes
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:149`)

## Purpose

Console command: `RemoteCameraOff` disables the remote camera and returns to the previous camera.

## Notes (Binary Evidence)

- If `GAME.mRemoteCamera` (`0x008a9e50`) is null:
  - Prints `Remote camera not active!\n` (`0x0062bc04`)
- If `GAME.mOldRemoteCamera` (`0x008a9e54`) is null:
  - Prints `No camera to return to!\n` (`0x0062bbe8`)
- Otherwise:
  - Calls `CGame::SetCurrentCamera(player=0, camera=GAME.mOldRemoteCamera, releaseOld=false)` at `0x004705e0`
  - Clears `GAME.mOldRemoteCamera`
  - Deletes `GAME.mRemoteCamera` and clears it

## Related

- Registered in `CGame::InitRestartLoop()` (`CGame__InitRestartLoop`, `0x0046c430`):
  - Name `RemoteCameraOff` at `0x0062be98`
  - Description `Turn off the remote camera` at `0x0062bea8`
