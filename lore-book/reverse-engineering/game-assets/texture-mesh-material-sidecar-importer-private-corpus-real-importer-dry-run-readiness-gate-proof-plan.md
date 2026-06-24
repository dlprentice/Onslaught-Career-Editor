# Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Readiness Gate Proof Plan

Status: complete public-safe real-importer dry-run readiness gate, not real importer execution
Date: 2026-06-15
Scope: `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-readiness-gate-proof-plan`

This proof consumes only the tracked public-safe adapter-consumer dry-run proof and evaluates readiness for a later real-importer dry-run harness boundary lane. It does not read private asset bytes, raw private manifest rows, raw private paths, raw filenames/stems, texture refs, mesh refs, hashes, byte lengths, directory listings, ignored artifact paths, or importer stdout/stderr.

Evidence anchors:

- `privateCorpusRealImporterDryRunReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-readiness-gate-complete-public-safe-readiness-only-not-real-importer-execution`
- `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-readiness-gate-proof-plan.v1.json`
- `tools/texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_readiness_gate.py`
- `previousSlice=Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Consumer Dry-Run Proof Plan`
- `previousScope=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-consumer-dry-run-proof-plan`
- `selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Boundary Proof Plan`
- `selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary-proof-plan`
- `sourceAdapterConsumerDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-consumer-dry-run-complete-public-safe-readiness-row-consumption-not-real-importer`
- `sourceConsumerReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-consumer-readiness-gate-complete-public-safe-next-lane-selected-not-real-importer`
- `sourceConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-consumer-validation-complete-public-safe-materialized-adapter-artifact-consumed-not-real-importer`
- `sourceMaterializationStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-complete-public-safe-adapter-dry-run-row-artifact-not-real-importer`
- `sourceAdapterDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-dry-run-complete-public-safe-adapter-row-consumption-not-real-importer`
- `sourceAdapterStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-complete-public-safe-adapter-rows-not-real-importer`
- `sourceProofCount=21`

Readiness contract:

- `privateCorpusRealImporterDryRunReadinessGateOnly=true`
- `adapterConsumerDryRunProofConsumed=true`
- `adapterConsumerDryRunProofContinuityValidated=true`
- `adapterConsumerDryRunRowsConsumedByReadinessGate=true`
- `realImporterDryRunReadinessGateExecuted=true`
- `realImporterReadinessInputAccepted=true`
- `realImporterReadinessArchiveClassOrderValidated=true`
- `realImporterReadinessArchiveClassCountsValidated=true`
- `realImporterReadinessGuardCountersValidated=true`
- `realImporterReadinessInterfacesValidated=true`
- `realImporterDryRunHarnessBoundaryLaneSelected=true`
- `realImporterReadinessEmitsOnlyPublicSafeRows=true`
- `realImporterReadinessInputMode=tracked-public-safe-adapter-consumer-dry-run-proof-json`
- `realImporterReadinessOutputMode=public-safe-real-importer-readiness-gate-class-count-status-token-rows`
- `selectedNextLaneClass=private-corpus real importer dry-run harness boundary without execution`

Counts:

| Metric | Value |
| --- | ---: |
| `sourceAdapterContractInterfaceCount` | 7 |
| `sourceAdapterDryRunInterfaceCount` | 8 |
| `sourceAdapterMaterializationInterfaceCount` | 8 |
| `sourceConsumerValidationInterfaceCount` | 8 |
| `sourceConsumerReadinessInterfaceCount` | 8 |
| `sourceAdapterConsumerDryRunInterfaceCount` | 8 |
| `realImporterDryRunReadinessInterfaceCount` | 8 |
| `adapterConsumerDryRunRowsConsumed` | 5 |
| `realImporterReadinessGateRows` | 5 |
| `realImporterReadinessArchiveClassRows` | 5 |
| `realImporterReadinessSummaryRows` | 1 |
| `consumerArchiveTotalCount` | 301 |
| `baseArchiveClassCount` | 1 |
| `frontendArchiveClassCount` | 1 |
| `loadingArchiveClassCount` | 1 |
| `numericLevelArchiveClassCount` | 66 |
| `goodieArchiveClassCount` | 232 |
| `unknownAyaArchiveClassCount` | 0 |
| `publicSafeRealImporterReadinessArtifactRows` | 1 |
| `publicAllowedOutputCount` | 27 |
| `redactedFieldCount` | 23 |
| `falseGuardCount` | 77 |
| `zeroCounterCount` | 63 |

