# CFrontEnd__DrawBarGraph

- Address: 0x004670b0
- Status: Wave467 signature/comment hardened (headless apply/read-back/probe verified)
- Signature: `void __thiscall CFrontEnd__DrawBarGraph(void * this, float tlx, float tly, float brx, float bry, float num, float max, float depth, uint border_argb, uint back_argb, uint fore_argb)`
- Source match: `references/Onslaught/FrontEnd.cpp:763` (`void CFrontEnd::DrawBarGraph(float tlx, float tly, float brx, float bry, float num, float max, float z, SINT bordercol, SINT backcol, SINT forecol)`)

## Purpose

Draws background panel plus proportional foreground fill panel.

## Notes

Retail branch draws the foreground only when the bar value is non-zero. The source `bordercol` parameter is preserved in the signature, but exact retail color use and runtime visual behavior remain unproven.
