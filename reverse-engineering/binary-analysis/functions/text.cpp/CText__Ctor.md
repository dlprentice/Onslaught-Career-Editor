# CText__Ctor

> Address: 0x004f2150 | Source: text.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** No (source not available)

## Purpose
Lightweight constructor/reset for `CText`.

This does **not** free an existing buffer. Cleanup and deep-copy behavior is handled by [CText__CopyFrom](CText__CopyFrom.md).

## Signature
```c
// Thiscall convention (ECX = this)
void CText::Ctor();
```

## Key Observations
Sets the following fields:
- `mLanguage` = `-1` (offset `0x1C`)
- `mBuffer` = `NULL` (offset `0x04`)
- `mLoaded` = `0` (offset `0x14`)
- `mVersion` = `0` (offset `0x00`)
- `mFileSize` = `0` (offset `0x18`)

Note: It does not explicitly clear `mTextPool`, `mAudioPool`, or `mCount`. In practice these are either 0 (fresh BSS) or overwritten by `Init()`.

## Behaviour
It sets the language to `-1`, the buffer to null, and the loaded flag, version and file size to zero.

*Decompiler listing removed from the public tree (private RE archive: `scrubbed-passages/reverse-engineering/binary-analysis/functions/text.cpp/CText__Ctor.md`, block 1).*

## Related Functions
- [CText__Init](CText__Init.md) - Loads/parses the language file into `mBuffer` and populates pools
- [CText__CopyFrom](CText__CopyFrom.md) - Deep copy/assignment (allocates + adjusts pointers)
- [CText__GetStringById](CText__GetStringById.md) - Retrieves a string by `text_id`
