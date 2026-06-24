# CFrontEnd__GetShadowOffsetX

- Address: 0x00468730
- Status: Wave467 signature/comment hardened (headless apply/read-back/probe verified)
- Signature: `float __thiscall CFrontEnd__GetShadowOffsetX(void * this)`
- Source match: `references/Onslaught/FrontEnd.cpp:1559` (`float CFrontEnd::GetShadowOffsetX()`)

## Purpose

Computes animated X shadow offset from frontend counter.

## Notes

Matches source sine formula with SHADOW_PERIOD and SHADOW_RADIUS_X.
