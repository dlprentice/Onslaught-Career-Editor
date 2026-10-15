# CGame__GetNumSecondaryObjectives

- **Address:** `0x00472690`
- **Saved signature:** `int __fastcall CGame__GetNumSecondaryObjectives(void * this)`
- **Source context:** `references/Onslaught/game.cpp`, `CGame::GetNumSecondaryObjectives`

## Summary

Counts defined secondary objective rows in the CGame objective table at `this+0x9c`.

## Notes

- Wave 381 supersedes the older `CGame__CountActiveSlots_B` label.
- Saved via serialized headless dry/apply/read-back on 2026-05-13.
- The source and retail evidence agree on a bounded ten-row secondary-objective scan.

## Not Proven

- Runtime objective UI behavior is not proven by this static pass.
- Concrete objective row structure names and local types remain open.
- BEA launch behavior, game patching, and rebuild parity are not proven.
