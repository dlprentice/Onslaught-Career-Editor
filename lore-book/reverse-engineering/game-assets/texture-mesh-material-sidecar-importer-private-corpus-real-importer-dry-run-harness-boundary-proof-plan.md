# Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Boundary Proof Plan

Status: complete public-safe harness boundary, not real importer execution
Date: 2026-06-15
Scope: `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary-proof-plan`

This proof consumes only the tracked public-safe real-importer dry-run readiness-gate proof and defines the boundary for a later real-importer dry-run harness checklist. It does not execute the real/private importer, read private asset content, consume raw private manifest rows, publish private paths or filenames, generate assets, launch BEA, mutate Ghidra, mutate the installed game or original executable, start Godot work, wire product UI, implement a renderer, implement a rebuild, or claim parity.

Evidence anchors:

- `privateCorpusRealImporterDryRunHarnessBoundaryStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary-defined-public-safe-boundary-only-not-real-importer-execution`
- `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary-proof-plan.v1.json`
- `tools/texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_boundary.py`
- `previousSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Readiness Gate Proof Plan`
- `previousScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-readiness-gate-proof-plan`
- `selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Checklist Population Proof Plan`
- `selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-population-proof-plan`
- `sourceRealImporterReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-readiness-gate-complete-public-safe-readiness-only-not-real-importer-execution`
- `sourceProofCount=22`

Harness boundary contract:

- `privateCorpusRealImporterDryRunHarnessBoundaryOnly=true`
- `realImporterReadinessGateProofConsumed=true`
- `realImporterReadinessGateProofContinuityValidated=true`
- `realImporterReadinessRowsConsumedByHarnessBoundary=true`
- `realImporterDryRunHarnessBoundaryDefined=true`
- `harnessBoundaryInputClassesDefined=true`
- `harnessBoundaryOutputClassesDefined=true`
- `harnessBoundaryStopConditionsDefined=true`
- `harnessBoundaryRefusalGuardsValidated=true`
- `harnessBoundaryArchiveClassOrderValidated=true`
- `harnessBoundaryArchiveClassCountsValidated=true`
- `harnessBoundaryInterfacesValidated=true`
- `harnessBoundaryEmitsOnlyPublicSafeRows=true`
- `harnessChecklistPopulationLaneSelected=true`
- `realImporterHarnessBoundaryInputMode=tracked-public-safe-real-importer-readiness-gate-proof-json`
- `realImporterHarnessBoundaryOutputMode=public-safe-harness-boundary-class-count-status-token-rows`
- `selectedNextLaneClass=private-corpus real importer dry-run harness checklist population without execution`

Counts:

| Metric | Value |
| --- | ---: |
| `sourceRealImporterReadinessInterfaceCount` | 8 |
| `realImporterDryRunHarnessBoundaryInterfaceCount` | 10 |
| `realImporterReadinessRowsConsumed` | 5 |
| `harnessBoundaryRows` | 5 |
| `harnessBoundaryArchiveClassRows` | 5 |
| `harnessBoundarySummaryRows` | 1 |
| `consumerArchiveTotalCount` | 301 |
| `baseArchiveClassCount` | 1 |
| `frontendArchiveClassCount` | 1 |
| `loadingArchiveClassCount` | 1 |
| `numericLevelArchiveClassCount` | 66 |
| `goodieArchiveClassCount` | 232 |
| `unknownAyaArchiveClassCount` | 0 |
| `harnessAllowedFutureInputClassCount` | 5 |
| `harnessRequiredFutureArtifactClassCount` | 6 |
| `harnessStopConditionCount` | 12 |
| `publicSafeHarnessBoundaryArtifactRows` | 1 |
| `publicAllowedOutputCount` | 33 |
| `redactedFieldCount` | 28 |
| `falseGuardCount` | 85 |
| `zeroCounterCount` | 69 |

