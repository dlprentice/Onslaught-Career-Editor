# CFrontEnd__DrawPanel

- Address: 0x00467010
- Status: Renamed (headless batch, read-back verified)
- Source match: references/Onslaught/frontEnd.cpp:749 (void CFrontEnd::DrawPanel(float tlx, float tly, float brx, float bry, float z, DWORD col))

## Purpose

Draws a clamped blank-panel sprite over a rectangle.

## Notes

Function toggles texture clamp/wrap render states around the draw call.
