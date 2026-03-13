# Camera.cpp Functions

> Source File: Camera.cpp | Binary: BEA.exe
> Debug Path: 0x00623c90 (`C:\\dev\\ONSLAUGHT2\\Camera.cpp`)

## Overview

Camera implementations that use `CBSpline` control points and `CActiveReader` (monitor.h deletion-event system) to safely track a `CThing*`.

## Functions

> Note: these were previously documented as generic `CCamera__*` routines. Decompile + Stuart source confirm they are `CThing3rdPersonCamera` (and related cameras).

Renames/signatures for `0x00418ef0`, `0x00419140`, `0x00419120`, `0x004198d0`, `0x00419a60`, `0x00419a40`, `0x00419b00`, `0x0041a210`, `0x0041a390`, `0x0041a370`, `0x0041a200`, and `0x0041ad30` were successfully applied and read-back verified on 2026-02-11.

| Address | Current Ghidra Name | Correct Mapping (Internal Source) | Notes |
|---------|----------------------|-----------------------------------|-------|
| 0x00418ef0 | `CThing3rdPersonCamera__ctor` | `CThing3rdPersonCamera::CThing3rdPersonCamera(CThing* for_thing)` | Builds 3 control points using `for_thing->GetRadius()` (vcall +0x40), then `CBSpline(points)`. Registers the reader cell at `this+0x04` in `for_thing+0x04` (monitor.h deletion list). |
| 0x00419140 | `CThing3rdPersonCamera__dtor` | `CThing3rdPersonCamera::~CThing3rdPersonCamera()` | Deletes `mCurve` and unregisters the reader cell from the monitored thing’s deletion list. |
| 0x00419120 | `CThing3rdPersonCamera__scalar_deleting_dtor` | MSVC scalar deleting dtor for `CThing3rdPersonCamera` | Calls `0x00419140`, then `OID__FreeObject` if needed. |
| 0x004198d0 | `CPanCamera__ctor` | `CPanCamera::CPanCamera(CThing* for_thing, CBSpline* curve, float length)` | Stores `for_thing` in an embedded reader cell (`this+0x0C`) and registers that cell in `for_thing+0x04`. Called from `CPlayer::GotoPanView()` and script pan-camera creation. |
| 0x00419a60 | `CPanCamera__dtor` | `CPanCamera::~CPanCamera()` | Releases owned curve object (if present), unregisters embedded ActiveReader cell, then performs base monitor shutdown cleanup. |
| 0x00419a40 | `CPanCamera__scalar_deleting_dtor` | MSVC scalar deleting dtor for `CPanCamera` | Calls `0x00419a60`, then `OID__FreeObject` when delete flag bit is set. |
| 0x00419b00 | `CPanCamera__Update` | `CPanCamera::Update()` | Implements the time-based spline pan update and schedules the next-frame `UPDATE_CAMERA` event (`2000`) via the event system. |
| 0x0041a210 | `CMovieCamera__ctor` | `CMovieCamera::CMovieCamera(CThing* for_thing)` | Initializes `mForThing` ActiveReader (monitor deletion-list registration) and cached pos/orientation/zoom/time fields (`-2.0` sentinels, identity/default values). |
| 0x0041a390 | `CMovieCamera__dtor` | compiler-generated dtor body for `CMovieCamera` | Unregisters `mForThing` ActiveReader cell from monitored thing deletion list and restores base vtable. |
| 0x0041a370 | `CMovieCamera__scalar_deleting_dtor` | MSVC scalar deleting dtor for `CMovieCamera` | Calls `0x0041a390`, then `OID__FreeObject` when delete flag bit is set. |
| 0x0041a200 | `CMovieCamera__GetShowHUD` | `CMovieCamera::GetShowHUD()` | Returns `false` (HUD hidden for this camera mode). |
| 0x0041ad30 | `CInterpolatedCamera__ctor` | `CInterpolatedCamera::CInterpolatedCamera(CCamera* cam)` | Source parity with `Camera.cpp`: calls `PrepareForInterpolation`, lerps pos/orientation/zoom from old/current camera state via frame render fraction, normalizes orientation, returns `this`. |
| 0x0041a3f0 | `CMovieCamera__GetPos` | `CMovieCamera::GetPos()` | Function object recovered manually (CodeBrowser `F`) on 2026-02-12; returns current/cached movie-camera position into hidden struct-return buffer. |
| 0x0041a530 | `CMovieCamera__GetOrientation` | `CMovieCamera::GetOrientation()` | Function object recovered manually on 2026-02-12; returns current/cached orientation matrix into hidden struct-return buffer. |
| 0x0041a710 | `CMovieCamera__GetOldPos` | `CMovieCamera::GetOldPos()` | Function object recovered manually on 2026-02-12; returns cached old position from `this+0x88`. |
| 0x0041a6f0 | `CMovieCamera__GetOldOrientation` | `CMovieCamera::GetOldOrientation()` | Function object recovered manually on 2026-02-12; returns cached old orientation matrix from `this+0x58`. |
| 0x0041a630 | `CMovieCamera__GetZoom` | `CMovieCamera::GetZoom()` | Function object recovered manually on 2026-02-12; computes/returns current zoom (float) with per-frame cache against event-manager time. |
| 0x0041a6e0 | `CMovieCamera__GetOldZoom` | `CMovieCamera::GetOldZoom()` | Function object recovered manually on 2026-02-12; returns cached previous zoom (float) from `this+0x98`. |
| 0x0041b070 | `CCamera__GetAspectRatio` | `CCamera::GetAspectRatio()` | Function object recovered manually on 2026-02-12; returns aspect ratio constant (0.5/0.75) based on runtime mode check. |
| 0x00466140 | `CGenericCamera__GetPos` | `CGenericCamera::GetPos()` | Function object recovered manually on 2026-02-24; RTTI/COL for adjacent vtable resolves to `.?AVCGenericCamera@@`; body copies 16 bytes from `this+0x34` into an output buffer (struct-return style vector accessor). |
| 0x00466170 | `CGenericCamera__scalar_deleting_dtor` | MSVC scalar deleting dtor for `CGenericCamera` | Wrapper calls `CGenericCamera__dtor` then conditionally `OID__FreeObject(this)` when delete flag bit is set. |
| 0x004661b0 | `CGenericCamera__dtor` | `CGenericCamera::~CGenericCamera()` (retail body) | Tiny dtor body resets vtable to `0x005d9260` (`.?AVCGenericCamera@@`) and returns. |
| 0x00419d40 | `CPanCamera__GetPos` | `CPanCamera::GetPos()` | Function object recovered manually (CodeBrowser `F`) on 2026-02-12; body copies 16 bytes from `this+0x1C` (mPos) into the hidden struct-return buffer (`FVector` by value). |
| 0x00419d70 | `CPanCamera__GetOrientation` | `CPanCamera::GetOrientation()` | Function object recovered manually on 2026-02-12; body copies 0x30 bytes from `this+0x3C` (mOrientation) into the hidden struct-return buffer (`FMatrix` by value). |
| 0x00419d90 | `CPanCamera__GetOldPos` | `CPanCamera::GetOldPos()` | Function object recovered manually on 2026-02-12; body copies 16 bytes from `this+0x2C` (mOldPos) into the hidden struct-return buffer. |
| 0x00419dc0 | `CPanCamera__GetOldOrientation` | `CPanCamera::GetOldOrientation()` | Function object recovered manually on 2026-02-12; body copies 0x30 bytes from `this+0x6C` (mOldOrientation) into the hidden struct-return buffer. |
| 0x00419de0 | `CPanCamera__HandleEvent` | `CPanCamera::HandleEvent(CEvent* event)` | Function object recovered manually on 2026-02-12; current body compares event num to `0x07D0` (`UPDATE_CAMERA`) and calls `Update()` on match. |

