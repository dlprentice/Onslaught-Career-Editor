# CFEPGoodies__Deserialise

Status: active, bounded retail correction with historical notes retained
Last updated: 2026-09-27
Summary: retail image loading uses one texture and a derived height; source image-loop equivalence is disproved.
Source File: `references/Onslaught/FEPGoodies.cpp:1153–1223` | Binary: pristine `BEA.exe.original.backup`, identified below.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

> Address: `0x0045c870`
> Source: `references/Onslaught/FEPGoodies.cpp` (`CFEPGoodies::Deserialise`)

## September 27 retail recheck

All 355 bytes / 111 instructions in `[0045c870,0045c9d1)` were decoded from
the pristine specimen: SHA-256
`b2cbf9bf862db96797373dbf790aaaf4e82e2f72765886877f4b867085b3a800`.
The `GDIE` dispatcher call at `004d78f3` supplies this reader and receiver
`008a0f34`. The pinned source at `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`,
`FEPGoodies.cpp:1153–1223`, establishes the matching method identity but has
important differences:

- Retail calls GetNext at entry and reads number/type without testing the
  returned tag against source's GDAT assertion. Read statuses are ignored.
- Type zero sets `+14c` to one, allocates one pointer, calls the texture consumer
  once and stores its result through `+144`. It increments the texture's
  `+a4` word and sign-extends the word at texture `+b0` into page `+150`.
  This is different from the source IMAG header/count/height/texture loop.
- Type one retains a texture-count loop and a final mesh-consumer call. It
  increments the mesh's `+170` word. Other types return without the source's
  assertion path. Complete texture/mesh payload formats are separate.

The [reader/dispatcher contract](../../../source-code/io/chunker-system.md)
owns the transport evidence and source differences. This pass did not run
the Goodies loader, validate allocation failures, render the gallery or
promote its saved prototype/comment. Its older unqualified source-parity
statement below is superseded by these limits.

## Historical status and description
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
