# CCareer__SetKillCounterTopByte_23F4

> Address: 0x00421910 | Source: (binary helper; CCareer field access)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** N/A (not obviously present in Stuart's `references/Onslaught/Career.cpp`)

## Purpose
Updates only the **top byte** (high 8 bits) of the dword at `CCareer + 0x23F4`, preserving the lower 24-bit payload:

```c
uint32_t old = *(uint32_t*)(this + 0x23F4);
*(uint32_t*)(this + 0x23F4) = ((arg - 0x80) << 24) | (old & 0x00FFFFFF);
```

This is used by the retail binary to persist options/metadata (cached/restored via the Front End options system), not to edit the kill count itself. The exact UI meaning is still TBD.

Interpretation:
- `top_byte` is the same signed-with-bias value returned by `CCareer__GetKillCounterTopByte_23F4`.
- The stored top byte becomes `(uint8_t)(top_byte + 0x80)`.

## Signature
```c
void CCareer__SetKillCounterTopByte_23F4(void * this, int top_byte);
```

## Notes
- Called by `CFEPOptions__SetKillCounterTopBytes_23F4_23F8` (`0x0051f490`) to persist one of the two metadata values.
- The corresponding getter is `CCareer__GetKillCounterTopByte_23F4` (`0x004218f0`).
- `CCareer__Load` (`0x00421200`) clamps this byte on load for offsets `0x23F4` and `0x23F8`.

## Related
- [CCareer__GetKillCounterTopByte_23F4](CCareer__GetKillCounterTopByte_23F4.md)
- [CCareer__SetKillCounterTopByte_23F8](CCareer__SetKillCounterTopByte_23F8.md)
- [CCareer__Load](CCareer__Load.md)
