# Texture/Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Materialization Proof Plan

Slice: Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Materialization Proof Plan
Scope: `texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-proof-plan`
Status: complete public-safe adapter materialization, not real importer proof
Date: 2026-06-15

This slice materializes the already tracked public-safe adapter dry-run rows into a tracked proof artifact shape. It consumes only the tracked adapter dry-run proof JSON and embeds a materialized adapter artifact containing class/count/status-token rows.

Result artifact: [texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-proof-plan.v1.json](texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-proof-plan.v1.json)

Implementation: [`tools/texture_mesh_material_sidecar_importer_private_corpus_redacted_manifest_importer_contract_adapter_materialization.py`](../../tools/texture_mesh_material_sidecar_importer_private_corpus_redacted_manifest_importer_contract_adapter_materialization.py)

Continuity:

- Previous slice: Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Dry-Run Proof Plan
- Previous scope: `texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-dry-run-proof-plan`
- Next slice: Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Materialization Consumer Validation Proof Plan
- Next scope: `texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-consumer-validation-proof-plan`

Tracked status tokens:

- `privateCorpusRedactedManifestImporterContractAdapterMaterializationStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-complete-public-safe-adapter-dry-run-row-artifact-not-real-importer`
- `sourceAdapterDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-dry-run-complete-public-safe-adapter-row-consumption-not-real-importer`
- `sourceAdapterStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-complete-public-safe-adapter-rows-not-real-importer`
- `sourceProofCount=17`

Materialization evidence:

- `redactedManifestImporterContractAdapterMaterializationOnly=true`
- `adapterDryRunProofConsumed=true`
- `adapterDryRunProofContinuityValidated=true`
- `adapterMaterializationExecuted=true`
- `adapterMaterializationInputAccepted=true`
- `materializedAdapterArtifactWritten=true`
- `materializedAdapterArtifactStoredInTrackedProof=true`
- `materializedAdapterArtifactPathPublished=false`
- `materializedAdapterRowsGenerated=true`
- `materializedAdapterRowsValidated=true`
- `materializedAdapterAggregateCountsValidated=true`
- `materializationInterfacesValidated=true`
- `materializedAdapterEmitsOnlyPublicSafeRows=true`
- `adapterMaterializationInputMode=tracked-public-safe-adapter-dry-run-proof-json`
- `adapterMaterializationOutputMode=tracked-public-safe-materialized-adapter-artifact`
- `sourceAdapterContractInterfaceCount=7`
- `sourceAdapterDryRunInterfaceCount=8`
- `adapterMaterializationInterfaceCount=8`
- `materializedAdapterRows=5`
- `materializedAdapterArchiveClassRows=5`
- `materializedAdapterValidationRows=5`
- `materializedAdapterSummaryRows=1`
- `materializedAdapterArchiveTotalCount=301`
- `baseArchiveClassCount=1`
- `frontendArchiveClassCount=1`
- `loadingArchiveClassCount=1`
- `numericLevelArchiveClassCount=66`
- `goodieArchiveClassCount=232`
- `unknownAyaArchiveClassCount=0`
- `publicSafeMaterializedAdapterArtifactRows=1`
- `publicAllowedOutputCount=11`
- `redactedFieldCount=19`
- `falseGuardCount=56`
- `zeroCounterCount=47`
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
- `adapterMaterializationReadPrivateInputs=false`
- `adapterMaterializationPublishedPrivateInput=false`
- `privateMaterializationArtifactPublished=false`
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
- `rawDryRunTraceRows=0`
- `realImporterImplementationRows=0`
- `rebuildImplementationRows=0`

What this proves:

- The selected materialization can consume the tracked public-safe adapter dry-run proof rows.
- The materialized adapter artifact contains only public-safe archive class/count/status-token rows.
- The materialized adapter artifact preserves required archive class order and aggregate counts.
- Real importer implementation, real importer execution, private importer dry-run, and raw private manifest consumption remain unperformed.

What remains unproven:

- Private asset content parsing.
- Raw private manifest consumption.
- Real importer implementation or execution.
- Private importer dry run or real importer dry run.
- Adapter materialization consumer validation.
- Actual asset import or generated asset output.
- Runtime resource parser behavior, texture pixels, mesh loading/skinning, Direct3D/GPU behavior, material visual correctness, material/shader parity, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
