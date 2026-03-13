# CDXEngine__PostRender

> Address: `0x0053ecc0` | Source: `references/Onslaught/DXEngine.cpp:1279`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`int CDXEngine__PostRender(void *this, void *viewport)`)
- **Verified vs Source:** High confidence (`ENGINE.PostRender(&fullscreen)` callsite parity from `CGame__Render`)

## Purpose
Post-render overlay/UI stage:
- renders HUD/shared HUD
- renders message logs/briefing/pause overlays
- applies post-pass render-state cleanup
- performs end-of-frame UI/debug/front-end checks

## Notes
- Called once per rendered frame after per-view `CDXEngine__Render` calls.
- Closely matches the DXEngine post-render responsibilities in Stuart source.
