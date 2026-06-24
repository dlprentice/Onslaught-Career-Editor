# CGame__RestartLoopRunLevel

> Address: `0x0046dc30` | Source: `references/Onslaught/game.cpp:1260`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`int CGame__RestartLoopRunLevel(void *this, int aLevel)`)
- **Verified vs Source:** Yes (high-confidence structural match to restart-loop lifecycle in `CGame::RestartLoopRunLevel`)

## Purpose
Runs a single restart-loop pass for the current level:
- load level and post-load processing
- optional intro FMV / loading flow
- build level specifics + prerun setup
- run per-frame gameplay loop until `mQuit != QT_NONE`
- return per-pass quit result to `RunLevel`

## Notes
- This is the inner restart-loop function; top-level orchestration is `CGame__RunLevel` (`0x0046e240`).
- Calls `CGame__LoadLevel` then `CGame__PostLoadProcess` before entering prerun/main-loop flow.
- Includes the `GetIntroFMV` / `RunIntroFMV` branch and loading-range transitions seen in source.
- Calls into `CGame__MainLoop` for per-frame execution.
- Music selection is source-parity with `CGame__PlayMusicForCurrentLevel`
  (`0x0046dc00`) tutorial-vs-ingame selector logic, but the retail
  restart-loop path also directly performs this selector branch before entering
  the frame loop. A 2026-06-24 copied-runtime CDB diagnostic on level `100`
  observed `CMusic__PlaySelection` returning to `0x0046e0bf`, the instruction
  after the direct `CALL 0x004bb8c0` inside `CGame__RestartLoopRunLevel`. The
  same after-launch diagnostic did not observe the one-shot wrapper-entry
  breakpoint at `0x0046dc00`, so this is call-path provenance evidence, not
  audible-output proof.
- Initializes the local wait-sink helper via `CWaitForStart__ctor` (`0x0046dbd0`) during restart-loop setup.
- Executes `autoexec.con` through `CConsole__ExecScript` (`0x0042ad30`) as part of restart-loop preparation.
- Returns a per-pass quit code consumed by `CGame__RunLevel`, which then invokes `CGame__ShutdownRestartLoop`.
