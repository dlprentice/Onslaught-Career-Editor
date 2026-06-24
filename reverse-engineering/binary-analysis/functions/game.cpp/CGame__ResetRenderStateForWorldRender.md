# CGame__ResetRenderStateForWorldRender

- **Address:** `0x004eb1e0`
- **Source context:** `references/Onslaught/game.cpp` (behavior-level alignment pass)

## Summary

Reinitializes D3D render-state cache and sampler defaults before world rendering passes.

## Notes

- Recovered and semantically renamed via headless decompile + batch-rename workflow (2026-02-25).
- Signature is still decompiler-derived; parameter naming remains provisional pending deeper callsite pass.
