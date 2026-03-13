# CText__GetLanguageName

> Address: 0x004f2190 | Source: text.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** No (source not available)

## Purpose
Returns the lowercase language name string for `this->mLanguageId`:
`english`, `french`, `german`, `spanish`, `italian`.

## Signature
```c
// Thiscall convention (ECX = this)
const char* CText::GetLanguageName();
```

## Notes
- Logs `ERROR: unkown language %d` and falls back to `"english"` on unknown IDs.
- This duplicates the language switch used in [CText__Init](CText__Init.md), but uses `this->mLanguageId` rather than the `languageId` parameter.

