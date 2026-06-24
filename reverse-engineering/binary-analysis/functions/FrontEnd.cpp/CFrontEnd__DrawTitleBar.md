# CFrontEnd__DrawTitleBar

- Address: 0x00467bd0
- Status: Renamed (headless batch, read-back verified)
- Current saved signature: `void __stdcall CFrontEnd__DrawTitleBar(short * title_text, float transition, int dest_page)`
- Source match: references/Onslaught/frontEnd.cpp:1107 (void CFrontEnd::DrawTitleBar(WCHAR *text, float transition, EFrontEndPage dest))

## Purpose

Draws animated title bar, bracket sprites, and title text.

## Notes

Wave 377 hardened the saved Ghidra signature/comment/tag. The retail body renders title-bar sprites, measures wide title text, uses shadow-offset helpers, and dispatches dynamic font drawing with page-dependent transition shaping.

This is static source/decompile evidence only. Runtime title-bar rendering remains unproven by this page.
