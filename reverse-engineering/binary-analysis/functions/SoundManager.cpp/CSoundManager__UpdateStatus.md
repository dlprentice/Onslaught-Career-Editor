# CSoundManager__UpdateStatus

> Address: `0x004e1b20` | Source: `references/Onslaught/SoundManager.cpp:1220`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void CSoundManager__UpdateStatus(void *this)`)
- **Verified vs Source:** Yes (high-confidence structural match to `CSoundManager::UpdateStatus()`)

## Purpose
Per-frame sound update pass for active sound events.

## Behavior Summary
- Pulls camera pose/orientation from `GAME.GetCamera(0)` into sound-manager state.
- Sorts/updates global sound settings (`SortEventList`, `SOUND.UpdateGlobals` path).
- Computes frame delta via `PLATFORM__GetSysTimeFloat`.
- Iterates active sound events:
  - advances event time when not paused,
  - updates 3D positioning/attenuation when not frozen,
  - applies fade and pitch interpolation,
  - manages debug markers when `snd_visible` is enabled,
  - releases/clears stale owner-reader links for inactive events.

## Callers
- `CGame__MainLoop` (`0x0046eee0`)
