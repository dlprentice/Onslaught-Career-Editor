# CFrontEnd__GetClickStateInRect

- Address: 0x00469400
- Status: Renamed (headless batch, Wave 377 read-back verified)
- Current saved signature: `uint __cdecl CFrontEnd__GetClickStateInRect(float left, float top, float right, float bottom)`

## Purpose

Gates frontend modal mouse input and queries click state for a rectangle.

## Notes

Wave 377 hardened the saved signature/comment/tag. Static decompile/xref evidence shows the four-float rectangle wrapper around the click-state query path.

Wave567 refined the lower-level callee as `Input__GetClickStateInRect(float left, float top, float right, float bottom)`. Treat the four floats as left/top/right/bottom bounds, not x/y/width/height.

This is static evidence only. Runtime mouse behavior remains unproven by this page.
