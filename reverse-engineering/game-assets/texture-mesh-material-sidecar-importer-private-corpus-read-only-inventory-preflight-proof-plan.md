# Texture/Mesh Material Sidecar Importer Private Corpus Read-Only Inventory Preflight Proof Plan

Status: complete redacted read-only inventory preflight
Date: 2026-06-10
Scope: `texture-mesh-material-sidecar-importer-private-corpus-read-only-inventory-preflight-proof-plan`

Canonical display name: Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Inventory Preflight Proof Plan.

This slice follows the completed [Texture/Mesh Material Sidecar Importer Private Corpus Safety Packet Checklist Population Proof Plan](texture-mesh-material-sidecar-importer-private-corpus-safety-packet-checklist-population-proof-plan.md). It performs a bounded read-only inventory preflight against a user-owned installed or copied game resource root and publishes only class/count/status-token output. It does not publish raw private paths, raw filenames, raw stems, raw texture references, raw mesh references, hashes, byte lengths, directory listings, or importer output. It does not mutate the installed game, mutate the original executable, read asset content bytes, materialize a private manifest, execute a real importer, emit imported assets, launch BEA, mutate Ghidra, patch executables, use Godot, wire product UI, implement a renderer, or claim rebuild/no-noticeable-difference parity.

Preflight module: `tools/texture_mesh_material_sidecar_importer_private_corpus_readonly_inventory_preflight.py`.

Machine-checkable schema: [texture-mesh-material-sidecar-importer-private-corpus-read-only-inventory-preflight-proof-plan.v1.json](texture-mesh-material-sidecar-importer-private-corpus-read-only-inventory-preflight-proof-plan.v1.json).

## Result

- `privateCorpusReadOnlyInventoryPreflightStatus=texture-mesh-material-sidecar-importer-private-corpus-read-only-inventory-preflight-complete-redacted-class-count-summary-no-content-read`
- `previousSlice=Texture / Mesh Material Sidecar Importer Private Corpus Safety Packet Checklist Population Proof Plan`
- `previousScope=texture-mesh-material-sidecar-importer-private-corpus-safety-packet-checklist-population-proof-plan`
- `selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Dry-Run Proof Plan`
- `selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-dry-run-proof-plan`
- `sourceChecklistPopulationStatus=texture-mesh-material-sidecar-importer-private-corpus-safety-packet-checklist-population-complete-public-safe-checklist-populated-no-private-corpus-read`
- `sourceProofCount=10`
- `readOnlyInventoryPreflightOnly=true`
- `privateCorpusReadOnlyInventoryPreflightExecuted=true`
- `privateCorpusRootExistenceChecked=true`
- `privateResourceArchiveDirectoryExistenceChecked=true`
- `privateResourceArchiveClassEnumerationPerformed=true`
- `privateCorpusReadOnlyInventoryGenerated=true`
- `privateEvidenceStoredOutsidePublicReleaseScope=true`
- `privateAssetContentRead=false`
- `privateArchiveBytesRead=false`
- `privateManifestMaterialized=false`
- `privateManifestRowsObserved=false`
- `realImporterImplementation=false`
- `realImporterExecuted=false`
- `installedGameMutationAllowed=false`
- `originalExecutableMutationAllowed=false`
- `publicPrivateSeparationRequired=true`
- `sourceRootClass=user-owned-installed-or-copied-game-resource-root`
- `resourceRootExists=true`
- `resourceDirectoryExists=true`
- `requiredArchiveClassCount=5`
- `observedRequiredArchiveClassCount=5`
- `allRequiredArchiveClassesObserved=true`
- `ayaArchiveTotalCount=301`
- `baseArchiveClassCount=1`
- `frontendArchiveClassCount=1`
- `loadingArchiveClassCount=1`
- `numericLevelArchiveClassCount=66`
- `goodieArchiveClassCount=232`
- `unknownAyaArchiveClassCount=0`
- `publicAllowedOutputCount=6`
- `redactedFieldCount=12`
- `falseGuardCount=38`
- `zeroCounterCount=32`
- `publicLeakCheck=PASS`

Static context remains `6411/6411 = 100.00%`, `0 / 0 / 0`, `1560/1560 = 100.00%`, `1179/1179 = 100.00%`, and `remainingActiveFocusedWork=0`.

## Archive Class Summary

The preflight publishes only redacted archive classes and counts:

