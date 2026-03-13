# CFEPGoodies__FreeUpGoodyResources

> Address: `0x0045cd10`  
> Source: `references/Onslaught/FEPGoodies.cpp` (`CFEPGoodies::FreeUpGoodyResources`)

## Status
- Named in Ghidra: Yes
- Signature set: Yes
- Verified vs source: Yes

## Signature

```c
void CFEPGoodies__FreeUpGoodyResources(void * this)
```

## Behavior

- Releases currently loaded goody mesh (if present) and decrements refcount.
- Releases all currently loaded goody textures and clears render-target/texture pointers.
- Frees texture-pointer array storage.
- Resets loader state to no-goody.
