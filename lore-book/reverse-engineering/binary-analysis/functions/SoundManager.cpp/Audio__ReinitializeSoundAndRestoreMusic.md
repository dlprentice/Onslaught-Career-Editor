# Audio__ReinitializeSoundAndRestoreMusic

> Address: `0x004cddf0`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void __cdecl Audio__ReinitializeSoundAndRestoreMusic(int frontend_music_after_reset)`)
- **Verified vs Source:** No exact Stuart source method identified; source and saved helpers confirm the underlying sound/music operations.

## Purpose
Reinitializes the global sound manager after sound-device/settings changes, then restores either frontend music or current-level music.

## Behavior Summary
- Calls `CSoundManager__ReinitializeAfterDeviceLoss(&DAT_00896988)`.
- Tests the low byte of `frontend_music_after_reset`.
- If nonzero and global music is enabled (`DAT_00662dcc`), calls `CMusic__PlaySelection(&DAT_00889a48, 0, 0)`.
- If zero, calls `CGame__PlayMusicForCurrentLevel(&DAT_008a9a98)`.

## Evidence
- `OptionsTail_Read` calls this wrapper after sound settings changed and passes `1`.
- `0x004cddf0` loads `ECX = 0x00896988` and calls `CSoundManager__ReinitializeAfterDeviceLoss`.
- `0x004cddfa` reads `[ESP + 0x4]`; `0x004cddfe` tests the low byte.
- `0x004cde14` calls `CMusic__PlaySelection`; `0x004cde1f` tail-jumps to `CGame__PlayMusicForCurrentLevel`.
- Nearby raw config-change thunks at `0x004cf0a9`, `0x004cf139`, `0x004cf1a9`, and `0x004cf259` show the same sound-reset/music-restore pattern, but their function boundaries remain deferred.

## Limits
Static retail-binary evidence only. Runtime audio behavior, exact source identity, raw thunk boundaries, and rebuild parity remain unproven.
