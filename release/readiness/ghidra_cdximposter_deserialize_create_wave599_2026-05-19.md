# Ghidra CDXImposter Deserialize/Create Wave599 Readiness Note

Date: 2026-05-19
Status: static saved-Ghidra evidence only

Wave599 hardened the next queue head after Wave598: the CDXImposter IMPS chunk deserialize/create pair.

Saved rows:

| Address | Function |
| --- | --- |
| `0x00543d90` | `CDXImposter__Deserialize` |
| `0x00543f50` | `CDXImposter__Create` |

What is proven:

- Ghidra now records clean signatures, function comments, and `cdximposter-deserialize-create-wave599` tags for both rows.
- `CResourceAccumulator__ReadResourceFile` dispatches the IMPS chunk by pushing the active `CChunkReader` at `0x004d7705` and calling `0x00543d90 CDXImposter__Deserialize`; the caller cleans one stack argument with `ADD ESP, 0x4`.
- `CDXImposter__Deserialize` reads imposter atlas width/height globals `0x008aa8c0` and `0x008aa8c4`, replaces texture atlas global `0x008aa8b8` through `CDXTexture__Deserialize`, increments the atlas refcount at `+0xa4`, reads an imposter count, loops through `CDXImposter__Create`, allocates primary/secondary CVBufTexture globals `0x008aa8b4` and `0x008aa8cc`, sets VB format `0x152` and IB format `0x65`, and marks `0x0067a67c` initialized.
- `CDXImposter__Create` is called from `CDXImposter__Deserialize` with the same chunk reader. It allocates a `0x4c` OID type `0x39` imposter, clears `+0x30/+0x38/+0x3c`, increments `0x008aa8bc`, reads the serialized object payload, resolves a mesh/resource id through `CMesh__FindByRuntimeId`, stores it at `+0x24`, allocates frame data sized `+0x44 * +0x40 * 0x18`, reads frame records, restores the first dword, calls `CImposter__AddToList`, and returns the imposter pointer.
- Post-save read-back verified 2 metadata rows, 2 tag rows, 2 xref rows, 514 instruction rows, and 2 decompile rows.
- The queue refresh reports `6093` total functions, `3074` commented, `3019` commentless, `1331` exact-undefined signatures, and `1080` `param_N` signatures.
- Comment-backed proxy is `3074/6093 = 50.45%`; strict clean-signature proxy is `3029/6093 = 49.71%`.
- The next high-signal queue head is `0x00544040 CDXEngine__ClearHudTextureSlots`.
- The live Ghidra project backup verified at `G:\GhidraBackups\BEA_20260519-171359_post_wave599_cdximposter_deserialize_create_verified` with 19 files, 161155975 bytes, `DiffCount=0`, and manifest hash `df8ccc75f58e1c97db971b748b64b6909d61a4c602e16ce1fbc7c27f95178fa5`.

What is not proven:

- Runtime imposter loading, visible LOD behavior, runtime tree billboard behavior, and game-frame correctness remain unproven.
- Exact IMPS chunk contract, `CDXImposter`, `CImposter`, CVBufTexture, texture-atlas, mesh/resource-id, frame-data, and global-block layouts remain unproven beyond observed fields documented in the read-back notes.
- Exact source identity remains unproven because the current tracked Stuart source snapshot does not provide a byte/layout-matching retail DXImposter implementation.
- BEA patching, gameplay behavior, packaged release behavior, and rebuild parity remain unproven.
