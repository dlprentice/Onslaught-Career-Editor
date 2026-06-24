# MeshRenderer Read-Back - 2026-05-08

## Scope

This pass added a public-safe read-only verifier for the retail `CMeshRenderer__RenderMesh` dispatch path. It consumes an existing ignored Ghidra decompile export and checks that the public MeshRenderer function note is still backed by current decompile tokens.

The probe does not launch Ghidra, launch BEA, patch saves, read or write `BEA.exe`, mutate a Ghidra project, extract assets, or commit raw generated output.

Raw generated JSON remains ignored/private under:

```text
subagents/mesh-renderer-readback/current/mesh-renderer-readback.json
```

## Command

```powershell
npm run test:mesh-renderer-readback
```

Result: PASS

Important output:

```text
MeshRenderer read-back probe
Status: pass
Index: PASS
Files: 4/4
- PASS: retail renderer dispatch
- PASS: retail particle attachment state
- PASS: public function index
- PASS: lore function index mirror
```

## Public-Safe Summary

The verifier guards the existing retail decompile export for:

- the `0x004b6350` `CMeshRenderer__RenderMesh` index row,
- normal dispatch through `CMeshRenderer__RenderMeshCore`,
- debug render context,
- particle attachment/update context,
- mesh type-6 redirect through a sub-mesh slot,
- parameter flag gates, and
- default texture fallback through `meshtex_default.tga`.

The same probe also checks that the public function index and lore mirror carry the matching bounded behavior summary.

## What This Proves

- Existing retail Ghidra output contains machine-checkable evidence for the main mesh renderer dispatch function.
- The renderer path has a normal mesh-core dispatch, particle attachment context, debug render context, and default texture fallback context.
- The Goodies model-viewer evidence now has a retail renderer dispatch guard adjacent to the source/resource/catalog and Goodies frontend read-back guards.

## What This Does Not Prove

- It does not prove exact full source parity for `MeshRenderer.cpp`, because that source file is not present in this checkout.
- It does not prove runtime in-game model-viewer playback in the Steam build.
- It does not prove final native WinUI textured/material/animated 3D rendering.
- It does not prove camera, lighting, skeleton, animation, or material parity with the retail model viewer.
- It does not permit committing extracted models, textures, raw catalogs, screenshots, frames, private decompile output, or proof JSON.

## Follow-Up

Use this guard before a native textured model-viewer product slice. A future renderer-focused RE pass can split `CMeshRenderer__RenderMeshCore`, material/layer passes, and texture binding behavior into smaller machine-checkable notes, but runtime Goodies model-viewer proof remains a separate copied-profile task.
