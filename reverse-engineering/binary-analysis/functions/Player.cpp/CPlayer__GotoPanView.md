# CPlayer__GotoPanView

> Address: `0x004d2c10`
>
> Source: `references/Onslaught/Player.cpp` (`CPlayer::GotoPanView(float for_time)`)

## Status
- **Named in Ghidra:** Yes (`CPlayer__GotoPanView`)
- **Verified vs Source:** Yes (matches `CPlayer::GotoPanView`)
- **MCP action needed:** None for this symbol (rename/prototype already applied and read-back verified)

## Purpose
Transitions the player into **pan view** for a short duration by:
- building a 3- or 4-point `CBSpline` of camera offsets relative to the Battle Engine orientation
- constructing a `CPanCamera` targeting the player’s `mBattleEngine`
- setting it as the current camera
- scheduling a `GOTO_CONTROL_VIEW` event (source: `EPlayerEvent` base `4000`) to return to control view after `for_time`

## Key Observations (Steam BEA.exe)
- Early-out if `mBattleEngine` is NULL (`*(this+0x1C) == 0`).
- Copies 12 floats from `mBattleEngine + 0x3C` into locals (matches grabbing the Battle Engine orientation matrix).
- Allocates an `SPtrSet<FVector>` (0x10 bytes) and appends heap `FVector` points (0x10 bytes each) built from the orientation matrix:
  - If `DAT_008a9d38` (current level num) is in `{0xDD, 0xDE, 0xE7, 0xE8, 0x14B, 0x14C, 0x20B, 0x20C}` (decimal `{221, 222, 231, 232, 331, 332, 523, 524}` per Stuart source):
    - half-pan start: `ori * FVector(5.0, 0.0, 0.0)`
  - Else:
    - full-pan start: `ori * FVector(0.0, 10.0, -4.3)`
    - next: `ori * FVector(5.0, 0.0, 1.3)`
  - Always appends:
    - `ori * FVector(0.0, -9.0, -1.3)`
    - `ori * FVector(0.0, -2.5, 0.0)`
- Allocates `CBSpline` (0x14 bytes) and constructs it with the points list (observed call form: `CBSpline__ctor(points, 3)`; the `3` matches spline order in our current RE notes).
- Allocates `CPanCamera` (0x9C bytes) and constructs it with `(mBattleEngine, spline, for_time)` (calls `CPanCamera__ctor` at `0x004198d0`).
- Calls `FUN_004705e0(*(this+0x2C)-1, camera, 1)` (engine path for “set current camera”).
- Schedules player event `4000` (matches `GOTO_CONTROL_VIEW`) at `max(for_time - 0.05, 0)` via `FUN_0044b2d0(&time, 4000, this, 0, 0, 0)`.

## Notes
- Stuart source has a level-number conditional that chooses **half-pan** vs full pan (3 vs 4 spline points). The Steam build decompile shows the same overall shape; confirm the specific level-ID comparisons when we finish naming the `GAME.GetCurrentlyRunningLevelNum()` helper.
- This function is currently incorrectly documented as “ApplyForce” in older RE notes; those docs have been corrected to reflect the pan-camera behavior.

## Related
- `reverse-engineering/binary-analysis/functions/Camera.cpp/_index.md` (CPanCamera mappings)
- `reverse-engineering/binary-analysis/functions/monitor.h/_index.md` (CPanCamera is `CCamera, CMonitor` and participates in ActiveReader deletion lists)
