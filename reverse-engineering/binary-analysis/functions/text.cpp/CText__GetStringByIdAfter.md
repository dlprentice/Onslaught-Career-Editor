# CText__GetStringByIdAfter

> Address: 0x004f2500 | Source: text.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** No (source not available)

## Purpose
Returns the UTF-16 string for the entry `afterIndex` positions after the entry whose `text_id` matches.

This is useful for "multi-line" or grouped strings stored consecutively in the entry table.

## Signature
```c
// Thiscall convention (ECX = this)
const wchar_t* CText::GetStringByIdAfter(int text_id, int afterIndex);
```

## Behavior (v1/v2/v3)
- Requires `mVersion <= 3` (otherwise triggers a fatal error: `TextDB_unsupported_v...`).
- Scans the v1/v2/v3 entry table at `mBuffer + 0x0C` to find the matching `text_id`.
- On match, reads `text_off_words` from the entry at `(matchIndex + afterIndex)` and returns:
  - `mTextPool + text_off_words * 2`
- On miss, logs `ERROR: No string after for id ...` and returns `mTextPool`.

Notes:
- Retail `.dat` files are v3, so this is the expected path.
- This function is not designed for legacy v0 layout.

## Related
- [CText__GetStringById](CText__GetStringById.md) - Simpler lookup for the matching entry

