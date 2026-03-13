# CFrontEnd__DrawBar

- Address: 0x00467ae0
- Status: Renamed (headless batch, read-back verified)
- Source match: references/Onslaught/frontEnd.cpp:1073 (void CFrontEnd::DrawBar(float sx, float sy, float z, SINT segs, DWORD col, float scale))

## Purpose

Draws segmented title/header bars with left, center, and right textures.

## Notes

Retail loop selects endcaps and repeats center segment by seg count.
