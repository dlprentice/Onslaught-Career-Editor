# CFrontEnd__Render

- **Address:** `0x00468200`
- **Status:** Renamed / signature + comment applied in Ghidra
- **Source match:** `references/Onslaught/FrontEnd.cpp` (`BOOL CFrontEnd::Render()` path)

## Purpose

Frontend render pass used by `CFrontEnd__Run` in `while (!Render())` loops.

## Key Behavior

1. Begins frontend render pass / scene setup.
2. Renders active or transitioning frontend pages (`RenderPreCommon` / `Render` style calls).
3. Draws overlays/cursors/dev visuals based on state/flags.
4. Ends render pass and returns non-zero on success.

## Call Relationship

- Called from `CFrontEnd__Run` (`0x004684d0`) in the transition wait loop.
- Works alongside `CFrontEnd__Process` (`0x00466ba0`) to form the frontend frame loop.
