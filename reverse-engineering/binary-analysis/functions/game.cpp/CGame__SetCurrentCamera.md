# CGame__SetCurrentCamera

> Address: 0x004705e0 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:CGame::SetCurrentCamera`)

## Purpose
Sets the active camera for a player slot, with special handling when free camera mode is active:

- If free camera is on, updates `mOldCamera[player]`
- Otherwise, updates `mCurrentCamera[player]`

Optionally releases (deletes) the previous camera pointer.

## Signature
```c
// __thiscall, pops 0xC (3 args)
void CGame::SetCurrentCamera(int player, void* camera /* CCamera* */, bool releaseoldcamera);
```

## Binary Observations
This function matches the source logic at `references/Onslaught/game.cpp:3308`:

- `mFreeCameraOn[player]` is stored as a dword array at `this + 0x9D0`
- `mCurrentCamera[player]` pointers at `this + 0x2C4`
- `mOldCamera[player]` pointers at `this + 0x2D4`

Pseudo-logic:
```c
if (mFreeCameraOn[player] == TRUE) {
    if (releaseoldcamera && mOldCamera[player]) delete mOldCamera[player];
    mOldCamera[player] = camera;
} else {
    if (releaseoldcamera && mCurrentCamera[player]) delete mCurrentCamera[player];
    mCurrentCamera[player] = camera;
}
```

## Related Functions
- `CGame__ToggleFreeCameraOn` (`0x00470430`) creates a controllable camera and then calls this with `releaseoldcamera=false`.
- `CGame__ReceiveButtonAction` (`0x0046f7e0`) uses this in the free-camera-off path (`releaseoldcamera=true`).

