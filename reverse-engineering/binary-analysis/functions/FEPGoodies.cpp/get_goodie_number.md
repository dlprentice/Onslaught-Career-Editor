# get_goodie_number

> Address: `0x0045cb80`  
> Source: `references/Onslaught/FEPGoodies.cpp` (static `get_goodie_number`)

## Status
- Named in Ghidra: Yes
- Signature set: Yes
- Verified vs source: Yes

## Signature

```c
int get_goodie_number(int x, int y)
```

## Behavior

- Maps goodies-grid coordinates `(x,y)` to a flattened goody id.
- Applies category/range-specific remap offsets.
- Returns `-1` when the requested grid position is invalid/unmapped.

## Notes

- Used by `CFEPGoodies__StartLoadingGoody`, `CFEPGoodies__LoadingGoodyPoll`, and `CFEPGoodies__Process`.
