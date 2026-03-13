# CText__FreeBuffer

> Address: 0x004f2170 | Source: text.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** No (source not available)

## Purpose
Frees the loaded language file buffer (if present) and clears `mBuffer`.

This is the cleanup primitive used by higher-level operations like [CText__CopyFrom](CText__CopyFrom.md).

## Signature
```c
// Thiscall convention (ECX = this)
void CText::FreeBuffer();
```

## Key Observations
- If `mBuffer != NULL`, calls `OID__FreeObject(mBuffer)` then sets `mBuffer = NULL`.
- Does not clear `mLoaded`, `mVersion`, etc (callers typically reset those separately).

## Related Functions
- [CText__CopyFrom](CText__CopyFrom.md) - Frees before deep-copying
- [CText__Ctor](CText__Ctor.md) - Lightweight reset (does not free)

