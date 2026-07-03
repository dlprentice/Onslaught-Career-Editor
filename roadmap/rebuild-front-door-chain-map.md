# Rebuild Front-Door Chain Map

Status: active routing map
Last updated: 2026-07-01

This is a compact navigation map from static closure to the current
static-to-proof rebuild-support scope. It is not a runtime proof, visual QA
result, patch proof, generated rebuild artifact, or rebuild parity claim.

## Canonical Entry Points

| Question | Current entry point | Use it for |
| --- | --- | --- |
| Where are static closure percentages measured? | [static-reaudit-measurement-register.md](../reverse-engineering/binary-analysis/static-reaudit-measurement-register.md) | Active static measurement authority and validation commands. |
| What is the RE front door? | [RE-INDEX.md](../reverse-engineering/RE-INDEX.md) | Broad RE navigation and historical proof summaries, not active selected-slice authority. |
| What does the app/repo currently claim? | [CURRENT_CAPABILITIES.md](../CURRENT_CAPABILITIES.md) | Product-level current truth and explicit non-claims. |
| What is the active rebuild/spec queue? | [static-to-proof-rebuild-transition-backlog.md](static-to-proof-rebuild-transition-backlog.md) | Selected proof slice, completed proof chain, and next safe scope. |
| Where are asset/rebuild proof files indexed? | [game-assets/_index.md](../reverse-engineering/game-assets/_index.md) | Texture, mesh, material, importer, and asset-sidecar proof summaries. |
| What stays local only? | [LOCAL_LAB_OVERLAY.md](../LOCAL_LAB_OVERLAY.md) | Game files, copied executables, raw proof captures, Ghidra databases, and secrets. |

## Static Closure Anchor

Static closure is measured in
[static-reaudit-measurement-register.md](../reverse-engineering/binary-analysis/static-reaudit-measurement-register.md):

| Track | Current value |
| --- | --- |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Active current-risk focused accounting | `1179/1179 = 100.00%` |
| Remaining active focused work | `0` |

This proves static documentation closure under the current measurement contract
only.

## Separate Proof Classes

| Proof class | Current boundary |
| --- | --- |
| Runtime gameplay behavior | Requires separate live/copied-runtime proof. Static closure does not prove it. |
| Patch behavior | Requires byte-verified copied-target patch evidence. Static closure does not prove it. |
| Visual output / QA | Requires separate visual or native UI/runtime evidence. Static closure does not prove it. |
| Online / multiplayer readiness | Requires accepted distinct-endpoint command-source proof plus source-bound copied-runtime causality. |
| Asset importer / rebuild tooling | Uses public-safe proof plans and redacted/fixture contracts until an explicit later gate allows more. |
| Renderer, Godot, generated rebuild output | Not proven by the current chain. |
| Rebuild parity / no-noticeable-difference parity | Not proven. This remains a later evidence class. |

## Original Game System Crosswalk

This crosswalk is a rebuild-mapping companion, not a new metric authority or
proof gate. It keeps source architecture, Steam retail static evidence, and
asset/corpus evidence separate: source names are candidate owners, while retail
binary, save, and runtime proof remain the higher authority for behavior.

