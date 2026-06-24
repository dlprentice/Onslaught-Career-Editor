# CFEPGoodies__Deserialise

> Address: `0x0045c870`
> Source: `references/Onslaught/FEPGoodies.cpp` (`CFEPGoodies::Deserialise`)

## Status
- Named in Ghidra: Yes
- Signature set: Yes
- Verified vs source: Yes (retail naming now aligned)

## Signature

```c
void CFEPGoodies__Deserialise(void * this, void * chunk_reader)
```

## Behavior

- Frees prior currently-loaded goody payload by calling `CFEPGoodies__FreeUpGoodyResources`.
- Deserializes goody content from the resource stream:
  - Texture list (`CDXTexture__Deserialize`)
  - Optional mesh (`CMesh__Deserialize`)
- Stores pointers/count/height metadata in the goody page object (`this+0x144/+0x148/+0x14c/+0x150`).
- Refcount increments are applied to loaded resources.

## Evidence

- `CResourceAccumulator__ReadResourceFile` has a direct call xref into `0x0045c870` for `GDIE` chunk handling.

## Wave395 Saved-Ghidra Read-Back (2026-05-14)

- Saved signature preserved as `void __thiscall CFEPGoodies__Deserialise(void * this, void * chunk_reader)`.
- Saved function comment now records the free-before-load, `GDAT` payload-type read, texture-array state, and mesh-slot state claim as static retail evidence only.
- Saved tags include `static-reaudit`, `goodies-wave395`, `frontend-goodies`, `resource-deserialise`, `gdatie-gdat`, `retail-binary-evidence`, and `comment-hardened`.
- Read-back includes `CFEPGoodies__FreeUpGoodyResources`, `CChunkReader__GetNext`, texture/mesh deserialize context, and object fields around `+0x144`, `+0x148`, `+0x150`, and `+0x154`.
- This does not prove exact chunk structure typing, full asset payload completeness, runtime playback/viewer behavior, or rebuild parity.
