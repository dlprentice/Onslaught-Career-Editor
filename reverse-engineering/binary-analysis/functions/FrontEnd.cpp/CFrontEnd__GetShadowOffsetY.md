# CFrontEnd__GetShadowOffsetY

- Address: 0x00468750
- Status: Wave467 signature/comment hardened (headless apply/read-back/probe verified)
- Signature: `float __thiscall CFrontEnd__GetShadowOffsetY(void * this)`
- Source match: `references/Onslaught/FrontEnd.cpp:1565` (`float CFrontEnd::GetShadowOffsetY()`)

## Purpose

Computes animated Y shadow offset from frontend counter.

## Notes

Matches source cosine formula with SHADOW_PERIOD and SHADOW_RADIUS_Y.
