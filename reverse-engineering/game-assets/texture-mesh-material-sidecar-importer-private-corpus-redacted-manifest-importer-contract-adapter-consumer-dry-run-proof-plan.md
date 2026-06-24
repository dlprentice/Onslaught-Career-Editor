# Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Consumer Dry-Run Proof Plan

Status: complete public-safe adapter-consumer dry run, not real importer proof
Date: 2026-06-15
Scope: `texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-consumer-dry-run-proof-plan`

This proof consumes only the tracked public-safe adapter consumer-readiness gate proof and performs a public-safe adapter-consumer dry run over archive class/count/status-token rows. It does not read private asset bytes, raw private manifest rows, raw private paths, raw filenames/stems, texture refs, mesh refs, hashes, byte lengths, directory listings, ignored artifact paths, or importer stdout/stderr.

Evidence anchors:

- `privateCorpusRedactedManifestImporterContractAdapterConsumerDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-consumer-dry-run-complete-public-safe-readiness-row-consumption-not-real-importer`
- `texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-consumer-dry-run-proof-plan.v1.json`
- `tools/texture_mesh_material_sidecar_importer_private_corpus_redacted_manifest_importer_contract_adapter_consumer_dry_run.py`
- `previousSlice=Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Consumer Readiness Gate Proof Plan`
- `previousScope=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-consumer-readiness-gate-proof-plan`
- `selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Readiness Gate Proof Plan`
- `selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-readiness-gate-proof-plan`
- `sourceConsumerReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-consumer-readiness-gate-complete-public-safe-next-lane-selected-not-real-importer`
- `sourceConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-consumer-validation-complete-public-safe-materialized-adapter-artifact-consumed-not-real-importer`
- `sourceMaterializationStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-complete-public-safe-adapter-dry-run-row-artifact-not-real-importer`
- `sourceAdapterDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-dry-run-complete-public-safe-adapter-row-consumption-not-real-importer`
- `sourceAdapterStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-complete-public-safe-adapter-rows-not-real-importer`
- `sourceProofCount=20`

Dry-run contract:

- `redactedManifestImporterContractAdapterConsumerDryRunOnly=true`
- `consumerReadinessProofConsumed=true`
- `consumerReadinessProofContinuityValidated=true`
- `consumerReadinessGateRowsConsumed=true`
- `adapterConsumerDryRunExecuted=true`
- `adapterConsumerDryRunInputAccepted=true`
- `adapterConsumerDryRunRowsGenerated=true`
- `adapterConsumerDryRunRowsValidated=true`
- `adapterConsumerDryRunAggregateCountsValidated=true`
- `adapterConsumerDryRunInterfacesValidated=true`
- `adapterConsumerDryRunEmitsOnlyPublicSafeRows=true`
- `adapterConsumerDryRunInputMode=tracked-public-safe-adapter-consumer-readiness-gate-proof-json`
- `adapterConsumerDryRunOutputMode=public-safe-adapter-consumer-dry-run-class-count-status-token-rows`
- `selectedNextLaneClass=private-corpus real importer dry-run readiness gate without execution`

Counts:

| Metric | Value |
| --- | ---: |
| `sourceAdapterContractInterfaceCount` | 7 |
| `sourceAdapterDryRunInterfaceCount` | 8 |
| `sourceAdapterMaterializationInterfaceCount` | 8 |
| `sourceConsumerValidationInterfaceCount` | 8 |
| `sourceConsumerReadinessInterfaceCount` | 8 |
| `adapterConsumerDryRunInterfaceCount` | 8 |
| `consumerReadinessRowsConsumed` | 5 |
| `adapterConsumerDryRunRows` | 5 |
| `adapterConsumerDryRunArchiveClassRows` | 5 |
| `adapterConsumerDryRunValidationRows` | 5 |
| `adapterConsumerDryRunSummaryRows` | 1 |
| `consumerArchiveTotalCount` | 301 |
| `baseArchiveClassCount` | 1 |
| `frontendArchiveClassCount` | 1 |
| `loadingArchiveClassCount` | 1 |
| `numericLevelArchiveClassCount` | 66 |
| `goodieArchiveClassCount` | 232 |
| `unknownAyaArchiveClassCount` | 0 |
| `publicSafeAdapterConsumerDryRunSummaryRows` | 1 |
| `publicAllowedOutputCount` | 23 |
| `redactedFieldCount` | 22 |
| `falseGuardCount` | 71 |
| `zeroCounterCount` | 59 |

Probe count anchors: `sourceAdapterContractInterfaceCount=7`; `sourceAdapterDryRunInterfaceCount=8`; `sourceAdapterMaterializationInterfaceCount=8`; `sourceConsumerValidationInterfaceCount=8`; `sourceConsumerReadinessInterfaceCount=8`; `adapterConsumerDryRunInterfaceCount=8`; `consumerReadinessRowsConsumed=5`; `adapterConsumerDryRunRows=5`; `adapterConsumerDryRunArchiveClassRows=5`; `adapterConsumerDryRunValidationRows=5`; `adapterConsumerDryRunSummaryRows=1`; `consumerArchiveTotalCount=301`; `publicSafeAdapterConsumerDryRunSummaryRows=1`; `publicAllowedOutputCount=23`; `redactedFieldCount=22`; `falseGuardCount=71`; `zeroCounterCount=59`.

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
- `rawDryRunTraceRows=0`
- `rawAdapterConsumerDryRunTraceRows=0`
- `realImporterImplementationRows=0`
- `rebuildImplementationRows=0`
- `publicLeakCheck=PASS`

What this proves:

- The adapter-consumer dry run can consume the tracked public-safe consumer-readiness proof rows.
- The dry run preserves required archive class order, aggregate counts, and private-data refusal guards.
- The dry run emits only public-safe class/count/status-token validation rows.
- The next selected lane is a private-corpus real importer dry-run readiness gate without executing the real/private importer.

What this does not prove:

- Private asset content parsing.
- Private raw corpus manifest materialization or row observation.
- Raw private manifest consumption.
- Real importer implementation or execution.
- Private importer dry run or real importer dry run.
- Private importer materialization.
- Actual asset import or generated asset outputs.
- Runtime resource archive parser behavior, runtime texture parser behavior, runtime texture pixels, runtime mesh loading/skinning, Direct3D/GPU behavior, native textured 3D rendering, material visual correctness, material/shader parity, asset format completeness, exact mesh/texture layouts, product UI behavior, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
