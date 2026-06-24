# Goodies Model Viewer Alignment - 2026-05-08

## Scope

This pass added a public-safe static alignment probe for Goodies model-viewer provenance. It compares Stuart's source-level `GT_MESH` Goodie rules with the installed PC resource archive `GDIE -> GDAT` model/gallery kind set, and with the generated private catalog if that catalog is present.

The probe does not extract assets, launch BEA, patch saves, read or write `BEA.exe`, mutate Ghidra, or commit raw generated output.

Raw generated JSON remains ignored/private under:

```text
subagents/goodies-model-viewer-alignment/current/goodies-model-viewer-alignment.json
```

## Command

```powershell
npm run test:goodies-model-viewer-alignment
```

Result: PASS

Important output:

```text
PASS: wrote subagents/goodies-model-viewer-alignment/current/goodies-model-viewer-alignment.json
Goodies model alignment: source 45, installed GDAT 45, catalog 45
```

## Public-Safe Summary

The source `get_goodie_type_hack` model set is:

- indices `8-57`,
- excluding image rows `12`, `13`, `24`, `33`, `34`, and `35`,
- plus developer/model row `76`.

That yields 45 source model Goodies. The installed resource archive census reports exactly the same 45 indices as `GDAT` kind `1` model/gallery rows. The generated private catalog, when present, also reports the same 45 model Goodies.

The probe also guards source tokens for the model path:

- `get_goodie_type_hack`,
- `GT_MESH` range and developer row,
- `get_goodie_mesh_hack`,
- `CMESH::Deserialize`,
- mesh interaction controls,
- render path through `CMESHRENDERER::RenderMesh`.

## What This Proves

- The 45 model Goodies are not arbitrary sample rows: the source model-viewer rules, installed archive metadata, and generated catalog agree on the same index set.
- The in-game source model-viewer path loads mesh resources, deserializes a `CMESH`, supports manual/auto interaction state, and renders through the frontend mesh-renderer path.
- The current WinUI model Goodies are grounded in real source/resource/catalog alignment.

## What This Does Not Prove

- It does not prove runtime model-viewer playback in the running Steam build.
- It does not prove final native WinUI textured/material/animated 3D rendering.
- It does not prove camera, lighting, skeleton, animation, or material parity with the in-game viewer.
- It does not permit committing extracted models, textures, raw catalogs, screenshots, frames, or private proof JSON.

## Follow-Up

Use this as the static readiness guard before a future model-viewer product slice or copied-profile runtime Goodies model-viewer proof. The next product gap remains a real native textured/material model viewer or a clearly bounded external-viewer handoff; the next runtime gap is proving representative in-game model-viewer behavior from a copied profile.