| Archive class | Count |
| --- | ---: |
| `base-resource-archive` | `1` |
| `frontend-resource-archive` | `1` |
| `loading-resource-archive` | `1` |
| `numeric-level-resource-archive` | `66` |
| `goodie-resource-archive` | `232` |
| `unknown-aya-resource-archive` | `0` |

The required class coverage is `observedRequiredArchiveClassCount=5` of `requiredArchiveClassCount=5`; `allRequiredArchiveClassesObserved=true`.

## Redaction Policy

Allowed public outputs are `resource-root-existence-status`, `resource-directory-existence-status`, `archive-class-counts`, `required-class-coverage-status`, `redaction-field-counts`, and `claim-boundary`.

Redacted fields are private corpus roots, concrete archive paths, concrete resource directory paths, raw resource filenames, raw resource stems, raw texture references, raw mesh references, private digests, private byte lengths, operator profile identifiers, raw directory listings, and raw importer stdout/stderr.

## Boundary Token

readOnlyInventoryPreflightOnly=true; privateCorpusReadOnlyInventoryPreflightExecuted=true; privateCorpusRootExistenceChecked=true; privateResourceArchiveDirectoryExistenceChecked=true; privateResourceArchiveClassEnumerationPerformed=true; privateCorpusReadOnlyInventoryGenerated=true; privateEvidenceStoredOutsidePublicReleaseScope=true; privateAssetContentRead=false; privateArchiveBytesRead=false; privateManifestMaterialized=false; privateManifestRowsObserved=false; realImporterImplementation=false; realImporterExecuted=false; privateImporterDryRunExecuted=false; installedGameMutationAllowed=false; originalExecutableMutationAllowed=false; importerImplementation=false; importerExecuted=false; actualAssetImport=false; generatedAssetOutputs=false; privateAssetPublication=false; runtimeExecution=false; beLaunch=false; newLaunch=false; screenshotCapture=false; nativeInput=false; debuggerAttachment=false; godotWork=false; ghidraMutation=false; executablePatching=false; productUiWired=false; rendererImplementation=false; rebuildImplementation=false; runtimeResourceArchiveParserProven=false; runtimeTextureParserBehaviorProven=false; runtimeTexturePixelsProven=false; runtimeMeshLoadingProven=false; runtimeMeshSkinningProven=false; runtimeDirect3DUploadProven=false; runtimeGpuBehaviorProven=false; nativeTextured3DRenderingProven=false; materialVisualCorrectnessProven=false; materialShaderParityProven=false; visualQaComplete=false; assetFormatCompletenessProven=false; exactMeshTextureLayoutsProven=false; rebuildParityProven=false; noNoticeableDifferenceParityProven=false; publicPrivateProofLeak=false; rawPathRows=0; rawFilenameRows=0; rawStemRows=0; rawHashRows=0; privateHashRows=0; byteLengthRows=0; rawTextureRefRows=0; rawMeshRefRows=0; privateManifestRows=0; actualAssetImportRows=0; generatedAssetRows=0; outputArtifactRows=0; privateArtifactRows=0; publishedPrivatePathRows=0; publishedRawRefRows=0; privatePathLeakCount=0; rawArtifactLeakCount=0; privateAssetLeakCount=0; publicPrivateProofLeakCount=0; runtimeObservationRows=0; runtimeTexturePixelRows=0; runtimeMeshRenderRows=0; runtimeMaterialRows=0; screenshotRows=0; captureRows=0; ghidraMutationRows=0; executablePatchRows=0; productUiRows=0; godotRows=0; realImporterImplementationRows=0; rebuildImplementationRows=0; mutationRows=0.

## What This Proves

- A selected read-only inventory preflight can inspect a user-owned installed or copied resource root without mutating it.
- The preflight observed all required resource archive classes using redacted class/count/status-token output only.
- The public proof contains no raw private paths, filenames, hashes, byte lengths, texture references, mesh references, or directory listings.
- Real importer implementation and execution remain unperformed in this slice.

## What Remains Separate Proof

This is a redacted read-only inventory preflight only. It does not prove private asset content parsing, private corpus manifest materialization, real importer implementation, real importer execution, runtime resource archive parser behavior, runtime texture parser behavior, runtime texture pixels, JPEG/inflate decode fidelity, runtime mesh loading or skinning, Direct3D upload or GPU behavior, native textured 3D rendering, material visual correctness, material/shader parity, asset format completeness, exact mesh or texture layouts, product UI behavior, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
