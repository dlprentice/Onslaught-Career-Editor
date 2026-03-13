# CFEPGoodies__LoadingGoodyPoll

> Address: `0x0045cc10`  
> Source: `references/Onslaught/FEPGoodies.cpp` (`CFEPGoodies::LoadingGoodyPoll`)

## Status
- Named in Ghidra: Yes
- Signature set: Yes
- Verified vs source: Yes

## Signature

```c
void CFEPGoodies__LoadingGoodyPoll(void * this)
```

## Behavior

- Checks async loader/thread state.
- When async load completes, reads goody resource data, closes temporary buffers/chunkers, and releases temporary objects.
- Promotes goody load state to loaded and logs load timing.
