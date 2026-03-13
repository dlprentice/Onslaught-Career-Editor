# CFrontEnd__DrawBox

- Address: 0x00466e70
- Status: Renamed (headless batch, read-back verified)
- Source match: references/Onslaught/frontEnd.cpp:737 (void CFrontEnd::DrawBox(float tlx, float tly, float brx, float bry, DWORD col, float width, float depth))

## Purpose

Draws a box by issuing four edge lines.

## Notes

Retail call sequence matches source DrawLine chaining.
