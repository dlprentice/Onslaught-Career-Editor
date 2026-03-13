# CText__GetStringById

> Address: 0x004f2580 | Source: text.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** No (source not available)

## Purpose
Resolves a `text_id` to a UTF-16 string pointer using the currently loaded language file.

This is the primary "text lookup" routine used throughout the game once `CText__Init` has loaded `data/LANGUAGE/<lang>.DAT`.

## Signature
```c
// Thiscall convention (ECX = this)
const wchar_t* CText::GetStringById(int text_id);
```

## Parameters
- `text_id` (param_1): For v1/v2/v3 this is the 32-bit `text_id` stored in the language `.dat` entry table.

## Key Observations

### Version 1/2/3: Entry Table Scan
For `mVersion > 0`, the function performs a linear scan over the entry table in `mBuffer`:
- Entry base: `(mBuffer + 0x0C)`
- Entry stride:
  - v1: 2 dwords per entry
  - v2/v3: 3 dwords per entry (`{ text_id, text_off_words, audio_off_bytes }`)

When a matching `text_id` is found, it returns:
```c
return (const wchar_t*)(mTextPool + text_off_words * 2);
```

`text_off_words` is measured in UTF-16 code units from the start of `mTextPool`.

If not found, logs `ERROR: No string for id %d` and returns `mTextPool` as a fallback.

### Version 0: Legacy Index + MultiByteToWideChar
For `mVersion == 0`, the parameter is treated like an **index** into a legacy offset table.

The resolved multibyte string is converted to UTF-16 with `MultiByteToWideChar` into a global scratch buffer (`DAT_0083d560`), which is returned.

Notes:
- This buffer is effectively shared state (not thread-safe).
- Retail `.dat` files are v3, so this path is likely unused in normal gameplay.

## Decompiled Code (Annotated)
```c
const wchar_t* CText__GetStringById(int text_id)
{
  int stride = 2;
  if (this->mVersion == 2 || this->mVersion == 3) {
    stride = 3;
  }

  if (this->mVersion > 0) {
    // v1/v2/v3: scan entry table in mBuffer
    int* pId   = (int*)(this->mBuffer + 0x0C);
    int* pText = (int*)(this->mBuffer + 0x10);

    for (int i = 0; i < this->mCount; i++) {
      if (text_id == *pId) {
        return (const wchar_t*)((char*)this->mTextPool + (*pText) * 2);
      }
      pId   += stride;
      pText += stride;
    }

    Log("ERROR: No string for id %d", text_id);
    return this->mTextPool;
  }

  // v0: legacy index + offset table => convert to UTF-16 scratch buffer
  ...
}
```

## Related Functions
- [CText__Init](CText__Init.md) - Loads the language `.dat` file and sets `mVersion/mCount/mTextPool/mAudioPool`
- [CText__GetAudioNameById](CText__GetAudioNameById.md) - Audio/voice identifier lookup for v2/v3
- [CText__GetStringByIdAfter](CText__GetStringByIdAfter.md) - Lookup relative to a matched entry (grouped strings)
- The repo also includes `tools/language_dat_decode.py` for offline decoding of `text_id` values via `text.stf`.
