# CDXEngine__PreRender

> Address: `0x0053e220` | Source: `references/Onslaught/DXEngine.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`int CDXEngine__PreRender(void *this, void *viewport)`)
- **Verified vs Source:** High confidence (`ENGINE.PreRender(&fullscreen)` callsite from `CGame__Render`)

## Purpose
Per-frame pre-render setup for the DX engine path:
- initializes render/frame state before per-view rendering
- applies viewport-driven setup
- prepares counters/state used by `CDXEngine__Render` and `CDXEngine__PostRender`

## Notes
- Called from `CGame__Render` before split-screen viewpoint loops.
- Corresponds to the source-level `CDXEngine::PreRender(CViewport*)` stage.