Probe count anchors: `sourceAdapterContractInterfaceCount=7`; `sourceAdapterDryRunInterfaceCount=8`; `sourceAdapterMaterializationInterfaceCount=8`; `sourceConsumerValidationInterfaceCount=8`; `sourceConsumerReadinessInterfaceCount=8`; `sourceAdapterConsumerDryRunInterfaceCount=8`; `realImporterDryRunReadinessInterfaceCount=8`; `adapterConsumerDryRunRowsConsumed=5`; `realImporterReadinessGateRows=5`; `realImporterReadinessArchiveClassRows=5`; `realImporterReadinessSummaryRows=1`; `consumerArchiveTotalCount=301`; `publicSafeRealImporterReadinessArtifactRows=1`; `publicAllowedOutputCount=27`; `redactedFieldCount=23`; `falseGuardCount=77`; `zeroCounterCount=63`.

Boundary counters:

- `privateAssetContentRead=false`
- `privateArchiveBytesRead=false`
- `privateManifestMaterialized=false`
- `privateRawManifestMaterialized=false`
- `privateRawManifestRowsObserved=false`
- `privateManifestRowsPublished=false`
- `rawPrivateManifestConsumed=false`
- `rawPrivateManifestRowsConsumed=false`
- `redactedPrivateManifestArtifactPathPublished=false`
- `ignoredArtifactPathPublished=false`
- `realImporterImplementation=false`
- `realImporterExecuted=false`
- `privateImporterDryRunExecuted=false`
- `realImporterDryRunExecuted=false`
- `privateImporterMaterializationExecuted=false`
- `realImporterMaterializationExecuted=false`
- `realImporterConsumerValidationExecuted=false`
- `realImporterConsumerReadinessExecuted=false`
- `realImporterConsumerDryRunExecuted=false`
- `adapterConsumerDryRunReadPrivateInputs=false`
- `adapterConsumerDryRunPublishedPrivateInput=false`
- `privateAdapterConsumerDryRunArtifactPublished=false`
- `rawAdapterConsumerDryRunTracePublished=false`
- `realImporterDryRunReadinessGateReadPrivateInputs=false`
- `realImporterDryRunReadinessGatePublishedPrivateInput=false`
- `privateRealImporterReadinessArtifactPublished=false`
- `realImporterDryRunHarnessExecuted=false`
- `realImporterDryRunHarnessMaterialized=false`
- `realImporterDryRunBoundaryBypassed=false`
- `actualAssetImportExecuted=false`
- `generatedAssetOutputExecuted=false`
- `installedGameMutationAllowed=false`
- `originalExecutableMutationAllowed=false`

Zero counters:

- `rawPathRows=0`
- `rawFilenameRows=0`
- `rawStemRows=0`
- `rawHashRows=0`
- `byteLengthRows=0`
- `rawTextureRefRows=0`
- `rawMeshRefRows=0`
- `actualAssetImportRows=0`
- `generatedAssetRows=0`
- `outputArtifactRows=0`
- `privateArtifactRows=0`
- `privateDryRunRows=0`
- `realImporterDryRunRows=0`
- `realImporterConsumerDryRunRows=0`
- `realImporterDryRunHarnessRows=0`
- `realImporterDryRunBoundaryBypassRows=0`
- `rawDryRunTraceRows=0`
- `rawAdapterConsumerDryRunTraceRows=0`
- `realImporterImplementationRows=0`
- `rebuildImplementationRows=0`
- `publicLeakCheck=PASS`

What this proves:

- The tracked public-safe adapter-consumer dry-run proof can be consumed by a real-importer dry-run readiness gate.
- The readiness gate preserves the five archive class/count/status-token rows and aggregate count `301`.
- The selected next lane is a harness-boundary proof, not direct private importer execution.

What remains unproven:

- Private asset content parsing.
- Raw private manifest consumption.
- Real importer implementation or execution.
- Private importer dry run or real importer dry run.
- Real importer dry-run harness execution.
- Actual asset import or generated asset outputs.
- Runtime resource/archive/texture/mesh behavior.
- Material visual correctness, shader parity, Godot parity, rebuild parity, or no-noticeable-difference parity.
