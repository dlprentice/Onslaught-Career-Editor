# CText__ResetCoreFields

> Address: 0x004f2140 | Source: text.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** No (source not available)

## Purpose
Clears the core "loaded text" fields without touching `mLanguageId`.

Observed usage: called from `CFEPMultiplayerStart__ctor` to initialize an embedded `CText` member.

## Signature
```c
// Thiscall convention (ECX = this)
void CText::ResetCoreFields();
```

## Behavior
Sets:
- `mBuffer = NULL`
- `mLoaded = 0`
- `mVersion = 0`
- `mFileSize = 0`

Does not set `mLanguageId` (contrast with [CText__Ctor](CText__Ctor.md), which sets `mLanguageId = -1`).