`functions_create` previously failed for `0x00419d40..0x00419de0` and `0x0041a3f0..0x0041b070` on 2026-02-11 (`Operation failed`). Both subsets were recovered on 2026-02-12 via manual CodeBrowser create (`F`) + MCP rename/signature read-back verification.

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d15cb | Unwind@005d15cb | 158 | Cleanup for type 0x28 allocation |
| 0x005d15e4 | Unwind@005d15e4 | 169 | Cleanup for BSpline allocation |

## Key Observations

- `0x00418ef0` implements the internal source constructor `CThing3rdPersonCamera::CThing3rdPersonCamera(CThing* for_thing)` (see `references/Onslaught/Camera.cpp`).
- The monitor.h deletion-event system is used via an embedded reader cell at `this+0x04` (CActiveReader/CGenericActiveReader semantics): when the monitored thing dies it nulls the cell to prevent dangling pointers.
- `CBSpline` is constructed with **degree/order 3** (cubic) for smooth movement.

## Constructor Allocations

| Line | Size | Type ID | Purpose |
|------|------|---------|---------|
| 158 | 16 bytes | 0x28 | Unknown component |
| 164 | 16 bytes | 0x26 | Vector3 #1 |
| 165 | 16 bytes | 0x26 | Vector3 #2 |
| 166 | 16 bytes | 0x26 | Vector3 #3 |
| 169 | 20 bytes | 0x26 | BSpline object |

## View Position Calculations

`CThing3rdPersonCamera::CThing3rdPersonCamera` sets up 3 camera control points based on entity radius:

| Vector | X | Y | Z Formula |
|--------|---|---|-----------|
| #1 | 0 | 22.5f | (-height - 3.8f) * 2.5f |
| #2 | 0 | -22.5f | (-height - 1.0f) * 2.5f |
| #3 | 0 | 2.5f | 4.5f (`1.8f * 2.5f`) |

## Related Files

- `references/Onslaught/Camera.h`
- `references/Onslaught/Camera.cpp`
- BSpline.cpp - Spline system for camera movement
- SPtrSet.cpp - Pointer set for camera positions

---
*Updated Feb 2026 with decompile-verified mappings + monitor.h deletion-event semantics.*
