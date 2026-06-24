# Dynamic Unit Render Read-Back - 2026-05-08

## Scope

This pass added a public-safe read-only verifier for the retail dynamic unit render pass currently exported as `CVBufTexture__RenderDynamicUnitPass` at `0x00476fe0`. It consumes an existing ignored Ghidra decompile export and checks that the public `vbuftexture.cpp` function note is still backed by current decompile tokens.

The probe does not launch Ghidra, launch BEA, patch saves, read or write `BEA.exe`, mutate a Ghidra project, extract assets, or commit raw generated output.

Raw generated JSON remains ignored/private under:

```text
subagents/dynamic-unit-render-readback/current/dynamic-unit-render-readback.json
```

## Command

```powershell
npm run test:dynamic-unit-render-readback
```

Result: PASS

Important output:

```text
Dynamic unit render read-back probe
Status: pass
Files: 5/5
- PASS: retail dynamic unit render pass
- PASS: retail visibility and LOD gates
- PASS: retail collision-map owner traversal
- PASS: public vbuftexture index
- PASS: lore vbuftexture index mirror
```

## Public-Safe Summary

The verifier guards the existing retail decompile export for:

- the `0x00476fe0` `CVBufTexture__RenderDynamicUnitPass` export header,
- unit-list traversal through the current global unit list,
- collision-map owner traversal,
- dynamic texture-transform helper calls,
- projected-sprite path through `CDXEngine__BuildProjectedSprites`,
- sorted render insertion through `CRenderQueue__InsertSortedByDepth`, and
- distance/LOD gates including `g_MeshQualityDistance` and `g_MeshQualityLodTable`.

The same probe also checks that the public function index and lore mirror carry the matching bounded behavior summary.

## What This Proves

- Existing retail Ghidra output contains machine-checkable evidence for a dynamic unit render pass.
- The pass is connected to visibility/depth filtering, projected sprites, collision-map owner traversal, and sorted render-queue insertion.
- The Goodies/model-viewer evidence now has an adjacent dynamic unit render-path guard in addition to the main `CMeshRenderer__RenderMesh` dispatch guard.

## What This Does Not Prove

- It does not prove exact full source identity for the dynamic unit render pass.
- It does not prove camera, lighting, material, shader, skeleton, animation, or textured-render parity.
- It does not prove runtime in-game model-viewer playback in the Steam build.
- It does not prove final native WinUI textured/material/animated 3D rendering.
- It does not permit committing extracted models, textures, raw catalogs, screenshots, frames, private decompile output, or proof JSON.

## Follow-Up

Use this guard before a native textured model-viewer product slice. A future renderer-focused RE pass can split texture binding, material layers, animation inputs, and render-queue consumers into smaller machine-checkable notes before runtime Goodies model-viewer proof.
