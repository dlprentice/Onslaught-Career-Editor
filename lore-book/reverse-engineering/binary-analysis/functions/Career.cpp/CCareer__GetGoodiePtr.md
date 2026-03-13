# CCareer__GetGoodiePtr

> Address: 0x00421980 | Source: (binary helper; pointer arithmetic)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** N/A (this is effectively `&mGoodies[index]`)

## Purpose
Returns a pointer to a `CGoodie` entry given an index:

```c
return (this + index * 4);
```

In practice, callers pass `ECX = (CCareer + 0x1F44)` (the base of the `CGoodie[300]` array) and `param_1 = goodieIndex`.

## Signature
```c
void * CCareer__GetGoodiePtr(void * this, int goodie_index);
```

## Notes
- Heavily used by `CCareer__UpdateGoodieStates` (`0x0041c470`) while recomputing unlock states.
- This helper is a good candidate for inlining in source builds; here it is materialized as a tiny leaf function.

## Related
- [CCareer__UpdateGoodieStates](CCareer__UpdateGoodieStates.md)
