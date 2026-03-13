# CFrontEnd__DrawLine

- Address: 0x00466de0
- Status: Renamed (headless batch, read-back verified)
- Source match: references/Onslaught/frontEnd.cpp:717 (void CFrontEnd::DrawLine(float sx, float sy, float ex, float ey, DWORD col, float width, float depth, float perc))

## Purpose

Draws a line as a rotated and scaled link sprite between endpoints.

## Notes

Matches source behavior: midpoint + atan2 + length-based scale.
