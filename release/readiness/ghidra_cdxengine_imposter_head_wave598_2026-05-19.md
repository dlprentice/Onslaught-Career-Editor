# Ghidra CDXEngine/DXImposter Head Wave598 Readiness Note

Date: 2026-05-19
Status: static saved-Ghidra evidence only

Wave598 hardened the next queue head after Wave597: the CDXEngine/DXImposter imposter setup and render-head cluster around `0x00542740`.

Saved rows:

| Address | Function |
| --- | --- |
| `0x00542740` | `CDXEngine__InitLandscapeTextureTables` |
| `0x005428d0` | `CDXImposter__InitGlobals` |
| `0x00542990` | `CDXImposter__ShutdownAll` |
| `0x00542a30` | `CDXImposter__InitEntry` |
| `0x00542a50` | `CDXEngine__BuildDirectionalSampleRing` |
| `0x00542ee0` | `CDXEngine__BuildZRotationMatrix` |
| `0x00543300` | `CDXEngine__RenderImposterBillboardSet` |
| `0x005438c0` | `CDXImposter__RenderAll` |

What is proven:

- Ghidra now records clean signatures, function comments, and `cdxengine-imposter-head-wave598` tags for all eight rows.
- `CDXEngine__InitLandscapeTextureTables` is an ECX-input helper reached from a static-init region; it loads `0x008aa4e8`, calls the current `0x00481400` helper, and returns the same pointer.
- `CDXImposter__InitGlobals` is called by `CGame__Init`, clears the observed imposter global block including `0x00650848` and `0x008aa8bc`, and returns 1.
- `CDXImposter__ShutdownAll` walks the imposter list at `0x0067a678`, frees frame-data allocations, releases CVBufTexture slots and texture globals, and clears observed width/height globals.
- `CDXImposter__InitEntry` is called by `CImposter__FindOrCreate` for a `0x4c` imposter object, clears `+0x30/+0x38/+0x3c`, increments `0x008aa8bc`, and returns the input object.
- `CDXEngine__BuildDirectionalSampleRing` is reached from `CDXEngine__Render`, takes one float yaw argument, prepares the imposter sample ring and matrix globals around `0x0067a680` and `0x008aa790`, and calls `CDXEngine__BuildZRotationMatrix`.
- `CDXEngine__BuildZRotationMatrix` has a saved `__thiscall` signature with `this` plus one stack float; `RET 0x4` proves one stack parameter, and the body builds a Z-rotation basis with an identity Z row.
- `CDXEngine__RenderImposterBillboardSet` has a saved `__thiscall` signature with `this`, `view_context`, `alpha`, and `frame_index`; `RET 0xc` proves three stack parameters after `this`, and the body drives CRTTree/CDXImposter billboard geometry through `CDXImposter__BuildQuadGeometry`.
- `CDXImposter__RenderAll` is called by `CDXEngine__Render`; it gates the global imposter render pass, binds the texture atlas, renders through CVBufTexture paths, and restores sampler/state-cache values.
- The first apply pass deliberately exposed a Ghidra read-back signature mismatch for the two `__thiscall` rows because Ghidra materialized the ECX parameter as `this`; the corrected dry/apply/final-dry pass saved the explicit `this` signatures and finished idempotently.
- Post-save read-back verified 8 metadata rows, 8 tag rows, 9 xref rows, 888 instruction rows, and 8 decompile rows.
- The queue refresh reports `6093` total functions, `3072` commented, `3021` commentless, `1333` exact-undefined signatures, and `1080` `param_N` signatures.
- Comment-backed proxy is `3072/6093 = 50.42%`; strict clean-signature proxy is `3027/6093 = 49.68%`.
- The next high-signal queue head is `0x00543d90 CDXImposter__Deserialize`.
- The live Ghidra project backup verified at `G:\GhidraBackups\BEA_20260519-164920_post_wave598_cdxengine_imposter_head_verified` with 19 files, 161155975 bytes, `DiffCount=0`, and manifest hash `d9ff83eb80ef21d63e7435740b015102f7f94ae98edc2e9e64b2ed58e2dd3c20`.

What is not proven:

- Runtime imposter rendering, runtime tree billboard behavior, visible LOD behavior, and game-frame correctness remain unproven.
- Exact `CDXEngine`, `CDXImposter`, `CImposter`, matrix/vector, CVBufTexture, texture-atlas, render-state, and global-block layouts remain unproven beyond observed fields documented in the read-back notes.
- Exact source identity remains unproven because the current tracked Stuart source snapshot does not provide a byte/layout-matching retail imposter render implementation.
- BEA patching, gameplay behavior, packaged release behavior, and rebuild parity remain unproven.
