# game.cpp Functions

> Source File: game.cpp | Binary: BEA.exe

## Overview

Core game initialization and lifecycle management. This file handles setting up all game subsystems during startup.

## Functions

### Console Commands (Free Functions)

| Address | Name | Purpose |
|---------|------|---------|
| 0x0046be10 | [con_map](./con_map.md) | Console command: `Map <n>` |
| 0x0046be80 | [con_resetmemsizes](./con_resetmemsizes.md) | Console command: `ResetMemSizes` |
| 0x0046bea0 | [con_dumptextures](./con_dumptextures.md) | Console command: `DumpTextures` |
| 0x0046bed0 | [con_dumptimerecords](./con_dumptimerecords.md) | Console command: `dumptimerecords` (disabled in this build) |
| 0x0046bef0 | [con_remotecameraon](./con_remotecameraon.md) | Console command: `RemoteCameraOn` |
| 0x0046c0b0 | [con_remotecameraoff](./con_remotecameraoff.md) | Console command: `RemoteCameraOff` |
| 0x0046c120 | [con_navmapon](./con_navmapon.md) | Console command: `NavMapOn` |
| 0x0046c150 | [con_navmapoff](./con_navmapoff.md) | Console command: `NavMapOff` |
| 0x0046c180 | [con_win](./con_win.md) | Console command: `Win` |
| 0x0046c200 | [con_lose](./con_lose.md) | Console command: `Lose` |

### Cutscene Helpers (Free Functions)

| Address | Name | Purpose |
|---------|------|---------|
| 0x00523120 | [lookup_FMV](./lookup_FMV.md) | Returns intro/outro FMV id from level->FMV lookup table (`index_type`: 0/1/2, `-1` when absent) |
| 0x0046d810 | [Cutscene_FormatPath_WithSmallFallback](./Cutscene_FormatPath_WithSmallFallback.md) | Builds `cutscenes\\%02d` and rewrites to `_small` variant when `data\\video\\<name>.vid` is missing |

### Restart-Loop Local Helpers

| Address | Name | Purpose |
|---------|------|---------|
| 0x0046dbd0 | [CWaitForStart__ctor](./CWaitForStart__ctor.md) | Initializes temporary wait-sink object used during restart-loop flow (`vtable@+0x00`, zero field at `+0x04`) |

### CGame Methods

| Address | Name | Purpose |
|---------|------|---------|
| 0x0046c360 | [CGame__Init](./CGame__Init.md) | Core game startup init (engine/imposters/render queue/static shadows/interface/HUD) |
| 0x0046c430 | [CGame__InitRestartLoop](./CGame__InitRestartLoop.md) | Per-level/restart runtime init (state reset, event manager, UI/runtime allocations, command/CVar registration) |
| 0x0046ca70 | [CGame__ShutdownRestartLoop](./CGame__ShutdownRestartLoop.md) | Per-level/restart teardown (runtime frees, script/event cleanup, subsystem reset) |
| 0x0046cd30 | [CGame__LoadResources](./CGame__LoadResources.md) | Loads level resources (resource bundle, texture/mesh resources, particle set) |
| 0x0046cdf0 | [CGame__LoadLevel](./CGame__LoadLevel.md) | Loads world/level data and creates per-player runtime objects |
| 0x0046d040 | [CGame__PostLoadProcess](./CGame__PostLoadProcess.md) | Post-load world/player setup and readiness checks |
| 0x0046d470 | [CGame__FillOutEndLevelData](./CGame__FillOutEndLevelData.md) | Captures end-of-level summary/progression snapshot data |
| 0x0046d890 | [CGame__RunIntroFMV](./CGame__RunIntroFMV.md) | Intro cutscene flow (lookup, path fallback, unlock goodie, play FMV) |
| 0x0046d9f0 | [CGame__RunOutroFMV](./CGame__RunOutroFMV.md) | Outro cutscene flow with conditional variants and end-level credits trigger |
| 0x004726b0 | [CGame__RollCredits](./CGame__RollCredits.md) | End-credits loop (temporary control handlers + credits renderer until completion/skip) |
| 0x0046dc00 | [CGame__PlayMusicForCurrentLevel](./CGame__PlayMusicForCurrentLevel.md) | Level music selector (tutorial track for level 100, otherwise in-game track) |
| 0x0046dc30 | [CGame__RestartLoopRunLevel](./CGame__RestartLoopRunLevel.md) | Per-restart pass inside a level (load/process/prerun/main-loop/cleanup) |
| 0x0046e240 | [CGame__RunLevel](./CGame__RunLevel.md) | Top-level level driver (init, restart-loop orchestration, shutdown/quit return) |
| 0x0046e460 | [CGame__Render](./CGame__Render.md) | Main render path (viewport setup, split-screen cameras, post-render pass) |
| 0x0046e910 | [CGame__Update](./CGame__Update.md) | Core gameplay tick/update path (event manager/controller/game-state/fade handling) |
| 0x0046eee0 | [CGame__MainLoop](./CGame__MainLoop.md) | Per-frame game loop (process, update, render, timing/fraction management) |
| 0x0046f2c0 | [CGame__GetCamera](./CGame__GetCamera.md) | Returns `mCurrentCamera[number]` |
| 0x0046f2d0 | [CGame__SetCamera](./CGame__SetCamera.md) | Thin wrapper around `CGame__SetCurrentCamera(number, cam, false)` |
| 0x0046f2f0 | [CGame__DeclareLevelWon](./CGame__DeclareLevelWon.md) | Level-won transition path |
| 0x0046f360 | [CGame__MPDeclarePlayerWon](./CGame__MPDeclarePlayerWon.md) | Multiplayer winner declaration (player 1/2) |
| 0x0046f3e0 | [CGame__MPDeclareGameDrawn](./CGame__MPDeclareGameDrawn.md) | Multiplayer draw declaration |
| 0x0046f430 | [CGame__DeclareLevelLost](./CGame__DeclareLevelLost.md) | Level-lost transition path |
| 0x0046f550 | [CGame__DeclarePlayerDead](./CGame__DeclarePlayerDead.md) | Death handling + camera switch + respawn/loss routing |
| 0x0046f7e0 | [CGame__ReceiveButtonAction](./CGame__ReceiveButtonAction.md) | Debug button dispatcher (0..14); contains Aurore gate for free camera |
| 0x0046fae0 | [CGame__UnPause](./CGame__UnPause.md) | Clears pause state and deactivates pause menu path |
| 0x0046fb00 | [CGame__Pause](./CGame__Pause.md) | Pause entrypoint with optional pause-menu handoff |
| 0x0046fb80 | [CGame__ToggleDebugUnitForward](./CGame__ToggleDebugUnitForward.md) | Debug unit selection forward |
| 0x0046fc40 | [CGame__ToggleDebugUnitBackward](./CGame__ToggleDebugUnitBackward.md) | Debug unit selection backward |
| 0x0046fd40 | [CGame__ToggleDebugSquadBackward](./CGame__ToggleDebugSquadBackward.md) | Debug squad selection backward |
| 0x0046fe20 | [CGame__ToggleDebugSquadForward](./CGame__ToggleDebugSquadForward.md) | Debug squad selection forward |
| 0x0046fec0 | [CGame__StartPlayingState](./CGame__StartPlayingState.md) | Transitions game state to playing, posts script event |
| 0x0046ff10 | [CGame__HandleEvent](./CGame__HandleEvent.md) | Core event dispatcher for gameplay state/events |
| 0x00470120 | [CGame__RespawnPlayer](./CGame__RespawnPlayer.md) | Respawn flow and spawn-point selection |
| 0x00470430 | [CGame__ToggleFreeCameraOn](./CGame__ToggleFreeCameraOn.md) | Enable free camera for a player slot |
| 0x004705d0 | [CGame__GetController](./CGame__GetController.md) | Returns `mController[player]` |
| 0x004705e0 | [CGame__SetCurrentCamera](./CGame__SetCurrentCamera.md) | Assign active camera (current vs old depending on free-cam mode) |
| 0x0053ecc0 | `CDXEngine__PostRender` | Engine post-render overlay/state pass called from `CGame__Render` |

