# CGame__XorBlock64Words

- **Address:** `0x00472270`
- **Source context:** `references/Onslaught/game.cpp` (behavior-level alignment pass)

## Summary

XORs two 0x64-byte blocks (ushort lanes) into scratch globals; used as an inline XOR helper.

## Notes

- Recovered and semantically renamed via headless decompile + batch-rename workflow (2026-02-25).
- Signature is still decompiler-derived; parameter naming remains provisional pending deeper callsite pass.
