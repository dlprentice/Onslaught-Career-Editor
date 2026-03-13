# CFrontEnd__DrawTitleBar

- Address: 0x00467bd0
- Status: Renamed (headless batch, read-back verified)
- Source match: references/Onslaught/frontEnd.cpp:1107 (void CFrontEnd::DrawTitleBar(WCHAR *text, float transition, EFrontEndPage dest))

## Purpose

Draws animated title bar, bracket sprites, and title text.

## Notes

Includes shadow-offset usage and page-dependent transition shaping.
