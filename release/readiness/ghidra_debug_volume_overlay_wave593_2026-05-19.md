# Ghidra Debug Volume Overlay Wave593 Readiness Note

Date: 2026-05-19
Status: static saved-Ghidra evidence only

Wave593 hardened the dedicated debug-volume overlay row that Wave592 split out for a separate pass.

Saved row:

| Address | Function |
| --- | --- |
| `0x0053d760` | `CThing__RenderDebugVolumeOverlay` |

What is proven:

- Ghidra now records a clean 16-stack-argument signature, function comment, and `debug-volume-overlay-wave593` tags for `CThing__RenderDebugVolumeOverlay`.
- The saved signature is `void __stdcall CThing__RenderDebugVolumeOverlay(uint color_argb, void * half_extents_vec3, void * center_vec3, float m00, float m01, float m02, float m03_unused, float m10, float m11, float m12, float m13_unused, float m20, float m21, float m22, float m23_unused, void * texture_or_material)`.
- `RET 0x40` and caller setup prove a stack-cleaned debug-volume draw helper shape: color, half-extents vector, center vector, twelve copied transform dwords, and texture/material pointer.
- Named xrefs now include `CDebugMarkers__Render`, `CMapWho__DebugDrawSector`, `CMeshRenderer__RenderMesh`, and two calls from `CThing__DrawDebugCuboid`.
- Callsite read-back shows callers copying twelve transform dwords with `MOVSD.REP`, then pushing center/half-extents pointers, color constants or selected colors, and texture/material pointers before calling the helper.
- Body read-back shows render-state setup for states `0x1b`, `0x13`, and `0x14`, transient `CVBufTexture` setup with FVF `0x152`, vertex stride `0x24`, vertex capacity `0x208`, index setup `0x65/0x208/2`, six face-emission paths, `CVBufTexture__Render`, resource release, and render-state restore for `0x13` and `0x14`.
- Post-save read-back verified 1 metadata row, 1 tag row, 10 xref rows, 1701 instruction rows, 1 target decompile row, 4 caller decompile rows, 490 callsite instruction rows, and 446 proof instruction rows.
- The queue refresh reports `6093` total functions, `3033` commented, `3060` commentless, `1347` exact-undefined signatures, and `1100` `param_N` signatures.
- Comment-backed proxy is `3033/6093 = 49.78%`; strict clean-signature proxy is `2987/6093 = 49.02%`.
- The next high-signal queue head is `0x0053f040 CVBufTexture__SetStateCacheModeByFlag`.
- The live Ghidra project backup verified at `[maintainer-local-ghidra-backup-root]\BEA_20260519-140648_post_wave593_debug_volume_overlay_verified` with 19 files, 160992135 bytes, `DiffCount=0`, and manifest hash `7dee8981c3fdc433ca3d28f7e02c8d1895a6c7a2c616a1355c9dc8f6597b66b9`.

What is not proven:

- Runtime debug-render behavior remains unproven.
- Exact vector, matrix, vertex, `CVBufTexture`, texture/material, `CThing`, debug-marker, map-who, and mesh-renderer layouts remain unproven beyond the observed fields documented in the read-back notes.
- Exact source identity remains unproven because no matching tracked Stuart source implementation body was found for this wave.
- The helper's face/edge visual behavior and all caller-side mode semantics remain unproven.
- BEA patching, gameplay behavior, and rebuild parity remain unproven.
