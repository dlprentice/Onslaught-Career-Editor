# CGame__IsWalkerGroundedOrCollision

- **Address:** `0x004080f0`
- **Source context:** `references/Onslaught/game.cpp` (behavior-level alignment pass)

## Summary

Checks walker-state plus ground/collision condition gate used by movement/camera logic.

## Notes

- Recovered and semantically renamed via headless decompile + batch-rename workflow (2026-02-25).
- 2026-05-09 signature tranche saved `bool __fastcall CGame__IsWalkerGroundedOrCollision(void * battleEngine)` after metadata/decompile/xref/instruction read-back.
- Current owner/source-method identity and concrete layout remain provisional; this is not runtime movement/collision proof.
