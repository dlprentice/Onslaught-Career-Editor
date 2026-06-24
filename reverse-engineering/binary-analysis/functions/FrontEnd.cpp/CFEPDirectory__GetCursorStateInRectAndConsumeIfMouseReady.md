# CFEPDirectory__GetCursorStateInRectAndConsumeIfMouseReady

- Address: 0x00469430
- Status: Renamed (headless batch, Wave 377 read-back verified)
- Current saved signature: `uint __cdecl CFEPDirectory__GetCursorStateInRectAndConsumeIfMouseReady(float left, float top, float right, float bottom)`

## Purpose

Directory-page mouse wrapper that queries and consumes cursor-state input for a rectangle when the frontend mouse-ready gate allows it.

## Notes

Wave 377 corrected the older `CFEPDirectory__CheckMouseInputReady` wording. Static decompile/xref evidence shows the helper gating through `CFrontEnd__IsMouseInputReady` and otherwise calling the cursor-state consume path with four float rectangle arguments.

Wave567 refined the lower-level callee as `Input__GetCursorStateInRectAndConsume(float left, float top, float right, float bottom)`. Treat the four floats as left/top/right/bottom bounds, not x/y/width/height.

This is static evidence only. Runtime directory-page mouse behavior remains unproven by this page.
