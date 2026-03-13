# CEngine__UpdatePos

> Address: `0x0044a1c0` | Source: `references/Onslaught/engine.cpp:386`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void CEngine__UpdatePos(void *this, void *cam)`)
- **Verified vs Source:** Yes (high-confidence structural match to `CEngine::UpdatePos(CCamera*)`)

## Purpose
Updates landscape tile/state position for the current viewpoint camera.

## Behavior Summary
- Checks the render-landscape flag (`this+0x4A8`).
- If enabled, forwards camera/tile context to `CDXLandscape__SetTileData(...)`.
- No-op when landscape rendering is disabled.

## Callers
- `CGame__MainLoop` (`0x0046eee0`) in the per-player/viewpoint update loop.
