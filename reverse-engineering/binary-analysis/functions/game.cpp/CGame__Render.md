# CGame__Render

> Address: `0x0046e460` | Source: `references/Onslaught/game.cpp:1704`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void CGame__Render(void *this, int num_renders)`)
- **Verified vs Source:** Yes (high-confidence structural match to `CGame::Render`)

## Purpose
Primary render-frame entry:
- updates render timing/fraction
- configures fullscreen/split-screen viewports
- sets active cameras/viewpoints and renders player views
- executes post-render HUD/overlay/state pass

## Notes
- Player-count branches match source behavior (`1`, `2`, `3/4` view layouts).
- Viewpoint setup helpers mapped in the same call path:
  - `CEngine__SetNumViewpoints` (`0x00528b50`)
  - `CEngine__SetViewpoint` (`0x0044a020`)
  - `CInterpolatedCamera__ctor` (`0x0041ad30`) used by `CEngine__SetViewpoint`
- Window-dimension helpers now named:
  - `PLATFORM__GetWindowWidth` (`0x00515940`)
  - `PLATFORM__GetWindowHeight` (`0x00515b00`)
- Engine call chain is now mapped as:
  - `CDXEngine__PreRender` (`0x0053e220`)
  - `CDXEngine__Render` (`0x0053e2e0`)
  - `CDXEngine__PostRender` (`0x0053ecc0`)
