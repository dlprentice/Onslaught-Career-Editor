# AYA Resource Tag-Family Static Contract

Status: source/static public-safe contract, not runtime parser proof
Last updated: 2026-07-03
Scope: `aya-resource-tag-family-static-contract`

This contract answers one bounded question from the rebuild front-door map:
how should the source and tracked static docs route the AYA resource tag
families `LVLR`, `WRES`, `ERES`, `LNDS`, `PAGE`, `GDIE`, `MESH`, and `TEXT`
before any loader, importer, runtime, or rebuild claim?

Current answer: use the tags as public-safe loader-contract vocabulary only.
The current proof class is Tier C source/file-format documentation plus Tier B
retail/static loader documentation. Corpus counts, exact payload schemas,
runtime parser behavior, generated asset output, importer execution, renderer
behavior, and rebuild parity require higher-authority proof.

## Evidence Class

| Tier | Current use in this contract | Boundary |
| --- | --- | --- |
| Tier C source and file-format docs | Names chunk tags, archive naming families, compression wrappers, and source-side resource vocabulary from tracked docs. | Candidate loader vocabulary only; not shipped behavior by itself. |
| Tier B retail/static loader docs | Records the tracked `CChunkReader` and `CResourceAccumulator` static docs that dispatch tagged chunks in resource-file loading. | Static loader context only; not runtime archive coverage or exact schema proof. |
| Tier A runtime/corpus proof | Not used in this slice. | Counts, private install corpus coverage, runtime parser behavior, and asset output need separate authorization and evidence. |

## Public Anchors

| Anchor | Current boundary used here |
| --- | --- |
| [chunker-system.md](../source-code/io/chunker-system.md) | Defines the chunker format and names the `ResourceAccumulator` tag set, including this contract's eight tags. |
| [aya-asset-format.md](aya-asset-format.md) | Describes the AYA zlib wrapper and nested tagged chunk architecture. |
| [extraction-pipeline.md](extraction-pipeline.md) | Records public-safe extraction workflow posture and existing private-baseline summaries without making this slice a fresh corpus proof. |
| [chunker.cpp/_index.md](../binary-analysis/functions/chunker.cpp/_index.md) | Tracks static `CChunkReader` read/skip/get-next helpers used by resource loaders. |
| [ResourceAccumulator.cpp/_index.md](../binary-analysis/functions/ResourceAccumulator.cpp/_index.md) | Tracks static resource file-name selection and recognized chunk dispatch boundaries. |
| [rebuild-front-door-chain-map.md](/roadmap/rebuild-front-door-chain-map.md) | Selects the AYA tag-family table as a bounded rebuild-support crosswalk item. |

## Tag-Family Table

| Tag | Routing family | Current public-safe use | Higher authority still required |
| --- | --- | --- | --- |
| `LVLR` | Level resource header | Route as level-resource archive vocabulary and a parent container cue. | Exact level header/world-header schema, live load behavior, and runtime mission state. |
| `WRES` | World resources | Route as world-resource loader vocabulary. | Exact `WRLD`/world payload layout, runtime world loading, and rebuild world serialization. |
| `ERES` | Entity resources | Route as entity/resource loader vocabulary. | Exact entity resource schema, object lifetime, spawned runtime behavior, and gameplay semantics. |
| `LNDS` | Landscape | Route as landscape/terrain-resource vocabulary. | Exact landscape page/header schemas, terrain runtime behavior, and visual parity. |
| `PAGE` | Page/UI resources | Route as page or UI resource vocabulary. | Exact page payload schema, frontend runtime presentation, and localization/display behavior. |
| `GDIE` | Goodie data | Route as Goodie/gallery resource vocabulary. | Exact `GDAT` family payload semantics, catalog completeness, runtime Goodie display behavior, and save unlock behavior. |
| `MESH` | Mesh resources | Route as mesh-resource vocabulary and importer-contract input. | Exact mesh payload layouts, animation/skinning, collision, renderer behavior, and generated asset equivalence. |
| `TEXT` | Text/texture-labeled resources | Route as a tagged resource family that existing docs use in text/string and texture-resource contexts. | Exact per-context schema, texture decode fidelity, language semantics, and rendered output. |

## Allowed Inputs

This checker-backed slice may read only tracked public Markdown and package
metadata. It may validate mirror parity, local links, required tag rows,
front-door/index registration, package-script registration, and explicit
non-claims.

Allowed source classes:

- tracked source-code and file-format docs;
- tracked retail/static loader docs;
- tracked product/register docs that keep the contract in a planning scope;
- package metadata for a local public checker.

## Out Of Scope

This slice must not:

- read ignored payload overlays, private assets, raw install manifests, raw
  proof bundles, copied executables, screenshots, frame dumps, auth/session/log
  cache material, or secrets;
- launch BEA, attach CDB, mutate Ghidra, patch an executable, mutate an
  installed game, run an extractor, execute an importer, or generate asset
  payloads;
- claim fresh archive counts, full corpus coverage, exact payload schemas,
  runtime parser behavior, runtime resource loading, visual output, gameplay
  behavior, renderer behavior, rebuild parity, or no-noticeable-difference
  parity;
- add AppCore, WinUI, CLI, release, installer, packaging, command-arm, or
  publication support.

## Exit Gate

This planning slice is complete only when:

- this document and its lore-book mirror match byte-for-byte;
- game-assets indexes link this contract as a source/static planning contract;
- `roadmap/rebuild-front-door-chain-map.md` links this contract as the AYA
  tag-family side guard without changing active rebuild proof scope;
- `tools/aya_resource_tag_family_static_contract_probe.py --check` passes;
- public documentation, Markdown link, hard-payload, and public-allowlist gates
  pass.

After this exit gate, the next safe action is still a bounded schema, corpus,
or retail/static review for one tag family. No runtime proof, extractor run,
importer execution, generated asset output, product exposure, or release action
is authorized by this contract.
