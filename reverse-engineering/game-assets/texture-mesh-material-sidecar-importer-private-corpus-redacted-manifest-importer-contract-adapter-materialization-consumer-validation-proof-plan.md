# Texture/Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Materialization Consumer Validation Proof Plan

Slice: Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Materialization Consumer Validation Proof Plan
Scope: `texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-consumer-validation-proof-plan`
Status: complete public-safe materialized adapter consumer validation, not real importer proof
Date: 2026-06-15

This slice validates the already tracked public-safe materialized adapter artifact as a consumer input. It consumes only the tracked adapter materialization proof JSON and emits a consumer-validation proof with class/count/status-token rows.

Result artifact: [texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-consumer-validation-proof-plan.v1.json](texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-consumer-validation-proof-plan.v1.json)

Implementation: [`tools/texture_mesh_material_sidecar_importer_private_corpus_redacted_manifest_importer_contract_adapter_materialization_consumer_validation.py`](../../tools/texture_mesh_material_sidecar_importer_private_corpus_redacted_manifest_importer_contract_adapter_materialization_consumer_validation.py)

Continuity:

- Previous slice: Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Materialization Proof Plan
- Previous scope: `texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-proof-plan`
- Next slice: Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Consumer Readiness Gate Proof Plan
- Next scope: `texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-consumer-readiness-gate-proof-plan`

Tracked status tokens:

- `privateCorpusRedactedManifestImporterContractAdapterMaterializationConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-consumer-validation-complete-public-safe-materialized-adapter-artifact-consumed-not-real-importer`
- `sourceMaterializationStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-complete-public-safe-adapter-dry-run-row-artifact-not-real-importer`
- `sourceAdapterDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-dry-run-complete-public-safe-adapter-row-consumption-not-real-importer`
- `sourceAdapterStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-complete-public-safe-adapter-rows-not-real-importer`
- `sourceProofCount=18`

Consumer-validation evidence:

- `redactedManifestImporterContractAdapterMaterializationConsumerValidationOnly=true`
- `materializedAdapterProofConsumed=true`
- `materializedAdapterArtifactConsumed=true`
- `materializedAdapterArtifactContinuityValidated=true`
- `consumerValidationExecuted=true`
- `consumerValidationInputAccepted=true`
- `consumerSchemaValidated=true`
- `consumerRowModeValidated=true`
- `consumerArchiveClassOrderValidated=true`
- `consumerArchiveClassCountsValidated=true`
- `consumerGuardCountersValidated=true`
- `consumerInterfacesValidated=true`
- `consumerValidationEmitsOnlyPublicSafeRows=true`
- `consumerValidationInputMode=tracked-public-safe-materialized-adapter-proof-json`
- `consumerValidationOutputMode=tracked-public-safe-materialized-adapter-consumer-validation-proof`
- `sourceAdapterContractInterfaceCount=7`
- `sourceAdapterDryRunInterfaceCount=8`
- `sourceAdapterMaterializationInterfaceCount=8`
- `consumerValidationInterfaceCount=8`
- `materializedAdapterRowsConsumed=5`
- `consumerValidationRows=5`
- `consumerValidationArchiveClassRows=5`
- `consumerValidationSummaryRows=1`
- `consumerArchiveTotalCount=301`
- `baseArchiveClassCount=1`
- `frontendArchiveClassCount=1`
- `loadingArchiveClassCount=1`
- `numericLevelArchiveClassCount=66`
- `goodieArchiveClassCount=232`
- `unknownAyaArchiveClassCount=0`
- `publicSafeConsumerValidationArtifactRows=1`
- `publicAllowedOutputCount=15`
- `redactedFieldCount=20`
- `falseGuardCount=61`
- `zeroCounterCount=51`
- `publicLeakCheck=PASS`

Negative guards:

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
- `materializedAdapterConsumerValidationReadPrivateInputs=false`
- `materializedAdapterConsumerValidationPublishedPrivateInput=false`
- `materializedAdapterArtifactPathConsumed=false`
- `privateConsumerValidationArtifactPublished=false`
- `installedGameMutationAllowed=false`
- `originalExecutableMutationAllowed=false`
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
- `realImporterMaterializationRows=0`
- `realImporterConsumerValidationRows=0`
- `rawDryRunTraceRows=0`
- `realImporterImplementationRows=0`
- `rebuildImplementationRows=0`

What this proves:

- The selected consumer validation can consume the tracked public-safe materialized adapter artifact.
- The consumer validation input contains only public-safe archive class/count/status-token rows.
- The consumer validation preserves required archive class order and aggregate counts.
- Real importer implementation, real importer execution, private importer dry-run, and raw private manifest consumption remain unperformed.

What remains unproven:

- Private asset content parsing.
- Raw private manifest consumption.
- Real importer implementation or execution.
- Private importer dry run or real importer dry run.
- Actual asset import or generated asset output.
- Runtime resource parser behavior, texture pixels, mesh loading/skinning, Direct3D/GPU behavior, material visual correctness, material/shader parity, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
