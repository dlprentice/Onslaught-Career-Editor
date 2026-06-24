# Ghidra MeshRenderer Core Wave866 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `meshrenderer-core-wave866`

Wave866 mesh renderer core saved the comment, tags, and 12-argument `void __cdecl CMeshRenderer__RenderMeshCore(float world_position_x, float world_position_y, float world_position_z, float world_position_w, float * transform_matrix12, void * mesh_part, void * render_context, void * effect_owner, int render_slot_or_mode, int render_flags, int reserved_zero, void * world_position_vec4)` signature for `0x00549570 CMeshRenderer__RenderMeshCore`. The pass made no rename, no function-boundary change, and no executable-byte change.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00549570 CMeshRenderer__RenderMeshCore` | Single observed caller `0x004b6a82 CMeshRenderer__RenderMesh`; caller pushes a copied four-dword world-position payload, `transform_matrix12`, `mesh_part`, `render_context`, `effect_owner`, `render_slot_or_mode`, `render_flags`, an observed zero slot, and `world_position_vec4`, then cleans `0x30` bytes. |
| `0x00549570 CMeshRenderer__RenderMeshCore` | Body uses a `0x1e54-byte stack frame`, reads `mesh_part+0x8c` for mesh-type dispatch, handles animated pose/interpolation evidence through `CMCMech__BuildInterpolatedPoseAndAnchor`, emits `CVBufTexture` vertices/indices/batch renders, and calls `CMeshRenderer__RenderMeshWithLayerPasses` at `0x0054a4b6` and `0x0054b265`. |

Read-back evidence:

- `ApplyMeshRendererCoreWave866.java dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyMeshRendererCoreWave866.java apply`: `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyMeshRendererCoreWave866.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 1 xref row, 2093 instruction rows, and 1 decompile row.
- Queue after Wave866: 6105 total, 5820 commented, 285 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5820/6105 = 95.33%`, strict clean-signature proxy `5820/6105 = 95.33%`.
- Next raw commentless row: `0x005501d0 CVBufTexture__GetVertexWriteCursorPlusOne`.
- Verified backup: `G:\GhidraBackups\BEA_20260525-162911_post_wave866_meshrenderer_core_verified`, 19 files, 172329863 bytes, `DiffCount=0`.

What this proves:

- The target function exists in the saved Ghidra project.
- The saved signature is caller-shape bounded to the observed `0x30` caller-cleaned stack payload.
- The saved comment and tags include `meshrenderer-core-wave866`, `wave866-readback-verified`, and `important-connective-infrastructure`.
- This is high-importance connective renderer infrastructure, not low-importance code.

What remains unproven:

- Exact renderer, mesh, pose, and material layouts.
- Exact source identity.
- Visual/runtime rendering behavior.
- BEA patching behavior.
- Rebuild parity.
