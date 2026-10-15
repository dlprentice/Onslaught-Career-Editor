# CCareer__GetAndResetGoodieNewCount

> Address: 0x00421550 | Source: `references/Onslaught/Career.cpp` (`CCareer::GetAndResetGoodieNewCount`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Yes

## Purpose
Returns the current debriefing new-goodie count, then resets it to zero.

Retail behavior (BEA.exe): reads `0x00662b20`, writes `0`, returns previous value.

## Signature
```c
int CCareer__GetAndResetGoodieNewCount(void);
```

## Notes
- This is not a per-goodie accessor; it is a single aggregate counter consumed by UI flow.
- In source this corresponds to:
  - `SINT v = new_goodie_count;`
  - `new_goodie_count = 0;`
  - `return v;`

## Related Functions
- [CCareer__UpdateGoodieStates](CCareer__UpdateGoodieStates.md) - Produces `new_goodie_count`
- [CCareer__GetAndResetFirstGoodie](CCareer__GetAndResetFirstGoodie.md) - Companion debriefing consume/reset flag
