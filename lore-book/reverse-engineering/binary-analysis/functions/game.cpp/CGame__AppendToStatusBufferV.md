# CGame__AppendToStatusBufferV

- **Address:** `0x00472240`
- **Source context:** `references/Onslaught/game.cpp` (behavior-level alignment pass)

## Summary

Appends formatted text into the game status/debug string buffer using `vsprintf` semantics.

## Notes

- Recovered and semantically renamed via headless decompile + batch-rename workflow (2026-02-25).
- Signature is still decompiler-derived; parameter naming remains provisional pending deeper callsite pass.
