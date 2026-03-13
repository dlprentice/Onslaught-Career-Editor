# CFrontEnd__GetShadowOffsetY

- Address: 0x00468750
- Status: Renamed (headless batch, read-back verified)
- Source match: references/Onslaught/frontEnd.cpp:1565 (float CFrontEnd::GetShadowOffsetY())

## Purpose

Computes animated Y shadow offset from frontend counter.

## Notes

Matches source cosine formula with SHADOW_PERIOD and SHADOW_RADIUS_Y.
