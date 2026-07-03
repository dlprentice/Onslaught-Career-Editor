# Render Resource Bridge Static Contract

Status: source/static public-safe bridge contract, not runtime or visual proof
Last updated: 2026-07-03
Scope: `render-resource-bridge-static-contract`

This contract answers one bounded question from the rebuild front-door map:
how should the tracked AYA loader vocabulary for `MESH` and `TEXT` be routed
into the renderer/material/mesh static docs before any GPU, visual, importer,
or rebuild claim?

Current answer: use `MESH` and `TEXT` only as bridge vocabulary between the
AYA loader contract and existing renderer/decode static contracts. The current
proof class is Tier C source engine architecture plus Tier B retail/static
renderer and texture decode documentation. Runtime GPU behavior, texture
pixels, animation, shader/material visual semantics, generated asset output,
and rebuild parity require higher-authority proof.

## Evidence Class

| Tier | Current use in this contract | Boundary |
| --- | --- | --- |
| Tier C source engine architecture | Names the DirectX 8 render pipeline, runtime-only engine state, and split renderer ownership from tracked source docs. | Architecture vocabulary only; not shipped behavior or output proof by itself. |
| Tier B retail/static render and decode docs | Routes `MESH` and `TEXT` into tracked static mesh, texture, DXMeshVB, DXTexture, and render-queue documentation. | Static handoff context only; not GPU upload, pixel, material, animation, shader, or visual proof. |
| Tier A runtime/GPU/visual proof | Not used in this slice. | Device behavior, rendered frames, texture pixels, animation/skinning, material appearance, and no-noticeable visual parity need separate authorization and evidence. |

## Public Anchors

| Anchor | Current boundary used here |
| --- | --- |
| [aya-resource-tag-family-static-contract.md](/reverse-engineering/game-assets/aya-resource-tag-family-static-contract.md) | Keeps `MESH` and `TEXT` as loader-contract vocabulary only. |
| [engine-system.md](/reverse-engineering/source-code/core/engine-system.md) | Names the DirectX 8 render pipeline and keeps rendering state runtime-only. |
| [mesh-resource-render-static-contract.md](/reverse-engineering/binary-analysis/mesh-resource-render-static-contract.md) | Provides the static mesh/resource/render subsystem map and its non-claims. |
| [texture-resource-decode-static-contract.md](/reverse-engineering/binary-analysis/texture-resource-decode-static-contract.md) | Provides the static texture/resource/decode map and its non-claims. |
| [DXMeshVB.cpp/_index.md](/reverse-engineering/binary-analysis/functions/DXMeshVB.cpp/_index.md) | Tracks static DirectX mesh vertex/index buffer and renderer row evidence. |
| [DXTexture.cpp/_index.md](/reverse-engineering/binary-analysis/functions/DXTexture.cpp/_index.md) | Tracks static DirectX texture load/decode/deserialization row evidence. |
| [rebuild-front-door-chain-map.md](/roadmap/rebuild-front-door-chain-map.md) | Selects this bridge as a bounded renderer/material/mesh side guard. |

## Bridge Table

| Bridge item | Static route allowed | Higher authority still required |
| --- | --- | --- |
| `MESH` loader vocabulary | Route from the AYA tag-family contract into `CMesh`, `CMeshPart`, `CDXMeshVB`, and `CMeshRenderer` static docs as mesh/resource handoff vocabulary. | Exact mesh payload layouts, runtime mesh loading, animation/skinning, collision, GPU buffers, and rendered output. |
| `TEXT` loader vocabulary | Route from the AYA tag-family contract into `CTexture` and `CDXTexture` static docs as texture/resource/decode handoff vocabulary. | Exact per-context text/texture schema, runtime decode pixels, GPU upload behavior, and language/display semantics. |
| Material/texture sidecar metadata | Route to static material/texture-binding rows and sidecar ledgers as importer-contract planning context. | Material visual semantics, shader or fixed-function parity, sidecar completeness, and generated asset equivalence. |
| Render-loop handoff | Route through static `CEngine`, `CDXEngine`, `CRenderQueue`, `CFastVB`, and `CVBufTexture` docs as call-path vocabulary. | Runtime device state, draw ordering as observed on screen, frame captures, visual QA, and no-noticeable visual parity. |

## Allowed Inputs

This checker-backed slice may read only tracked public Markdown and package
metadata. It may validate mirror parity, local links, required bridge rows,
front-door/index registration, package-script registration, and explicit
non-claims.

Allowed source classes:

- tracked source engine architecture docs;
- tracked AYA loader-contract docs;
- tracked retail/static mesh, texture, and render docs;
- tracked front-door/index docs that keep the bridge in a planning scope;
- package metadata for a local public checker.

## Out Of Scope

This slice must not:

- read ignored payload overlays, private assets, raw install manifests, raw
  proof bundles, copied executables, screenshots, frame dumps, auth/session/log
  cache material, or secrets;
- launch BEA, attach CDB, mutate Ghidra, patch an executable, mutate an
  installed game, run an extractor, execute an importer, or generate asset
  payloads;
- claim runtime parser behavior, runtime texture decode behavior, GPU upload,
  texture pixels, runtime mesh loading, animation/skinning, collision, material
  appearance, shader behavior, visual output, gameplay behavior, renderer
  behavior, rebuild parity, runtime parity, or no-noticeable-difference parity;
- add AppCore, WinUI, CLI, Godot, renderer implementation, release, installer,
  packaging, command-arm, or publication support.

## Exit Gate

This planning slice is complete only when:

- this document and its lore-book mirror match byte-for-byte;
- binary-analysis indexes link this contract as a source/static bridge
  contract;
- `roadmap/rebuild-front-door-chain-map.md` links this contract as the renderer
  bridge side guard without changing active rebuild proof scope;
- `tools/render_resource_bridge_static_contract_probe.py --check` passes;
- public documentation, Markdown link, hard-payload, and public-allowlist gates
  pass.

After this exit gate, the next safe action is still a bounded schema,
runtime-readiness, or renderer proof-plan question with its own higher-authority
proof class. No runtime proof, extractor run, importer execution, generated
asset output, renderer implementation, visual claim, product exposure, or
release action is authorized by this contract.
