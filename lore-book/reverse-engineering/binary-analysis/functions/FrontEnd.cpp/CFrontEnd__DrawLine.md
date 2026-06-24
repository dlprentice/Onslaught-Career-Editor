# CFrontEnd__DrawLine

- Address: 0x00466de0
- Status: Wave467 signature/comment hardened (headless apply/read-back/probe verified)
- Signature: `void __thiscall CFrontEnd__DrawLine(void * this, float sx, float sy, float ex, float ey, uint argb, float width, float depth, float percent)`
- Source match: `references/Onslaught/FrontEnd.cpp:717` (`void CFrontEnd::DrawLine(float sx, float sy, float ex, float ey, DWORD col, float width, float depth, float perc)`)

## Purpose

Draws a line as a rotated and scaled link sprite between endpoints.

## Notes

Retail stack cleanup matches the source argument shape. The body computes midpoint/angle/scale and draws the level-link surface. Runtime visual behavior and exact texture/render-state identity remain unproven.
