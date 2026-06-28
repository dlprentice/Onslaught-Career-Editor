# Rebuild Front-Door Chain Map

Status: active routing map
Last updated: 2026-06-28

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

## Short Proof Aliases

Use these aliases in reports and future worker prompts when the full proof-slice
names are too long.

| Alias | Canonical file | Meaning |
| --- | --- | --- |
| `static-measurement` | [static-reaudit-measurement-register.md](../reverse-engineering/binary-analysis/static-reaudit-measurement-register.md) | Active static percentage front door. |
| `static-map` | [mapped-systems.md](../reverse-engineering/binary-analysis/mapped-systems.md) | Implementation-facing static system map front door. |
| `static-to-proof-backlog` | [static-to-proof-rebuild-transition-backlog.md](static-to-proof-rebuild-transition-backlog.md) | Active proof queue and selected scope. |
| `tmm-contract-extension` | [texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.md](../reverse-engineering/game-assets/texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.md) | Texture/mesh/material sidecar rebuild contract extension. |
| `tmm-fixture-matrix` | [texture-mesh-material-sidecar-rebuild-fixture-matrix-proof.md](../reverse-engineering/game-assets/texture-mesh-material-sidecar-rebuild-fixture-matrix-proof.md) | Public-safe fixture matrix proof. |
| `tmm-fixture-harness` | [texture-mesh-material-sidecar-importer-fixture-harness-proof-plan.md](../reverse-engineering/game-assets/texture-mesh-material-sidecar-importer-fixture-harness-proof-plan.md) | Fixture harness proof plan. |
| `tmm-fixture-harness-materialize` | [texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan.md](../reverse-engineering/game-assets/texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan.md) | Fixture harness materialization proof plan. |
| `tmm-fixture-harness-consumer-dryrun` | [texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan.md](../reverse-engineering/game-assets/texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan.md) | Fixture harness consumer dry-run proof plan. |
| `tmm-implementation-readiness` | [texture-mesh-material-sidecar-importer-implementation-readiness-gate-proof-plan.md](../reverse-engineering/game-assets/texture-mesh-material-sidecar-importer-implementation-readiness-gate-proof-plan.md) | Public-safe importer implementation readiness gate. |
| `tmm-private-inventory-preflight` | [texture-mesh-material-sidecar-importer-private-corpus-read-only-inventory-preflight-proof-plan.md](../reverse-engineering/game-assets/texture-mesh-material-sidecar-importer-private-corpus-read-only-inventory-preflight-proof-plan.md) | Redacted private-corpus inventory preflight. |
| `tmm-arm4-validation` | [texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-validation-proof.md](../reverse-engineering/game-assets/texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-validation-proof.md) | Latest completed public-safe command arm-checklist validation proof. |
| `tmm-arm4-readiness-gate` | Selected next scope in [static-to-proof-rebuild-transition-backlog.md](static-to-proof-rebuild-transition-backlog.md) | Current active selected slice; proof file is not materialized yet. |

## Current Active Scope

The selected active static-to-proof slice is:

- Alias: `tmm-arm4-readiness-gate`
- Full slice: `Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Checklist Readiness Gate Proof Plan`
- Scope token: `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-checklist-readiness-gate-proof-plan`
- Source evidence: completed `tmm-arm4-validation`
- Current status: selected next scope; not yet a completed proof file

The next safe rebuild-support artifact is therefore a public-safe
`tmm-arm4-readiness-gate` proof plan/artifact slot that consumes the completed
validation rows and keeps command arming, shell dispatch, importer execution,
private asset reads, generated asset output, BEA launch, Ghidra mutation,
runtime proof, rebuild parity, and no-noticeable-difference claims out of
scope.
