# CCareer__GetAndResetFirstGoodie

> Address: 0x00421560 | Source: `references/Onslaught/Career.cpp` (`CCareer::GetAndResetFirstGoodie`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Yes

## Purpose
Returns whether the session has a "first goodie" debriefing event pending, then clears the flag.

Retail behavior (BEA.exe): reads `0x00662b24`, writes `0`, returns previous value.

## Signature
```c
bool CCareer__GetAndResetFirstGoodie(void);
```

## Notes
- This is not a "new tech" flag in retail.
- In source this corresponds to:
  - `BOOL b = first_goodie;`
  - `first_goodie = FALSE;`
  - `return b;`

## Related Functions
- [CCareer__UpdateGoodieStates](CCareer__UpdateGoodieStates.md) - Sets `first_goodie` under unlock conditions
- [CCareer__GetAndResetGoodieNewCount](CCareer__GetAndResetGoodieNewCount.md) - Companion debriefing counter consume/reset
