# CGoodieData__ctor

> Address: `0x0045c770`  
> Source: `references/Onslaught/FEPGoodies.cpp`

## Status
- Named in Ghidra: Yes
- Signature set: Yes
- Verified vs source: Yes

## Signature

```c
void CGoodieData__ctor(void * this, int method, int method2, int number, int number2, int t1, int t2)
```

## Behavior

- Writes 6 consecutive fields on the destination object:
  - `Method`
  - `Method2`
  - `Number`
  - `Number2`
  - `mT1`
  - `mT2`
- This matches the constructor body for `CGoodieData` in source.

## Notes

- Called repeatedly by the static goodie-table builder path (`FUN_0045ac30`) to materialize entries.
