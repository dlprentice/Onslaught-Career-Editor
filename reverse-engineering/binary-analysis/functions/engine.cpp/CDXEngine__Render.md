# CDXEngine__Render

> Address: `0x0053e2e0` | Source: `references/Onslaught/DXEngine.cpp:637`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`int CDXEngine__Render(void *this, unsigned int viewpoint)`)
- **Verified vs Source:** High confidence (`ENGINE.Render(i)` callsite parity from `CGame__Render`)

## Purpose
Per-view render stage for the DX engine:
- selects active viewpoint/camera
- computes view/gamut/LOD
- renders landscape/world/water/particles/atmospherics
- applies per-view render-state transitions and cleanup

## Notes
- Called 1-4 times per frame (depending on split-screen player count).
- This is the heavy world-render pass between pre/post render stages.
