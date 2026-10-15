# CFrontEnd__UpdateCamera

- Address: 0x004685a0
- Status: Wave467 renamed/signature/comment hardened (headless apply/read-back/probe verified)
- Previous label: `CFrontEnd__SetRenderViewAndProjection`
- Signature: `void __thiscall CFrontEnd__UpdateCamera(void * this)`
- Source match: `references/Onslaught/FrontEnd.cpp` (`void CFrontEnd::UpdateCamera()`)

## Purpose

Fetches the frontend camera view matrix and installs view/projection state through the retail `CDXEngine` path.

## Notes

The source bridge is strong for behavior and role, but exact `FED`/`ENGINE` layout, camera state semantics, runtime visual behavior, and rebuild parity remain unproven.
