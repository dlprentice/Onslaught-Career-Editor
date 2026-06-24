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

## Wave395 Saved-Ghidra Read-Back (2026-05-14)

- Saved signature preserved as `void __fastcall CFEPGoodies__FreeUpGoodyResources(void * this)`.
- Saved function comment now records mesh/texture release, backing-resource destruction, texture-pointer-array free, counter/slot clear, and `NO_GOODY` reset as static retail evidence only.
- Saved tags include `static-reaudit`, `goodies-wave395`, `frontend-goodies`, `resource-cleanup`, `goodie-resource-lifetime`, `retail-binary-evidence`, and `comment-hardened`.
- Read-back includes fields around `+0x144`, `+0x148`, `+0x14c`, `+0x170`, and `+0x1d8`, plus `CTexture__Release` and `OID__FreeObject` context.
- This does not prove allocator/layout completeness, runtime asset lifetime behavior, or rebuild parity.