| System | Public anchors | Rebuild implication | Explicit unknowns / next mapping batch |
| --- | --- | --- | --- |
| Campaign/career progression | `reverse-engineering/source-code/gameplay/career-system.md`, `reverse-engineering/source-code/gameplay/game-system.md`, `reverse-engineering/save-file/_index.md`, `reverse-engineering/save-file/career-graph.md`, `reverse-engineering/save-file/career-links.md`, `reverse-engineering/binary-analysis/career-progression-static-bridge-contract.md`, `reverse-engineering/binary-analysis/functions/Career.cpp/_index.md`, `reverse-engineering/binary-analysis/functions/game.cpp/_index.md`, `reverse-engineering/binary-analysis/functions/EndLevelData.cpp/_index.md` | Use `CCareer`, `level_structure`, `CGame`, and `CEndLevelData` names to organize static save, career, and mission-outcome vocabulary, but treat `.bes` true-view offsets and tracked save proofs as the persistence boundary. The campaign/career progression side guard keeps those names as source/static save and career vocabulary only. | Exact retail career UI flow, complete `worldheaders.dat` schema, source-to-retail field identity, runtime save/load behavior, runtime objective UI, runtime mission-outcome persistence, Goodies behavior, gameplay outcomes, and rebuild parity remain open; this side guard does not change the active rebuild proof scope. |
| MissionScript and events | `reverse-engineering/game-assets/msl-scripting.md`, `reverse-engineering/source-code/io/event-system.md`, `reverse-engineering/binary-analysis/functions/Script.cpp/_index.md`, `reverse-engineering/binary-analysis/missionscript-command-effect-fixture-family-completion-rollup-proof-plan.md`, `reverse-engineering/binary-analysis/world-thing-spawn-static-to-rebuild-contract-crosswalk.md` | Keep loose MSL syntax, command descriptors, `IScript` helpers, event scheduling, object references, and slot/goodie/save bridges as separate static contracts before any runtime script claim. | Packed-vs-loose source selection, live command effects, object-code storage, VM layout, timing, and object lifetime remain separate proof. Next batch: summarize descriptor and script-source evidence without execution or private asset reads. |
| AYA resources and file formats | `reverse-engineering/source-code/io/chunker-system.md`, `reverse-engineering/game-assets/aya-asset-format.md`, `reverse-engineering/game-assets/extraction-pipeline.md`, `reverse-engineering/game-assets/aya-resource-tag-family-static-contract.md`, `reverse-engineering/binary-analysis/functions/chunker.cpp/_index.md`, `reverse-engineering/binary-analysis/functions/ResourceAccumulator.cpp/_index.md` | Treat AYA chunk tags, compression wrappers, archive families, language rows, mesh/texture/material sidecars, and parser fixtures as loader-contract inputs, not generated asset output. The AYA tag-family static contract records `LVLR`, `WRES`, `ERES`, `LNDS`, `PAGE`, `GDIE`, `MESH`, and `TEXT` as source/static loader-contract vocabulary only. | Full world-header, landscape/world resource, physics script, particle, material, and per-tag payload schemas remain open. Any later corpus counts, runtime parser behavior, extractor run, importer execution, generated asset output, or rebuild claim needs a separate higher-authority proof; this side guard does not change the active rebuild proof scope. |
| Renderer, material, and mesh path | `reverse-engineering/source-code/core/engine-system.md`, `reverse-engineering/binary-analysis/render-resource-bridge-static-contract.md`, `reverse-engineering/binary-analysis/mesh-resource-render-static-contract.md`, `reverse-engineering/binary-analysis/texture-resource-decode-static-contract.md`, `reverse-engineering/binary-analysis/functions/DXMeshVB.cpp/_index.md`, `reverse-engineering/binary-analysis/functions/DXTexture.cpp/_index.md` | DirectX 8 engine structure, render ordering, mesh/resource ownership, texture decode boundaries, and material sidecar ledgers can guide importer contracts and fixture staging. The render-resource bridge side guard keeps `MESH` and `TEXT` as source/static bridge vocabulary only. | Runtime device behavior, GPU upload behavior, texture pixels, animation/skinning, lighting, material visual semantics, shader parity, renderer implementation, generated output, and no-noticeable visual parity remain unproven; this side guard does not change the active rebuild proof scope. |
| Internal editor and developer hooks | `reverse-engineering/source-code/original-system-internal-tooling-vocabulary-map.md`, `reverse-engineering/source-code/internal-viewer-editor-command-boundary-proof-plan.md`, `reverse-engineering/source-code/core/engine-system.md`, `reverse-engineering/source-code/source-file-inventory.md`, `reverse-engineering/binary-analysis/functions/CLIParams.cpp/_index.md`, `reverse-engineering/binary-analysis/functions/d3dapp.cpp/_index.md`, `reverse-engineering/binary-analysis/windowed-mode-analysis.md` | Source-only tool names such as `EditorD3DApp`, model viewer, cutscene editor, particle editor, developer menus, and source-only flag names are candidate vocabulary only; the linked vocabulary map is context, not readiness-gate evidence. The internal viewer/editor command-boundary proof plan is a bounded internal-tooling side guard, not command authorization, and keeps `-modelviewer` and `-cutsceneeditor` as source/internal vocabulary and blocked product flags. Retail-facing rows stay limited to separately documented CLI/window/capture evidence. | Retail availability, activation behavior, complete editor assets, world editor flow, build/precompute tools, source-vs-retail tool identity, command arming, importer execution, generated payloads, runtime proof, and parity remain unproven. Any later executable use still needs separate retail/static proof, product command-boundary review, and explicit authorization; this side guard does not change the active rebuild proof scope. |
| Missing tooling and source-to-binary bridge | `reverse-engineering/source-code/_index.md`, `roadmap/reverse-engineering/coverage-map.md`, `reverse-engineering/binary-analysis/static-reaudit-measurement-register.md`, `reverse-engineering/binary-analysis/mapped-systems.md`, `roadmap/static-to-proof-rebuild-transition-backlog.md` | Promote a relationship only when source/internal names, retail static anchors, asset/schema contracts, or save/proof docs provide bounded evidence. | Exact source-body identity, ABI/layout equivalence, runtime parser behavior, patch behavior, generated rebuild output, and no-noticeable-difference parity remain outside this crosswalk. Next batch: require source anchor, retail/static anchor, non-claims, and validation gate for each promoted bridge. |

## Short Proof Aliases

Use these aliases in reports and future worker prompts when the full proof-slice
names are too long.

