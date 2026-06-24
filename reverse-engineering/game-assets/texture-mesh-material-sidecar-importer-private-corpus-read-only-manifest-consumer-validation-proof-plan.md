# Texture/Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Consumer Validation Proof Plan

Status: complete redacted manifest consumer validation, not importer execution
Date: 2026-06-10
Slice: Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Consumer Validation Proof Plan
Scope: `texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-consumer-validation-proof-plan`

This slice validates the ignored/app-owned redacted manifest artifact produced by the prior materialization slice as a consumer input. The consumer accepts only archive class/count/status-token rows and does not publish the artifact path or any raw private identifiers.

Proof artifact: `texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-consumer-validation-proof-plan.v1.json`

Implementation/probe:

- `tools/texture_mesh_material_sidecar_importer_private_corpus_readonly_manifest_consumer_validation.py`
- `tools/texture_mesh_material_sidecar_importer_private_corpus_readonly_manifest_consumer_validation_proof_plan_probe.py`

Continuity:

- `previousSlice=Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Materialization Proof Plan`
- `previousScope=texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-materialization-proof-plan`
- `selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Proof Plan`
- `selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-proof-plan`
- `sourceMaterializationStatus=texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-materialization-complete-redacted-private-manifest-artifact-no-content-read`
- `sourceDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-dry-run-complete-redacted-class-manifest-shape-no-content-read`
- `sourceProofCount=13`

Consumer validation result:

- `privateCorpusReadOnlyManifestConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-consumer-validation-complete-redacted-manifest-consumed-no-content-read`
- `readOnlyManifestConsumerValidationOnly=true`
- `privateCorpusReadOnlyManifestConsumerValidationExecuted=true`
- `redactedPrivateManifestArtifactConsumed=true`
- `redactedPrivateManifestArtifactPathPublished=false`
- `ignoredArtifactPathPublished=false`
- `consumerInputAccepted=true`
- `consumerSchemaValidated=true`
- `consumerRowModeValidated=true`
- `consumerArchiveClassOrderValidated=true`
- `consumerArchiveClassCountsValidated=true`
- `consumerGuardCountersValidated=true`
- `privateEvidenceStoredOutsidePublicReleaseScope=true`

Validated redacted input:

- `sourceRootClass=user-owned-installed-or-copied-game-resource-root`
- `manifestKind=redacted-private-corpus-class-count-manifest`
- `manifestRowMode=class-count-status-token-only`
- `requiredArchiveClassCount=5`
- `consumerArchiveClassRowsValidated=5`
- `consumerValidationRows=5`
- `consumerValidationSummaryRows=1`
- `consumerArchiveTotalCount=301`
- `baseArchiveClassCount=1`
- `frontendArchiveClassCount=1`
- `loadingArchiveClassCount=1`
- `numericLevelArchiveClassCount=66`
- `goodieArchiveClassCount=232`
- `unknownAyaArchiveClassCount=0`

Redaction and guard counters:

- `publicAllowedOutputCount=10`
- `redactedFieldCount=16`
- `forbiddenManifestKeyCount=17`
- `falseGuardCount=43`
- `zeroCounterCount=38`
- `privateAssetContentRead=false`
- `privateArchiveBytesRead=false`
- `privateManifestMaterialized=false`
- `privateRawManifestMaterialized=false`
- `privateRawManifestRowsObserved=false`
- `privateManifestRowsPublished=false`
- `rawPrivateManifestConsumed=false`
- `rawPrivateManifestRowsConsumed=false`
- `realImporterImplementation=false`
- `realImporterExecuted=false`
- `importerContractAdapterImplemented=false`
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
- `importerContractAdapterRows=0`
- `rebuildImplementationRows=0`
- `publicLeakCheck=PASS`

Static context remains unchanged: `6411/6411 = 100.00%`, `0 / 0 / 0`, `1560/1560 = 100.00%`, and `1179/1179 = 100.00%`.

What this proves:

- The selected consumer-validation lane can parse and validate the redacted manifest artifact shape.
- The consumer input contains only archive class/count/status-token rows.
- The consumer input preserves required archive class order, counts, and guard counters.
- Raw private manifest consumption, real importer implementation, and real importer execution remain unperformed.

What remains unproven:

- Private asset content parsing.
- Private raw corpus manifest materialization.
- Private raw manifest row observation.
- Raw private manifest consumption.
- Real importer implementation.
- Real importer execution.
- Importer contract adapter implementation.
- Runtime resource archive parser behavior.
- Runtime texture parser behavior or texture pixels.
- Runtime mesh loading or skinning.
- Direct3D upload or GPU behavior.
- Native textured 3D rendering.
- Material visual correctness or material/shader parity.
- Asset format completeness or exact mesh/texture layouts.
- Product UI behavior.
- Godot parity.
- Rebuild implementation, rebuild parity, or no-noticeable-difference parity.
