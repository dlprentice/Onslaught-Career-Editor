# CFrontEnd__SetLanguage

- Address: 0x00466ab0
- Status: Renamed (headless batch, read-back verified)
- Current saved signature: `void __thiscall CFrontEnd__SetLanguage(void * this, int language_index)`
- Source match: references/Onslaught/frontEnd.cpp:557 (void CFrontEnd::SetLanguage(SINT l))

## Purpose

Switches frontend text/language resources.

## Notes

Wave 377 hardened the saved Ghidra signature/comment/tag. Retail path cleans up frontend option text state and copies the selected text set into the active text database object.

This is static source/decompile evidence only. Runtime localization behavior remains unproven by this page.
