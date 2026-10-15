# CFrontEnd__DrawSlidingTextBordersAndMask

- Address: 0x00467200
- Status: Renamed (headless batch, read-back verified)
- Current saved signature: `void __thiscall CFrontEnd__DrawSlidingTextBordersAndMask(void * this, float transition, int dest_page)`
- Source match: references/Onslaught/frontEnd.cpp:807 (void CFrontEnd::DrawSlidingTextBordersAndMask(float transition, EFrontEndPage dest))

## Purpose

Renders animated bracket and mask layers used during frontend transitions.

## Notes

Wave 377 hardened the saved Ghidra signature/comment/tag. The helper takes a transition value and destination page, uses the source-static page predicate now saved as [FrontEnd__HasStandardSlidingTextBordersAndMaskPage](./FrontEnd__HasStandardSlidingTextBordersAndMaskPage.md), and dispatches the shared selection-bracket renderer while shaping per-page mask behavior.

This is static source/decompile evidence only. Runtime frontend rendering remains unproven by this page.
