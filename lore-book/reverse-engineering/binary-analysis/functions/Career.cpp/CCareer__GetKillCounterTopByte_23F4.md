# CCareer__GetKillCounterTopByte_23F4

> Address: 0x004218f0 | Source: (binary helper; CCareer field access)

## Status
- **Named in Ghidra:** Yes (renamed from `FUN_004218f0`)
- **Signature Set:** Yes
- **Verified vs Source:** N/A (not obviously present in Stuart's `references/Onslaught/Career.cpp`)

## Purpose
Returns the **top byte** (high 8 bits) of the dword at `CCareer + 0x23F4`, expressed as a signed-with-bias value:

```c
return ((*(uint32_t*)(this + 0x23F4) >> 24) - 0x80);
```

This byte is *not* part of the kill count payload. In the retail binary it is used as **persistent options/metadata** (cached/restored via the Front End options system). The exact UI meaning is still TBD.

Interpretation:
- `storedTopByte` is an on-disk byte value.
- This function returns `storedTopByte - 0x80` (typically clamped to `[-0x40..0x40]` on load).

## Signature
```c
int CCareer__GetKillCounterTopByte_23F4(void * this);
```

## Notes
- Called by `CFEPOptions__GetKillCounterTopBytes_23F4_23F8` (`0x0051f470`) to fetch one of the two persisted metadata values.
- The matching setter is `CCareer__SetKillCounterTopByte_23F4` (`0x00421910`).
- `CCareer__Load` (`0x00421200`) clamps the top byte for the first two counters (offsets `0x23F4` and `0x23F8`) into a limited range around `0x80`, while preserving the lower 24 bits.

## Related
- [CCareer__GetKillCounterTopByte_23F8](CCareer__GetKillCounterTopByte_23F8.md)
- [CCareer__SetKillCounterTopByte_23F4](CCareer__SetKillCounterTopByte_23F4.md)
- [CCareer__Load](CCareer__Load.md)
