# CFEPGoodies__StartLoadingGoody

> Address: `0x0045c9f0`  
> Source: `references/Onslaught/FEPGoodies.cpp` (`CFEPGoodies::StartLoadingGoody`)

## Status
- Named in Ghidra: Yes
- Signature set: Yes
- Verified vs source: Yes

## Signature

```c
void CFEPGoodies__StartLoadingGoody(void * this)
```

## Behavior

- Clears current load-state/result fields.
- Resolves selected goody id through `get_goodie_number(this->mCX, this->mCY)`.
- Computes goody content type bucket (image/mesh/fmv/level/cheat behavior path).
- For loadable goody types, starts async mission-script resource load and marks goody state as loading.
