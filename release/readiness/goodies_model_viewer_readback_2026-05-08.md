# Goodies Model Viewer Read-Back - 2026-05-08

## Scope

This pass added a public-safe read-only verifier for the Goodies model-viewer path. It consumes existing ignored Ghidra decompile exports plus Stuart's source files, and checks that source mesh-viewer behavior lines up with the current retail decompile exports for mesh deserialization and mesh interaction/update branches.

The probe does not launch Ghidra, launch BEA, patch saves, read or write `BEA.exe`, mutate a Ghidra project, extract assets, or commit raw generated output.

Raw generated JSON remains ignored/private under:

```text
subagents/goodies-model-viewer-readback/current/goodies-model-viewer-readback.json
```

## Command

```powershell
npm run test:goodies-model-viewer-readback
```

Result: PASS

Important output:

```text
Goodies model-viewer read-back probe
Status: pass
Files: 7/7
- PASS: source mesh deserialization branch
- PASS: source mesh interaction controls
- PASS: source mesh renderer path
- PASS: source field anchors
- PASS: retail mesh deserialization branch
- PASS: retail mesh interaction controls
- PASS: retail mesh update branch
```

## Public-Safe Summary

The verifier guards the source model-viewer path for:

- mesh-type Goodie deserialization,
- `CMESH` deserialization into the current Goodie mesh field,
- model interaction controls,
- manual-control toggle,
- mesh-distance clamp behavior,
- render-mode switches and `CMESHRENDERER::RenderMesh` source calls.

It also checks the existing retail decompile exports for:

- the `CFEPGoodies__Deserialise` mesh branch,
- current mesh pointer assignment,
- mesh refcount increment,
- `CFEPGoodies__ButtonPressed` mesh-control branch keyed by bucket value `1`,
- manual-control toggle state,
- mesh-distance adjustment/clamp path, and
- `CFEPGoodies__Process` mesh update branch keyed by bucket value `1`.

## What This Proves

- The source model-viewer path is not only a catalog classification: it has source-level mesh deserialization, input/update, and render behavior.
- Existing retail Ghidra read-back contains the model-viewer mesh deserialization branch and mesh interaction/update branches.
- The current static model-viewer evidence now has a machine-checkable source-to-retail read-back guard in addition to the prior source/resource/catalog 45-row alignment.

## What This Does Not Prove

- It does not prove runtime in-game model-viewer playback in the Steam build.
- It does not prove final native WinUI textured/material/animated 3D rendering.
- It does not prove camera, lighting, skeleton, animation, or material parity with the retail model viewer.
- It does not permit committing extracted models, textures, raw catalogs, screenshots, frames, private decompile output, or proof JSON.

## Follow-Up

Use this guard before a future native textured model-viewer product slice or copied-profile runtime Goodies model-viewer proof. The next product gap remains a real native textured/material viewer or an explicit external-viewer handoff. The next runtime gap is proving representative in-game model-viewer behavior from a copied profile.
