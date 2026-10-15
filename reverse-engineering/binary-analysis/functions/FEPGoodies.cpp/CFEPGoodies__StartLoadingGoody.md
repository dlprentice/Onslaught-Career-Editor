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

## Headless Read-Back Detail (2026-05-07)

Read-only headless Ghidra export rechecked the compiled retail function at `0x0045c9f0`:

- It resolves the selected grid coordinate through `get_goodie_number`.
- For valid selections, it asks the resource accumulator for the `-1000 - goodieId` resource filename.
- It branches selected Goodie ids into content buckets before deciding whether to start an async resource load.
- Non-resource buckets such as FMV/level-style paths skip the async `GDIE` resource load and mark the goody as ready through the alternate state path.

This supports the current Asset Library split between local texture/model preview rows, media handoff rows, and level/metadata rows.

## Wave395 Saved-Ghidra Read-Back (2026-05-14)

- Saved signature preserved as `void __fastcall CFEPGoodies__StartLoadingGoody(void * this)`.
- Saved function comment now records image-pan reset, `get_goodie_number` selection mapping, `-1000-goodie` resource filename construction, current-type storage, and async/ready-state branching as static/source-parity evidence only.
- Saved tags include `static-reaudit`, `goodies-wave395`, `frontend-goodies`, `async-goodie-load`, `goodie-resource-filename`, `retail-binary-evidence`, and `comment-hardened`.
- Instruction/decompile read-back includes stores at the image pan offsets, a call to `get_goodie_number`, `-1000 - goodieId` resource-id construction, selected type/state writes, and the `0x500000` async load size.
- This does not prove runtime load timing, all asset coverage, hidden Goodies reachability, or rebuild parity.
