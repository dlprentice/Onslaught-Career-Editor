# Original-System Internal Tooling Vocabulary Map

Status: source-only continuity map; context only, not readiness evidence
Last updated: 2026-07-02

This map records source-indexed internal editor, developer-tool, resource, and
pipeline vocabulary that can help future clean-room planning. It is a context
companion for the current `tmm-arm4-readiness-gate` continuity lane, not a
readiness-gate artifact.

Authority boundary: Steam retail binary, save, and separately documented
runtime evidence outrank Stuart source names, internal-tool references, static
contracts, and asset extraction notes. Source names are candidate vocabulary
only.

This artifact makes no readiness-gate execution or completion claim; no command
arming claim; no importer-execution claim; no private-asset-read claim; no
generated-payload claim; no runtime-proof claim; no Ghidra mutation claim; no
rebuild-parity claim; and no no-noticeable-difference claim. It is not an
instruction to run internal tools, parse private assets, materialize outputs,
launch BEA, attach CDB, mutate a Ghidra project, or patch an executable.

## Use

Use this file as a compact index when deciding what original-system vocabulary
needs higher-authority confirmation before it can inform a clean-room rebuild
contract. Link to the canonical docs for detail instead of copying complete
inventories or tag catalogs here.

## Authority Tiers

| Tier | Evidence class | May support | Must not be used for |
| --- | --- | --- | --- |
| A | Retail binary, save, and separately documented runtime evidence | Behavior, persistence, and runtime truth for the specific proof class documented elsewhere | Claims outside that proof class |
| B | Static RE contracts and function docs | Candidate subsystem ownership, call-path vocabulary, and static contract planning | GPU behavior, exact runtime layouts, visual/material semantics, runtime proof, or parity |
| C | Stuart internal PC source docs and source inventory | Candidate names, build defines, internal tool vocabulary, and source-to-static questions | Retail feature presence, shipping UI flow, complete toolchain reconstruction, or command execution |
| D | Asset extraction and AYA format docs | Chunk/tag vocabulary, public-safe asset-lane shape, and dev-vs-release provenance questions | Real importer execution, generated payload correctness, textured rendering, animation, or no-noticeable-difference |

## Source-Indexed Vocabulary