### CGame Helpers (2026-02-25 Semantic Tranche)

| Address | Name | Purpose |
|---------|------|---------|
| 0x004080f0 | [CGame__IsWalkerGroundedOrCollision](./CGame__IsWalkerGroundedOrCollision.md) | Checks walker-state plus ground/collision gate used by movement/camera logic |
| 0x00470650 | [CGame__RenderDebugMemoryAndSelectionInfo](./CGame__RenderDebugMemoryAndSelectionInfo.md) | Renders heap/memory pressure and selected squad/unit debug overlay text |
| 0x00472240 | [CGame__AppendToStatusBufferV](./CGame__AppendToStatusBufferV.md) | Appends formatted text into status/debug string buffer via `vsprintf` |
| 0x00472270 | [CGame__XorBlock64Words](./CGame__XorBlock64Words.md) | XOR helper over two 0x64-byte blocks (ushort lanes) into scratch globals |
| 0x00472670 | [CGame__CountActiveSlots_A](./CGame__CountActiveSlots_A.md) | Counts non-zero entries in first active-slot array (`+0x4c`) |
| 0x00472690 | [CGame__CountActiveSlots_B](./CGame__CountActiveSlots_B.md) | Counts non-zero entries in second active-slot array (`+0x9c`) |
| 0x004eaf20 | [CGame__SetupRespawnReaderAndEffect](./CGame__SetupRespawnReaderAndEffect.md) | Initializes respawn reader state and optional respawn particle effect |
| 0x004eb130 | [CGame__HasNearbyHostileWithinRadius](./CGame__HasNearbyHostileWithinRadius.md) | Returns whether a nearby hostile is present within query radius |
| 0x004eb1e0 | [CGame__ResetRenderStateForWorldRender](./CGame__ResetRenderStateForWorldRender.md) | Reinitializes D3D render-state defaults before world rendering |

## Key Observations

- Game initialization is a critical entry point for understanding how subsystems are configured
- Main-loop helper call chain is now partially named and source-aligned:
  - `CProfiler__ResetAll` (`0x00523db0`)
  - `PLATFORM__Process` (`0x00515880`)
  - `CController__InactivityMeansQuitGame` (`0x0042d810`)
  - `CSoundManager__UpdateStatus` (`0x004e1b20`)
- Cutscene helper alignment:
  - `lookup_FMV` (`0x00523120`) resolves intro/outro FMV ids from the level lookup table.
  - `Cutscene_FormatPath_WithSmallFallback` (`0x0046d810`) centralizes `%02d` vs `%02d_small` path fallback used by cutscene-award/playback paths.
  - `CGame__RunIntroFMV` (`0x0046d890`) and `CGame__RunOutroFMV` (`0x0046d9f0`) now carry source-aligned naming and signatures.
  - `CGame__RollCredits` (`0x004726b0`) drives the interactive credits sequence used by final-level outro routes.
- Restart-loop local helper alignment:
  - `CWaitForStart__ctor` (`0x0046dbd0`) initializes the temporary wait object consumed by restart-loop scheduling logic.
- Related to Career, Script, World, and other core systems

## Related Files

- Career.cpp - Career/save system
- World.cpp - Level loading
- Script.cpp - Scripting system

---
*Migrated from ghidra-analysis.md (Dec 2025)*
