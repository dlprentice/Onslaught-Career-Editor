# Ghidra CDXEngine Kempy Cube Wave600 Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x005441b0` comment correction. The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Date: 2026-05-19
Status: static saved-Ghidra evidence only

Wave600 hardened the next queue head after Wave599: five CDXEngine Kempy cube resource/setup/render helpers around the older HUD-texture-slot labels.

Saved rows:

| Address | Function |
| --- | --- |
| `0x00544040` | `CDXEngine__ClearKempyCubeTextureSlots` |
| `0x00544060` | `CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer` |
| `0x005440a0` | `CDXEngine__InitKempyCubeTexturesAndVertexBuffer` |
| `0x005441a0` | `CDXEngine__InitKempyCubeResources` |
| `0x005441b0` | `CDXEngine__RenderKempyCubeFaces` |

What is proven:

- Ghidra now records clean signatures, function comments, and `cdxengine-kempy-cube-wave600` tags for all five rows.
- `CEngine__Init` allocates a `0xa14` resource block at `engine+0x498`, calls `0x00544040 CDXEngine__ClearKempyCubeTextureSlots`, and stores the returned pointer back at `engine+0x498`; the helper zeroes five texture slots at `+0x00..+0x10`.
- `CEngine__Shutdown` calls `0x00544060 CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer` for the same `engine+0x498` block; the helper walks five texture pointers, calls `CHud__DecrementCounter9C(texture+8)`, clears the slots, releases global CVBuffer pointer `0x008aa908` through the vtable delete path, and clears the global.
- `CEngine__SetKempyCube` forwards `engine+0x498` and one cube index through `0x005441a0 CDXEngine__InitKempyCubeResources`, which calls `0x005440a0 CDXEngine__InitKempyCubeTexturesAndVertexBuffer` and returns with `RET 0x4`.
- `CDXEngine__InitKempyCubeTexturesAndVertexBuffer` formats five texture paths through `CDXEngine__FormatCubeTextureFilename`, loads them through `CTexture__FindTexture`, stores the five texture pointers, recreates global CVBuffer `0x008aa908`, creates a `20`-vertex buffer with `20`-byte stride and FVF `0x102`, copies `100` dwords from static vertex data `0x006508f0`, and unlocks the buffer.
- `CDXEngine__Render` calls `0x005441b0 CDXEngine__RenderKempyCubeFaces` with `engine+0x498`; the helper copies view/world matrix data from `0x008aa8d8`, binds global CVBuffer `0x008aa908`, loops the five texture slots, resolves animated frames through `CDXTexture__GetAnimatedFrame`, issues the D3D draw path, and restores render/sampler state.
- Post-save read-back verified 5 metadata rows, 5 tag rows, 5 xref rows, 1505 instruction rows, and 5 decompile rows.
- The queue refresh reports `6093` total functions, `3079` commented, `3014` commentless, `1331` exact-undefined signatures, and `1075` `param_N` signatures.
- Comment-backed proxy is `3079/6093 = 50.53%`; strict clean-signature proxy is `3034/6093 = 49.79%`.
- The next high-signal queue head is `0x00544770 CDXLandscape__ReleaseOwnedResources`.
- The live Ghidra project backup verified at `[maintainer-local-ghidra-backup-root]\BEA_20260519-174509_post_wave600_cdxengine_kempy_cube_verified` with 19 files, 161188743 bytes, `DiffCount=0`, and manifest hash `d86b1630787846993bbd52f40f4821e89ecc5f13e8fa0afddccbe4feb8725247`.

What is not proven:

- Runtime cube rendering, visible sky/reflection behavior, texture asset correctness, and frame-state correctness remain unproven.
- Exact Kempy cube resource-block, texture, CVBuffer, vertex, render-state, matrix, and source class/body layouts remain unproven beyond observed fields documented in the read-back notes.
- Exact source identity remains unproven because the current tracked Stuart source snapshot does not provide a byte/layout-matching retail DXKempyCube implementation.
- BEA patching, gameplay behavior, packaged release behavior, and rebuild parity remain unproven.