| Area | Public anchor | Source/internal signal | Candidate clean-room use | Evidence ceiling | Higher authority still required | Still out of scope here |
| --- | --- | --- | --- | --- | --- | --- |
| Internal editor shell | [engine-system.md](core/engine-system.md) | `EditorD3DApp`, `EDITORBUILD`, `EDITORBUILD2`, `DEV_VERSION`, `LT_DEBUG` | Vocabulary for internal D3D8 editor-shell separation and future tool-facing UI boundaries | Tier C source-only context | Retail static or runtime evidence before any Steam-build editor/tool claim | Readiness-gate execution, tool launch, renderer implementation, visual proof, or parity |
| Internal viewer/editor names | [source-code/_index.md](_index.md), [engine-system.md](core/engine-system.md) | Model viewer, cutscene editor, particle editor, and source-only flag names such as `-modelviewer` and `-cutsceneeditor` | Candidate labels for tool families that may need separate public-safe requirements later | Tier C source vocabulary only; flag names are not runnable instructions | Retail flag/static proof and separate command-boundary review before any executable use | Command arming, command arguments, shell traces, tool execution, or retail feature claims |
| Development menu / level selection | [full source parse](full-source-parse-2026-02-11.md), [source-code index](_index.md) | `FEPDevelopment` dev-menu / level-select signal and source/internal cheat/debug vocabulary | Candidate frontend/debug taxonomy that stays separate from user-facing WinUI wording | Tier C unless independently tied to retail binary behavior | Retail UI/static and runtime evidence for any Steam-facing menu behavior | Product UI promotion, Host/Join enablement, runtime gameplay proof, or save-format changes |
| Map/world tooling boundary | [full source parse](full-source-parse-2026-02-11.md), [engine system](core/engine-system.md) | Provided source lacks several world/render bodies while source-path evidence names families such as `world.cpp`, `WorldMeshList.cpp`, `WorldPhysicsManager.cpp`, `LandscapeTexture.cpp`, and `maptex.cpp` | Gap map for later world/resource/schema questions without treating absence as proof | Tier B/C planning context | Retail static docs, asset schemas, and runtime proof before any world-editor or map-pipeline claim | Complete map editor reconstruction, world-header schema completion, generated world payloads, or parity |
| Resource container vocabulary | [chunker-system.md](io/chunker-system.md), [aya-asset-format.md](../game-assets/aya-asset-format.md) | `CChunker`, `CChunkReader`, `ResourceAccumulator`, `MKID`, and chunk tags such as `LVLR`, `WRES`, `ERES`, `LNDS`, `PAGE`, `GDIE`, `MESH`, and `TEXT` | Candidate parser/schema vocabulary for public-safe resource contracts | Tier D/B tag and static context | Structured parser proof and retail/static confirmation for exact layouts and load order | `.bes` save semantics, private asset reads, raw manifests, importer execution, or generated output |
| Mesh/material sidecar vocabulary | [aya-asset-format.md](../game-assets/aya-asset-format.md), [extraction-pipeline.md](../game-assets/extraction-pipeline.md) | Mesh/material tags and rows such as `CMST`, `MSHT`, `TEXB`, `MESP`, `CMSP`, `CMVB`, `MMPT`, `IBUF`, `VBUF`, and `TEXR` | Candidate vocabulary for TMM contract rows and fixture/checker design | Tier D public extraction/format context | Fixture or retail/static proof for exact per-tag contracts before implementation claims | Real importer execution, material visual correctness, animation/skinning, generated payloads, or no-noticeable-difference |
| Dev precompute versus release load posture | [aya-asset-format.md](../game-assets/aya-asset-format.md), [extraction-pipeline.md](../game-assets/extraction-pipeline.md) | Public notes describe development/precompute paths and release/console builds loading saved outputs | Planning prompt to keep generated/precomputed artifacts distinct from runtime resource loading | Tier D provenance only | Separate retail evidence before asserting which path a Steam build uses in a given case | Recreating internal precompute tools, generated runtime assets, importer execution, or rebuild parity |
| Renderer/material static contracts | [mesh-resource-render-static-contract.md](../binary-analysis/mesh-resource-render-static-contract.md), [texture-resource-decode-static-contract.md](../binary-analysis/texture-resource-decode-static-contract.md) | Static mesh/resource/render and texture/decode ownership maps | Candidate subsystem ownership and validation targets for later parser or renderer specs | Tier B static contract only | Runtime and visual proof for Direct3D behavior, GPU upload, material semantics, animation, lighting, and camera output | Runtime proof, native textured rendering, gameplay proof, visual parity, or no-noticeable-difference |
| Career and mission outcome boundary | [career-system.md](gameplay/career-system.md), [game-system.md](gameplay/game-system.md) | `CCareer`, `level_structure`, `EndLevelData`, mission-outcome flow, and retail `.bes` caveats | Keep campaign/save progression evidence separate from the asset/editor pipeline vocabulary | Tier A/C split, depending on the cited save/runtime proof | Retail save/static/runtime evidence for any persistence or UI behavior claim | Asset importer claims, world resource schema completion, runtime gameplay proof, or save layout expansion |

## Scope Firewall

- Internal editor names, build defines, source-only flag names, and developer
  menu names are candidate vocabulary only; they do not prove Steam retail
  feature presence or runtime behavior.
- AYA/resource tags describe asset/resource context only. They do not describe
  `.bes` save format unless a separate save-file proof says so.
- Static renderer/material contracts are planning evidence only. They do not
  prove Direct3D runtime behavior, GPU upload correctness, material visual
  semantics, animation, lighting, camera fidelity, gameplay outcome, rebuild
  parity, runtime parity, visual parity, or no-noticeable-difference.
- Source inventory gaps are gaps in the provided source/docs, not proof that a
  retail system is absent or complete.
- This file must not be used as command-arm checklist evidence, importer
  dry-run evidence, readiness-gate proof evidence, runtime proof evidence, or
  generated-output evidence.

## Next Safe Use

Future public-safe slices can use this vocabulary map to pick one bounded
question, then write a separate proof plan or checker that names its authority
class and explicit non-claims. Any slice that would read private assets, consume
raw private manifests, publish private paths, arm commands, run importers,
launch BEA, attach CDB, mutate Ghidra, write generated payloads, or claim
runtime/rebuild/visual parity needs separate authority and a dedicated proof
contract.
