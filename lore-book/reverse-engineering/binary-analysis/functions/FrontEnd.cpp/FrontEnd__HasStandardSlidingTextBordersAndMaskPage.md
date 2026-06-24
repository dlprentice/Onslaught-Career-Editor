# FrontEnd__HasStandardSlidingTextBordersAndMaskPage

- Address: 0x004679a0
- Status: Renamed (headless batch, Wave 377 read-back verified)
- Current saved signature: `int __cdecl FrontEnd__HasStandardSlidingTextBordersAndMaskPage(int dest_page)`
- Source match: references/Onslaught/frontEnd.cpp:778 (static BOOL got_standard_SlidingTextBordersAndMask(EFrontEndPage dest))

## Purpose

Returns whether a destination frontend page uses the standard sliding text borders and mask transition style.

## Notes

Wave 377 corrected the older `CFrontEnd__HasStandardSlidingTextBordersAndMask` owner wording because the source analogue is a source-static page predicate, not a `CFrontEnd` instance method. The saved comment records the observed standard page switch set `7,8,9,10,11,13,14,16,17,19`.

This is static source/decompile evidence only. Runtime page styling remains unproven by this page.
