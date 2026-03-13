# CText__GetAudioNameById

> Address: 0x004f24b0 | Source: text.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** No (source not available)

## Purpose
Resolves a `text_id` to an audio/voice identifier string (ASCII) for v2/v3 language `.dat` files.

This uses the `audio_off_bytes` field in the v2/v3 entry table and returns a pointer into `mAudioPool`.

## Signature
```c
// Thiscall convention (ECX = this)
const char* CText::GetAudioNameById(int text_id);
```

## Behavior
- Only operates when `mVersion` is `2` or `3`.
- Scans the entry table `{ text_id, text_off_words, audio_off_bytes }` at `mBuffer + 0x0C`.
- If `audio_off_bytes == 0xFFFFFFFF`, returns `NULL`.
- Otherwise returns `mAudioPool + audio_off_bytes`.

## Related
- [CText__Init](CText__Init.md) - Computes `mAudioPool` for v2/v3
- [tools/language_dat_decode.py](../../../../tools/language_dat_decode.py) - Can dump `audio_off_bytes` and audio identifiers offline
