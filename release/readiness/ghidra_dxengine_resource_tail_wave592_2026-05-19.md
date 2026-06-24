# Ghidra DXEngine Resource Tail Wave592 Readiness Note

Date: 2026-05-19
Status: static saved-Ghidra evidence only

Wave592 hardened five CDXEngine resource-lifecycle rows at the static re-audit queue head. The split-out next row, `0x0053d760 CThing__RenderDebugVolumeOverlay`, remains deferred because its current signature shape is much larger than the existing queue row.

Saved rows:

| Address | Function |
| --- | --- |
| `0x0053d3a0` | `CDXEngine__ReleaseDefaultTextureAndMeshRefs` |
| `0x0053d3e0` | `CDXEngine__Shutdown` |
| `0x0053d4c0` | `CDXEngine__UploadScaledRgbLookupTable` |
| `0x0053d5f0` | `CDXEngine__Init` |
| `0x0053d6d0` | `CDXEngine__InitResources` |

What is proven:

- Ghidra now records clean signatures, comments, and `dxengine-resource-tail-wave592` tags for all five rows.
- `CLTShell__ShutdownRuntimeAndReleaseResources` passes the global CDXEngine object at `0x89c9a0` in `ECX` to `CDXEngine__ReleaseDefaultTextureAndMeshRefs`, which releases the default texture at `this+0x4e4`, decrements the default mesh usage counter at `this+0x28 + 0x170`, and clears both slots.
- The CDXEngine vtable at `0x005e4fc8` now resolves slot 0 to `CDXEngine__Init`, slot 1 to `CDXEngine__InitResources`, and slot 2 to `CDXEngine__Shutdown`.
- `CGame__Init` calls `CDXEngine__Init`; the body calls `CEngine__Init`, initializes render/resource fields, obtains a device RGB lookup table, registers `SetGammaBias`, `cg_renderreflections`, and `cg_texturereflections`, initializes `CDXPatchManager`, and returns `TRUE/FALSE`.
- `CGame__RunLevel` calls `CDXEngine__InitResources` after level resource loading and before GameInterface/HUD texture loading; the body calls `CEngine__InitResources`, loads `meshtex/default.tga`, `meshtex/outline.tga`, `meshtex/EdArrow.tga`, `default.msh`, and caches `Sun_Sprite`.
- `CDXEngine__Shutdown` calls `CEngine__Shutdown`, releases the observed texture/default-mesh handles, destroys `CDXPatchManager`, and clears the cached `Sun_Sprite` slot.
- `CDXEngine__UploadScaledRgbLookupTable` is a `RET 0x4` helper called by the `SetGammaBias` command stub with one float stack argument; the body scales three RGB lookup-table lanes and dispatches the active device vfunc at `+0x54`.
- Post-save read-back verified 5 metadata rows, 5 tag rows, 8 xref rows, 1305 instruction rows, 5 target decompile rows, 3 caller decompile rows, 205 callsite instruction rows, 1305 proof instruction rows, and 3 vtable rows.
- The queue refresh reports `6093` total functions, `3032` commented, `3061` commentless, `1347` exact-undefined signatures, and `1101` `param_N` signatures.
- Comment-backed proxy is `3032/6093 = 49.76%`; strict clean-signature proxy is `2986/6093 = 49.01%`.
- The next high-signal queue head is `0x0053d760 CThing__RenderDebugVolumeOverlay`.
- The live Ghidra project backup verified at `G:\GhidraBackups\BEA_20260519-134212_post_wave592_dxengine_resource_tail_verified` with 19 files, 160992135 bytes, `DiffCount=0`, and manifest hash `de15221c47eb97780dca8330a7a1decf858f621f3b267da86e4d8650488d7415`.

What is not proven:

- Runtime render/resource lifecycle behavior remains unproven.
- Exact source identity remains unproven because no matching tracked Stuart source implementation body was found for this wave.
- Exact `CDXEngine`, `CEngine`, device, mesh, texture, patch-manager, and world-physics node layouts remain unproven beyond the observed fields documented in the read-back notes.
- The debug-volume overlay row at `0x0053d760` was not mutated in this wave.
- BEA patching, gameplay behavior, and rebuild parity remain unproven.
