# CFrontEnd__DrawBox

- Address: 0x00466e70
- Status: Wave467 signature/comment hardened (headless apply/read-back/probe verified)
- Signature: `void __thiscall CFrontEnd__DrawBox(void * this, float tlx, float tly, float brx, float bry, uint argb, float width, float depth)`
- Source match: `references/Onslaught/FrontEnd.cpp:737` (`void CFrontEnd::DrawBox(float tlx, float tly, float brx, float bry, DWORD col, float width, float depth)`)

## Purpose

Draws a box by issuing four edge lines.

## Notes

Retail stack cleanup matches the source argument shape, but the optimized body inlines the line-sprite draws instead of calling `CFrontEnd__DrawLine`. Runtime visual behavior remains unproven.