Probe count anchors: `sourceRealImporterReadinessInterfaceCount=8`; `realImporterDryRunHarnessBoundaryInterfaceCount=10`; `realImporterReadinessRowsConsumed=5`; `harnessBoundaryRows=5`; `harnessBoundaryArchiveClassRows=5`; `harnessBoundarySummaryRows=1`; `consumerArchiveTotalCount=301`; `harnessAllowedFutureInputClassCount=5`; `harnessRequiredFutureArtifactClassCount=6`; `harnessStopConditionCount=12`; `publicSafeHarnessBoundaryArtifactRows=1`; `publicAllowedOutputCount=33`; `redactedFieldCount=28`; `falseGuardCount=85`; `zeroCounterCount=69`.

Allowed later input classes:

- `read-only-corpus-root-handle`
- `tracked-public-safe-redacted-manifest`
- `public-safe-archive-class-count-rows`
- `app-owned-private-evidence-root`
- `app-owned-importer-dry-run-output-root`

Required later artifact classes:

- `private-dry-run-command-manifest`
- `private-dry-run-input-manifest`
- `private-dry-run-output-inventory`
- `private-dry-run-log-inventory`
- `private-leak-scan-report`
- `public-safe-result-summary`

Stop conditions:

- `installed-game-or-original-executable-would-be-mutated`
- `raw-private-paths-or-filenames-would-enter-public-scope`
- `private-asset-content-read-outside-later-armed-harness`
- `raw-private-manifest-rows-would-be-published`
- `real-importer-output-escapes-app-owned-artifact-root`
- `dry-run-would-generate-assets-without-output-inventory`
- `importer-would-launch-bea-or-require-runtime-game-state`
- `ghidra-mutation-would-be-needed`
- `godot-ui-renderer-or-rebuild-work-would-be-needed`
- `archive-class-order-or-counts-mismatch-readiness-contract`
- `unknown-archive-class-appears`
- `raw-hashes-byte-lengths-or-private-refs-would-enter-public-scope`

Boundary counters:

- `privateAssetContentRead=false`
- `privateArchiveBytesRead=false`
- `rawPrivateManifestConsumed=false`
- `rawPrivateManifestRowsConsumed=false`
- `realImporterImplementation=false`
- `realImporterExecuted=false`
- `privateImporterDryRunExecuted=false`
- `realImporterDryRunExecuted=false`
- `realImporterDryRunHarnessExecuted=false`
- `realImporterDryRunHarnessArmed=false`
- `realImporterDryRunHarnessExecutedInBoundarySlice=false`
- `realImporterDryRunHarnessOutputPublished=false`
- `realImporterDryRunHarnessBoundaryReadPrivateInputs=false`
- `realImporterDryRunHarnessBoundaryPublishedPrivateInput=false`
- `privateHarnessBoundaryArtifactPublished=false`
- `harnessChecklistPopulationExecuted=false`
- `harnessChecklistMaterialized=false`
- `actualAssetImportRows=0`
- `generatedAssetRows=0`
- `generatedDryRunOutputRows=0`
- `outputArtifactRows=0`
- `rawPathRows=0`
- `rawFilenameRows=0`
- `rawHashRows=0`
- `byteLengthRows=0`
- `rawTextureRefRows=0`
- `rawMeshRefRows=0`
- `realImporterDryRunRows=0`
- `realImporterDryRunHarnessRows=0`
- `realImporterDryRunHarnessOutputRows=0`
- `realImporterDryRunHarnessTraceRows=0`
- `harnessChecklistRows=0`
- `publicLeakCheck=PASS`

What this proves:

- The tracked real-importer readiness-gate proof can support a public-safe dry-run harness boundary.
- The boundary defines later allowed input classes, required private artifact classes, and stop conditions.
- The boundary preserves archive class order and aggregate count `301`.
- The selected next lane is a harness checklist population proof without executing the real/private importer.

What remains unproven:

- Private asset content parsing.
- Raw private manifest consumption.
- Real importer implementation or execution.
- Private importer dry run or real importer dry run.
- Real importer dry-run harness execution.
- Harness checklist population.
- Actual asset import or generated asset outputs.
- Runtime resource/archive/texture/mesh behavior.
- Material visual correctness, shader parity, Godot parity, rebuild parity, or no-noticeable-difference parity.
