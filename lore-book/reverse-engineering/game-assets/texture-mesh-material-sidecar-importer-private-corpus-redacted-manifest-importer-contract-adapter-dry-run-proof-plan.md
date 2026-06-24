# Texture/Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Dry-Run Proof Plan

Slice: Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Dry-Run Proof Plan
Scope: `texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-dry-run-proof-plan`
Status: complete public-safe adapter dry run, not real importer proof
Date: 2026-06-15

This slice dry-runs consumption of the already tracked public-safe adapter rows. It consumes only the tracked adapter proof JSON and emits deterministic class/count/status-token dry-run rows.

Result artifact: [texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-dry-run-proof-plan.v1.json](texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-dry-run-proof-plan.v1.json)

Implementation: [`tools/texture_mesh_material_sidecar_importer_private_corpus_redacted_manifest_importer_contract_adapter_dry_run.py`](../../tools/texture_mesh_material_sidecar_importer_private_corpus_redacted_manifest_importer_contract_adapter_dry_run.py)

Continuity:

- Previous slice: Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Proof Plan
- Previous scope: `texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-proof-plan`
- Next slice: Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Materialization Proof Plan
- Next scope: `texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-proof-plan`

Tracked status tokens:

- `privateCorpusRedactedManifestImporterContractAdapterDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-dry-run-complete-public-safe-adapter-row-consumption-not-real-importer`
- `sourceAdapterStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-complete-public-safe-adapter-rows-not-real-importer`
- `sourceProofCount=16`

Dry-run evidence:

- `redactedManifestImporterContractAdapterDryRunOnly=true`
- `adapterProofConsumed=true`
- `adapterProofContinuityValidated=true`
- `adapterContractDryRunExecuted=true`
- `adapterDryRunInputAccepted=true`
- `adapterDryRunRowsGenerated=true`
- `adapterDryRunRowsValidated=true`
- `adapterDryRunAggregateCountsValidated=true`
- `adapterDryRunInterfacesValidated=true`
- `adapterDryRunEmitsOnlyPublicSafeRows=true`
- `adapterDryRunInputMode=tracked-public-safe-adapter-proof-json`
- `adapterDryRunOutputMode=public-safe-archive-class-count-status-token-dry-run-rows`
- `sourceAdapterContractInterfaceCount=7`
- `adapterDryRunInterfaceCount=8`
- `adapterDryRunRows=5`
- `adapterDryRunArchiveClassRows=5`
- `adapterDryRunValidationRows=5`
- `adapterDryRunSummaryRows=1`
- `adapterArchiveTotalCount=301`
- `baseArchiveClassCount=1`
- `frontendArchiveClassCount=1`
- `loadingArchiveClassCount=1`
- `numericLevelArchiveClassCount=66`
- `goodieArchiveClassCount=232`
- `unknownAyaArchiveClassCount=0`
- `publicAllowedOutputCount=10`
- `redactedFieldCount=18`
- `falseGuardCount=51`
- `zeroCounterCount=43`
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
- `adapterDryRunReadPrivateInputs=false`
- `adapterDryRunPublishedPrivateInput=false`
- `privateDryRunArtifactPublished=false`
- `rawDryRunTracePublished=false`
- `installedGameMutationAllowed=false`
- `originalExecutableMutationAllowed=false`
- `rawPathRows=0`
- `rawFilenameRows=0`
- `rawStemRows=0`
- `rawHashRows=0`
- `byteLengthRows=0`
- `rawTextureRefRows=0`
- `rawMeshRefRows=0`
- `privateManifestRows=0`
- `rawPrivateManifestRows=0`
- `rawManifestPathRows=0`
- `ignoredArtifactPathRows=0`
- `actualAssetImportRows=0`
- `generatedAssetRows=0`
- `outputArtifactRows=0`
- `privateArtifactRows=0`
- `privateDryRunRows=0`
- `realImporterDryRunRows=0`
- `rawDryRunTraceRows=0`
- `realImporterImplementationRows=0`
- `rebuildImplementationRows=0`

What this proves:

- The selected dry run can consume the tracked public-safe adapter proof rows.
- The dry run preserves required archive class order, aggregate counts, and private-data refusal guards.
- The dry run emits only public-safe class/count/status-token validation rows.
- Real importer implementation, real importer execution, private importer dry run, and raw private manifest consumption remain unperformed.

What remains unproven:

- Private asset content parsing.
- Raw private manifest consumption.
- Real importer implementation or execution.
- Private importer dry run or real importer dry run.
- Adapter materialization.
- Actual asset import or generated asset output.
- Runtime resource parser behavior, texture pixels, mesh loading/skinning, Direct3D/GPU behavior, material visual correctness, material/shader parity, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
