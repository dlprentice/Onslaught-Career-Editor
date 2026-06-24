# CFrontEnd__RenderStart

- Address: 0x004685f0
- Status: Wave467 renamed/signature/comment hardened (headless apply/read-back/probe verified)
- Previous label: `CFrontEnd__VFunc_06_004685f0`
- Signature: `int __thiscall CFrontEnd__RenderStart(void * this)`
- Source match: `references/Onslaught/FrontEnd.cpp` (`BOOL CFrontEnd::RenderStart()`)

## Purpose

Begins the frontend scene, configures projection/view/world render state, binds the frontend camera, applies render state, and returns begin-scene success.

## Notes

The function is reached from `CDXFrontEnd__VFunc_06_00540f70`, matching source `CDXFrontEnd::RenderStart()` forwarding into `CFrontEnd::RenderStart()`. Exact vtable layout beyond this slot, runtime rendering behavior, and rebuild parity remain unproven.
