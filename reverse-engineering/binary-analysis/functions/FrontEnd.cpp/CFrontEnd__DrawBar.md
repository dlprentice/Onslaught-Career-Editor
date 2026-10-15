# CFrontEnd__DrawBar

- Address: 0x00467ae0
- Status: Wave467 signature/comment hardened (headless apply/read-back/probe verified)
- Signature: `void __thiscall CFrontEnd__DrawBar(void * this, float sx, float sy, float depth, int segment_count, uint argb, float scale)`
- Source match: `references/Onslaught/FrontEnd.cpp:1073` (`void CFrontEnd::DrawBar(float sx, float sy, float z, SINT segs, DWORD col, float scale)`)

## Purpose

Draws segmented title/header bars with left, center, and right textures.

## Notes

Retail loop selects endcaps and repeats the center segment for `segment_count + 2` total sprites. Runtime visual behavior and exact texture identity remain unproven.
