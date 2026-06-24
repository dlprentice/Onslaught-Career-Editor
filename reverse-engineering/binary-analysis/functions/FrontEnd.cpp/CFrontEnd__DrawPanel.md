# CFrontEnd__DrawPanel

- Address: 0x00467010
- Status: Wave467 signature/comment hardened (headless apply/read-back/probe verified)
- Signature: `void __thiscall CFrontEnd__DrawPanel(void * this, float tlx, float tly, float brx, float bry, float depth, uint argb)`
- Source match: `references/Onslaught/FrontEnd.cpp:749` (`void CFrontEnd::DrawPanel(float tlx, float tly, float brx, float bry, float z, DWORD col)`)

## Purpose

Draws a clamped blank-panel sprite over a rectangle.

## Notes

Function toggles texture clamp/wrap render states around the draw call. Runtime visual behavior and exact texture identity remain unproven.
