# CGame__MainLoop

> Address: `0x0046eee0` | Source: `references/Onslaught/game.cpp:2076`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void CGame__MainLoop(void *this)`)
- **Verified vs Source:** Yes (high-confidence structural match to `CGame::MainLoop`)

## Purpose
Per-frame gameplay loop:
- processes platform quit/input state
- runs gameplay update and audio status updates
- performs render pass and frame timing maintenance
- updates frame-fraction/base-time bookkeeping

## Notes
- Called from `CGame__RestartLoopRunLevel` (`0x0046dc30`) while `mQuit == QT_NONE`.
- Entry call chain now resolves to named helpers:
  - `CProfiler__ResetAll` (`0x00523db0`)
  - `PLATFORM__Process` (`0x00515880`)
  - `CController__InactivityMeansQuitGame` (`0x0042d810`)
- Audio/status tail now resolves to:
  - `CSoundManager__UpdateStatus` (`0x004e1b20`)
  - `CMusic__Update` (`0x004e2ea0`)
- Viewpoint maintenance loop now resolves to `CEngine__UpdatePos` (`0x0044a1c0`) per active camera slot.
- Calls `CGame__Update` (`0x0046e910`) before render/audio frame completion.
- Contains the runtime branch that can force quit-state transitions based on platform/process results.
- `Platform__AsyncSaveCareer` call path references this function in the current mapping set.
