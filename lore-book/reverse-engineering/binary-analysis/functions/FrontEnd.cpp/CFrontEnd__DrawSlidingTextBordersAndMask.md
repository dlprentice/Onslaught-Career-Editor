# CFrontEnd__DrawSlidingTextBordersAndMask

- Address: 0x00467200
- Status: Renamed (headless batch, read-back verified)
- Source match: references/Onslaught/frontEnd.cpp:807 (void CFrontEnd::DrawSlidingTextBordersAndMask(float transition, EFrontEndPage dest))

## Purpose

Renders animated bracket and mask layers used during frontend transitions.

## Notes

High-fanout transition logic with per-page cases, alpha/scale shaping, and mask pass.