| Alias | Canonical file | Meaning |
| --- | --- | --- |
| `static-measurement` | [static-reaudit-measurement-register.md](../reverse-engineering/binary-analysis/static-reaudit-measurement-register.md) | Active static percentage front door. |
| `static-map` | [mapped-systems.md](../reverse-engineering/binary-analysis/mapped-systems.md) | Implementation-facing static system map front door. |
| `original-system-crosswalk` | [Original Game System Crosswalk](#original-game-system-crosswalk) | Public-safe companion map from original-game source/static/asset evidence to rebuild implications; not a metric authority or proof gate. |
| `aya-tag-family-static-contract` | [aya-resource-tag-family-static-contract.md](../reverse-engineering/game-assets/aya-resource-tag-family-static-contract.md) | Source/static AYA tag-family table for loader-contract vocabulary; not corpus proof, runtime parser proof, generated asset output, importer execution, or release action. |
| `render-resource-bridge-static-contract` | [render-resource-bridge-static-contract.md](../reverse-engineering/binary-analysis/render-resource-bridge-static-contract.md) | Source/static bridge contract for routing `MESH` and `TEXT` into renderer/decode docs; not runtime proof, GPU upload proof, texture pixel proof, importer execution, generated asset output, renderer implementation, visual proof, rebuild parity, or release action. |
| `career-progression-static-bridge-contract` | [career-progression-static-bridge-contract.md](../reverse-engineering/binary-analysis/career-progression-static-bridge-contract.md) | Source/static bridge contract for routing `CCareer`, `level_structure`, `CGame`, and `CEndLevelData` into save/career docs; not runtime save/load proof, runtime mission-outcome proof, runtime objective UI proof, Goodies behavior proof, gameplay proof, rebuild parity, or release action. |
| `internal-viewer-editor-boundary` | [internal-viewer-editor-command-boundary-proof-plan.md](../reverse-engineering/source-code/internal-viewer-editor-command-boundary-proof-plan.md) | Source-only command-boundary plan for internal viewer/editor vocabulary; not command authorization, product exposure, runtime proof, or release action. |
| `static-to-proof-backlog` | [static-to-proof-rebuild-transition-backlog.md](static-to-proof-rebuild-transition-backlog.md) | Active proof queue and selected scope. |
| `tmm-contract-extension` | [texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.md](../reverse-engineering/game-assets/texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.md) | Texture/mesh/material sidecar rebuild contract extension. |
| `tmm-fixture-matrix` | [texture-mesh-material-sidecar-rebuild-fixture-matrix-proof.md](../reverse-engineering/game-assets/texture-mesh-material-sidecar-rebuild-fixture-matrix-proof.md) | Public-safe fixture matrix proof. |
| `tmm-fixture-harness` | [texture-mesh-material-sidecar-importer-fixture-harness-proof-plan.md](../reverse-engineering/game-assets/texture-mesh-material-sidecar-importer-fixture-harness-proof-plan.md) | Fixture harness proof plan. |
| `tmm-fixture-harness-materialize` | [texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan.md](../reverse-engineering/game-assets/texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan.md) | Fixture harness materialization proof plan. |
| `tmm-fixture-harness-consumer-dryrun` | [texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan.md](../reverse-engineering/game-assets/texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan.md) | Fixture harness consumer dry-run proof plan. |
| `tmm-implementation-readiness` | [texture-mesh-material-sidecar-importer-implementation-readiness-gate-proof-plan.md](../reverse-engineering/game-assets/texture-mesh-material-sidecar-importer-implementation-readiness-gate-proof-plan.md) | Public-safe importer implementation readiness gate. |
| `tmm-private-inventory-preflight` | [texture-mesh-material-sidecar-importer-private-corpus-read-only-inventory-preflight-proof-plan.md](../reverse-engineering/game-assets/texture-mesh-material-sidecar-importer-private-corpus-read-only-inventory-preflight-proof-plan.md) | Redacted private-corpus inventory preflight. |
| `tmm-arm4-validation` | [texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-validation-proof.md](../reverse-engineering/game-assets/texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-validation-proof.md) | Latest completed public-safe command arm-checklist validation proof. |
| `tmm-arm4-readiness-gate` | [texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-readiness-gate-proof-plan.md](../reverse-engineering/game-assets/texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-readiness-gate-proof-plan.md) | Current active proof-plan slot; continuity guard only, not readiness-gate execution and not readiness-gate proof completion; no runtime proof, rebuild proof, rebuild parity, or no-noticeable-difference proof. |

## Current Active Scope

The selected active static-to-proof slice is:

- Alias: [`tmm-arm4-readiness-gate`](../reverse-engineering/game-assets/texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-readiness-gate-proof-plan.md)
- Full slice: `Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Checklist Readiness Gate Proof Plan`
- Scope token: `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-checklist-readiness-gate-proof-plan`
- Source evidence: completed `tmm-arm4-validation`, backed by
  `texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-validation-proof.v1.json`
- Current status: proof-plan slot materialized; continuity guard only; not readiness-gate execution; not readiness-gate proof completion
- Non-claims: this slot claims no runtime proof, no rebuild parity, and no no-noticeable-difference proof

The next safe rebuild-support artifact is therefore the public-safe
`tmm-arm4-readiness-gate` proof plan/artifact slot linked above. It consumes the
completed validation rows only as public-safe source evidence and keeps command
arming, shell dispatch, importer execution, private asset reads, generated asset
output, BEA launch, Ghidra mutation, runtime proof, rebuild parity, and
no-noticeable-difference claims out of scope. It claims no runtime proof, no
rebuild parity, and no no-noticeable-difference proof.
