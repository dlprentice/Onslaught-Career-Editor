# Frontend__XorWideTextBlock100BytesToScratch

- **Address:** `0x00472270`
- **Saved signature:** `short * __cdecl Frontend__XorWideTextBlock100BytesToScratch(short * encoded_text, short * xor_mask)`
- **Source context:** frontend cheat/status text path

## Summary

XORs a `0x64` byte wide-text block from `encoded_text` and `xor_mask` into scratch buffer `DAT_00679e18`, then returns that scratch pointer.

## Notes

- Wave 381 supersedes the older `CGame__XorBlock64Words` label.
- The old description was size-ambiguous. Current evidence supports a 100-byte / 50-short frontend wide-text block used by the now-corrected `CGame__DrawGameStuff` overlay path.
- Saved via serialized headless dry/apply/read-back on 2026-05-13.

## Not Proven

- Runtime frontend text behavior is not proven by this static pass.
- Exact text-table ownership and higher-level cheat UI semantics remain open.
- BEA launch behavior, game patching, and rebuild parity are not proven.
