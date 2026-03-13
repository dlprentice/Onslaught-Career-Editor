# CFEPLevelSelect__UpdateMouseEdgeSlide

> Address: `0x0045d730`  
> Source parity: inferred helper (single callsite from `CFEPLevelSelect__Process`)

## Status
- Named in Ghidra: Yes
- Signature set: Yes
- Verified vs source: Partial (behavior-confirmed, exact source symbol name unknown)

## Signature

```c
void CFEPLevelSelect__UpdateMouseEdgeSlide(int state, float * value, float max_value)
```

## Behavior

- Early-outs unless FE state allows pointer-driven slide updates.
- Reads pointer-edge input globals and applies a cubic response curve.
- Accumulates into `*value`, then clamps to `[0, max_value]`.
- Called from `CFEPLevelSelect__Process` with `max_value = 1100.0f`.
