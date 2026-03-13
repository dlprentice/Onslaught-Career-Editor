# CFrontEnd__DrawBarGraph

- Address: 0x004670b0
- Status: Renamed (headless batch, read-back verified)
- Source match: references/Onslaught/frontEnd.cpp:763 (void CFrontEnd::DrawBarGraph(float tlx, float tly, float brx, float bry, float num, float max, float z, SINT bordercol, SINT backcol, SINT forecol))

## Purpose

Draws background panel plus proportional foreground fill panel.

## Notes

Retail branch draws the foreground only when the bar value is non-zero.
