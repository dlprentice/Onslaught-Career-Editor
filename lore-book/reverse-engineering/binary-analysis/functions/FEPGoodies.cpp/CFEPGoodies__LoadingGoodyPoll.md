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

## Wave395 Saved-Ghidra Read-Back (2026-05-14)

- Saved signature preserved as `void __fastcall CFEPGoodies__LoadingGoodyPoll(void * this)`.
- Saved function comment now records async-completion polling, membuffer handling, `-1000-goodie` resource read, buffer close/free, and loaded-state marking as static/source-parity evidence only.
- Saved tags include `static-reaudit`, `goodies-wave395`, `frontend-goodies`, `async-goodie-load`, `resource-poll`, `retail-binary-evidence`, and `comment-hardened`.
- Read-back includes loader state at `+0x1d8`, membuffer context at `+0x28`, `CBinkOpenThread__IsRunning`, `get_goodie_number`, `CResourceAccumulator__ReadResourceFile`, and `CDXMemBuffer__Close`.
- This does not prove runtime async behavior, asset decode success, hidden Goodies reachability, or rebuild parity.
