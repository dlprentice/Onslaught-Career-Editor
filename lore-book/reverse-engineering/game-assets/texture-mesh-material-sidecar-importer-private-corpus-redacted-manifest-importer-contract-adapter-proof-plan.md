# Texture/Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Proof Plan

Slice: Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Proof Plan
Scope: `texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-proof-plan`
Status: complete public-safe adapter rows, not real importer proof
Date: 2026-06-14

This slice adapts the already validated redacted private-corpus manifest shape into importer-contract adapter rows. It consumes only tracked public-safe proof JSON from the read-only manifest consumer-validation slice and the public contract skeleton slice.

Result artifact: [texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-proof-plan.v1.json](texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-proof-plan.v1.json)

Implementation: [`tools/texture_mesh_material_sidecar_importer_private_corpus_redacted_manifest_importer_contract_adapter.py`](../../tools/texture_mesh_material_sidecar_importer_private_corpus_redacted_manifest_importer_contract_adapter.py)

Continuity:

- Previous slice: Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Consumer Validation Proof Plan
- Previous scope: `texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-consumer-validation-proof-plan`
- Next slice: Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Dry-Run Proof Plan
- Next scope: `texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-dry-run-proof-plan`

Tracked status tokens:

- `privateCorpusRedactedManifestImporterContractAdapterStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-complete-public-safe-adapter-rows-not-real-importer`
- `sourceConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-consumer-validation-complete-redacted-manifest-consumed-no-content-read`
- `sourcePublicContractSkeletonStatus=texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-complete-public-contract-only-not-real-importer-proof`
- `sourceProofCount=15`

Adapter evidence:

- `redactedManifestImporterContractAdapterOnly=true`
- `redactedManifestImporterContractAdapterImplemented=true`
- `adapterContractValidationExecuted=true`
- `redactedManifestConsumerProofConsumed=true`
- `publicContractSkeletonProofConsumed=true`
- `adapterInputAccepted=true`
- `adapterRowsGenerated=true`
- `adapterRowsValidated=true`
- `adapterAggregateCountsValidated=true`
- `adapterContractInterfacesValidated=true`
- `adapterEmitsOnlyPublicSafeRows=true`
- `adapterInputMode=tracked-redacted-manifest-consumer-proof-plus-public-contract-skeleton`
- `adapterOutputMode=archive-class-count-status-token-contract-rows`
- `adapterContractInterfaceCount=7`
- `publicContractSkeletonInterfaceCount=6`
- `publicContractSkeletonFunctionCount=2`
- `publicContractSkeletonImplementationRows=1`
- `adapterRows=5`
- `adapterArchiveClassRows=5`
- `adapterValidationRows=5`
- `adapterValidationSummaryRows=1`
- `adapterArchiveTotalCount=301`
- `baseArchiveClassCount=1`
- `frontendArchiveClassCount=1`
- `loadingArchiveClassCount=1`
- `numericLevelArchiveClassCount=66`
- `goodieArchiveClassCount=232`
- `unknownAyaArchiveClassCount=0`
- `publicAllowedOutputCount=9`
- `redactedFieldCount=17`
- `falseGuardCount=45`
- `zeroCounterCount=37`
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
- `realImporterImplementationRows=0`
- `rebuildImplementationRows=0`

What this proves:

- The selected adapter can map redacted manifest class/count/status rows into public importer-contract adapter rows.
- The adapter output preserves required archive class order, aggregate counts, and private-data refusal guards.
- The adapter can link the redacted manifest consumer proof with the public contract skeleton proof.
- Real importer implementation, real importer execution, private asset parsing, and raw private manifest consumption remain unperformed.

What remains unproven:

- Private asset content parsing.
- Raw private manifest consumption.
- Real importer implementation or execution.
- Private importer dry run.
- Actual asset import or generated asset output.
- Runtime resource parser behavior, texture pixels, mesh loading/skinning, Direct3D/GPU behavior, material visual correctness, material/shader parity, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
