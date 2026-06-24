# Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Boundary Proof Plan

Status: complete public-safe harness boundary, not real importer execution
Date: 2026-06-15
Scope: `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary-proof-plan`

This readiness note records a public-safe harness boundary over the tracked real-importer readiness-gate proof. It defines allowed later input classes, required private artifact classes, and stop conditions for a later checklist-population lane; it does not execute the real/private importer or read private asset content.

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

Boundary result:

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

Counts: `sourceRealImporterReadinessInterfaceCount=8`; `realImporterDryRunHarnessBoundaryInterfaceCount=10`; `realImporterReadinessRowsConsumed=5`; `harnessBoundaryRows=5`; `harnessBoundaryArchiveClassRows=5`; `harnessBoundarySummaryRows=1`; `consumerArchiveTotalCount=301`; `harnessAllowedFutureInputClassCount=5`; `harnessRequiredFutureArtifactClassCount=6`; `harnessStopConditionCount=12`; `publicSafeHarnessBoundaryArtifactRows=1`; `publicAllowedOutputCount=33`; `redactedFieldCount=28`; `falseGuardCount=85`; `zeroCounterCount=69`.

Boundary tokens: `privateAssetContentRead=false`; `privateArchiveBytesRead=false`; `rawPrivateManifestConsumed=false`; `rawPrivateManifestRowsConsumed=false`; `realImporterImplementation=false`; `realImporterExecuted=false`; `privateImporterDryRunExecuted=false`; `realImporterDryRunExecuted=false`; `realImporterDryRunHarnessExecuted=false`; `realImporterDryRunHarnessArmed=false`; `realImporterDryRunHarnessExecutedInBoundarySlice=false`; `realImporterDryRunHarnessOutputPublished=false`; `realImporterDryRunHarnessBoundaryReadPrivateInputs=false`; `realImporterDryRunHarnessBoundaryPublishedPrivateInput=false`; `privateHarnessBoundaryArtifactPublished=false`; `harnessChecklistPopulationExecuted=false`; `harnessChecklistMaterialized=false`; `actualAssetImportRows=0`; `generatedAssetRows=0`; `generatedDryRunOutputRows=0`; `outputArtifactRows=0`; `rawPathRows=0`; `rawFilenameRows=0`; `rawHashRows=0`; `byteLengthRows=0`; `rawTextureRefRows=0`; `rawMeshRefRows=0`; `realImporterDryRunRows=0`; `realImporterDryRunHarnessRows=0`; `realImporterDryRunHarnessOutputRows=0`; `realImporterDryRunHarnessTraceRows=0`; `harnessChecklistRows=0`; `publicLeakCheck=PASS`.

Allowed later input classes: `read-only-corpus-root-handle`; `tracked-public-safe-redacted-manifest`; `public-safe-archive-class-count-rows`; `app-owned-private-evidence-root`; `app-owned-importer-dry-run-output-root`.

Required later artifact classes: `private-dry-run-command-manifest`; `private-dry-run-input-manifest`; `private-dry-run-output-inventory`; `private-dry-run-log-inventory`; `private-leak-scan-report`; `public-safe-result-summary`.

Stop conditions include installed-title/original-executable mutation, raw private path publication, unarmed private asset reads, raw private manifest publication, output escaping app-owned roots, asset generation without inventory, BEA launch/runtime dependency, Ghidra mutation, Godot/UI/renderer/rebuild dependency, archive class/count mismatch, unknown archive class, and raw hash/byte-length/private-ref publication.

What remains unproven: private asset parsing, raw private manifest consumption, real importer implementation/execution, private or real importer dry run, real-importer harness execution, harness checklist population, actual asset import, generated asset output, runtime parser behavior, texture pixels, mesh loading/skinning, Direct3D/GPU behavior, material visual correctness, Godot, product UI, renderer, rebuild parity, and no-noticeable-difference parity.
