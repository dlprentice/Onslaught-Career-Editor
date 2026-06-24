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

## 2026-05-07 Xref Read-Back

A read-only Ghidra xref export for `0x00421980` wrote 423 rows. A second read-only export checked the concrete `g_Career_mGoodies[71..73]` addresses. `tools/goodies_getgoodieptr_xref_probe.py --check` passed and confirmed all 423 exported helper calls currently resolve to `CCareer__UpdateGoodieStates`, with zero direct data references reported for the 71-73 state addresses.

This supports the current Goodies 71-73 model: `CCareer__GetGoodiePtr` is an unlock-recomputation helper in the known retail xref set, not evidence for a frontend direct-selection path. It does not prove that no indirect array access or runtime-only path can request 71-73.

## Related
- [CCareer__UpdateGoodieStates](CCareer__UpdateGoodieStates.md)
